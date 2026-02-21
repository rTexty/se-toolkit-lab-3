"""Router for outcome endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.db.outcomes import create_outcome, read_outcome, read_outcomes
from app.models.outcome import Outcome, OutcomeCreate

router = APIRouter()


@router.get("/", response_model=list[Outcome])
async def get_outcomes(session: AsyncSession = Depends(get_session)):
    """Get all outcomes."""
    return await read_outcomes(session)


@router.get("/{outcome_id}", response_model=Outcome)
async def get_outcome(outcome_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific outcome by its id."""
    outcome = await read_outcome(session, outcome_id)
    if outcome is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Outcome not found"
        )
    return outcome


@router.post("/", response_model=Outcome, status_code=201)
async def post_outcome(body: OutcomeCreate, session: AsyncSession = Depends(get_session)):
    """Create a new outcome."""
    try:
        return await create_outcome(
            session,
            learner_id=body.learner_id,
            item_id=body.item_id,
            status=body.status,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="learner_id or item_id does not reference an existing record",
        )
