from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.schemas import (
    AnalysisCreate,
    AnalysisListItem,
    AnalysisOut,
    HealthOut,
    SchemaContextCreate,
    SchemaContextOut,
)
from app.core.config import get_settings
from app.db.models import Analysis, IndexRecommendation, Risk, SchemaContext, Suggestion
from app.db.session import get_db
from app.services.ai.base import AIAnalysisContext
from app.services.ai.factory import get_ai_adapter
from app.services.sql_analyzer import SQLAnalyzer

router = APIRouter()


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", app=get_settings().app_name)


@router.post("/schemas", response_model=SchemaContextOut, status_code=201)
def create_schema(payload: SchemaContextCreate, db: Session = Depends(get_db)) -> SchemaContext:
    schema = SchemaContext(name=payload.name, description=payload.description, ddl=payload.ddl)
    db.add(schema)
    db.commit()
    db.refresh(schema)
    return schema


@router.get("/schemas", response_model=list[SchemaContextOut])
def list_schemas(db: Session = Depends(get_db)) -> list[SchemaContext]:
    return list(db.query(SchemaContext).order_by(desc(SchemaContext.created_at)).all())


@router.post("/analyze", response_model=AnalysisOut, status_code=201)
async def analyze(payload: AnalysisCreate, db: Session = Depends(get_db)) -> AnalysisOut:
    schema = None
    schema_text = payload.schema_text
    if payload.schema_context_id:
        schema = db.get(SchemaContext, payload.schema_context_id)
        if not schema:
            raise HTTPException(status_code=404, detail="Schema context not found")
        schema_text = schema.ddl

    deterministic = SQLAnalyzer().analyze(payload.query, schema_text)
    ai_summary = await get_ai_adapter().summarize(
        AIAnalysisContext(
            query=payload.query,
            dialect=payload.dialect,
            schema_text=schema_text,
            deterministic_summary=deterministic.summary,
        )
    )
    analysis = Analysis(
        title=payload.title or _title_from_query(payload.query),
        query=payload.query,
        dialect=payload.dialect,
        risk_level=deterministic.risk_level,
        score=deterministic.score,
        summary=deterministic.summary,
        plan_notes=deterministic.plan_notes,
        ai_summary=ai_summary,
        schema_context=schema,
    )
    analysis.suggestions = [Suggestion(**item.__dict__) for item in deterministic.suggestions]
    analysis.risks = [Risk(**item.__dict__) for item in deterministic.risks]
    analysis.indexes = [
        IndexRecommendation(
            table_name=item.table_name,
            columns=",".join(item.columns),
            statement=item.statement,
            confidence=item.confidence,
            reason=item.reason,
        )
        for item in deterministic.indexes
    ]
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return _analysis_out(analysis)


@router.get("/analyses", response_model=list[AnalysisListItem])
def list_analyses(
    db: Session = Depends(get_db), limit: int = Query(default=20, ge=1, le=100)
) -> list[Analysis]:
    return list(db.query(Analysis).order_by(desc(Analysis.created_at)).limit(limit).all())


@router.get("/analyses/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)) -> AnalysisOut:
    analysis = db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _analysis_out(analysis)


def _title_from_query(query: str) -> str:
    compact = " ".join(query.split())
    return compact[:90] if compact else "Untitled analysis"


def _analysis_out(analysis: Analysis) -> AnalysisOut:
    return AnalysisOut(
        id=analysis.id,
        title=analysis.title,
        query=analysis.query,
        dialect=analysis.dialect,
        status=analysis.status,
        risk_level=analysis.risk_level,
        score=analysis.score,
        summary=analysis.summary,
        plan_notes=analysis.plan_notes,
        ai_summary=analysis.ai_summary,
        created_at=analysis.created_at,
        suggestions=[
            {
                "category": suggestion.category,
                "severity": suggestion.severity,
                "message": suggestion.message,
                "rationale": suggestion.rationale,
            }
            for suggestion in analysis.suggestions
        ],
        risks=[{"level": risk.level, "code": risk.code, "message": risk.message} for risk in analysis.risks],
        indexes=[
            {
                "table_name": index.table_name,
                "columns": [column for column in index.columns.split(",") if column],
                "statement": index.statement,
                "confidence": index.confidence,
                "reason": index.reason,
            }
            for index in analysis.indexes
        ],
    )
