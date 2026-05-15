from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SchemaContext(Base):
    __tablename__ = "schema_contexts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ddl: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    analyses: Mapped[list["Analysis"]] = relationship(back_populates="schema_context")


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False, default="Untitled analysis")
    dialect: Mapped[str] = mapped_column(String(40), nullable=False, default="postgresql")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="completed")
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    plan_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ai_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    schema_context_id: Mapped[int | None] = mapped_column(ForeignKey("schema_contexts.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    schema_context: Mapped[SchemaContext | None] = relationship(back_populates="analyses")
    suggestions: Mapped[list["Suggestion"]] = relationship(cascade="all, delete-orphan", back_populates="analysis")
    risks: Mapped[list["Risk"]] = relationship(cascade="all, delete-orphan", back_populates="analysis")
    indexes: Mapped[list["IndexRecommendation"]] = relationship(cascade="all, delete-orphan", back_populates="analysis")


class Suggestion(Base):
    __tablename__ = "suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    analysis: Mapped[Analysis] = relationship(back_populates="suggestions")


class Risk(Base):
    __tablename__ = "risks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    analysis: Mapped[Analysis] = relationship(back_populates="risks")


class IndexRecommendation(Base):
    __tablename__ = "index_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), index=True)
    table_name: Mapped[str] = mapped_column(String(160), nullable=False)
    columns: Mapped[str] = mapped_column(String(300), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.75)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    analysis: Mapped[Analysis] = relationship(back_populates="indexes")
