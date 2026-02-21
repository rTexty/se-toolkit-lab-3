"""Database operations for outcomes."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.outcome import OutcomeRecord


async def read_outcomes(session: AsyncSession) -> list[OutcomeRecord]:
    """Read all outcomes from the database."""
    result = await session.exec(select(OutcomeRecord))
    return list(result.all())


async def read_outcome(session: AsyncSession, outcome_id: int) -> OutcomeRecord | None:
    """Read a single outcome by id."""
    return await session.get(OutcomeRecord, outcome_id)


async def create_outcome(
    session: AsyncSession,
    learner_id: int,
    item_id: int,
    status: str,
) -> OutcomeRecord:
    """Create a new outcome in the database."""
    outcome = OutcomeRecord(
        learner_id=learner_id, item_id=item_id, status=status
    )
    session.add(outcome)
    await session.commit()
    await session.refresh(outcome)
    return outcome
