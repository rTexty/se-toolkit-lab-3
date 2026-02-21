"""Models for learning outcomes."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class OutcomeRecord(SQLModel, table=True):
    """A row in the outcomes table."""

    __tablename__ = "outcomes"

    id: int | None = Field(default=None, primary_key=True)
    learner_id: int = Field(foreign_key="learners.id")
    item_id: int = Field(foreign_key="items.id")
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


class OutcomeCreate(SQLModel):
    """Schema for creating an outcome."""

    learner_id: int
    item_id: int
    status: str


class Outcome(SQLModel):
    """Response schema for an outcome."""

    id: int
    learner_id: int
    item_id: int
    status: str
    created_at: datetime
