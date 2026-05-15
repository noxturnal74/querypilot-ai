from datetime import datetime

from pydantic import BaseModel, Field


class SuggestionOut(BaseModel):
    category: str
    severity: str
    message: str
    rationale: str


class RiskOut(BaseModel):
    level: str
    code: str
    message: str


class IndexRecommendationOut(BaseModel):
    table_name: str
    columns: list[str]
    statement: str
    confidence: float
    reason: str


class AnalysisCreate(BaseModel):
    query: str = Field(min_length=1, max_length=20000)
    title: str | None = Field(default=None, max_length=180)
    dialect: str = Field(default="postgresql", max_length=40)
    schema_context_id: int | None = None
    schema_text: str | None = Field(default=None, max_length=50000)


class AnalysisOut(BaseModel):
    id: int
    title: str
    query: str
    dialect: str
    status: str
    risk_level: str
    score: float
    summary: str
    plan_notes: str
    ai_summary: str
    created_at: datetime
    suggestions: list[SuggestionOut]
    risks: list[RiskOut]
    indexes: list[IndexRecommendationOut]

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    id: int
    title: str
    dialect: str
    risk_level: str
    score: float
    summary: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SchemaContextCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    ddl: str = Field(min_length=1, max_length=50000)


class SchemaContextOut(BaseModel):
    id: int
    name: str
    description: str | None
    ddl: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    app: str
