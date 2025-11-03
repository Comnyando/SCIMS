"""
Commons router for submission and moderation workflows.
"""

from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.commons_submission import CommonsSubmission
from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.schemas.commons import (
    CommonsSubmissionCreate,
    CommonsSubmissionUpdate,
    CommonsSubmissionResponse,
    CommonsSubmissionsListResponse,
)
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/commons", tags=["commons"])


def build_submission_response(submission: CommonsSubmission) -> dict:
    """Build a submission response dictionary."""
    return {
        "id": str(submission.id),
        "submitter_id": submission.submitter_id,
        "entity_type": submission.entity_type,
        "entity_payload": submission.entity_payload,
        "source_reference": submission.source_reference,
        "status": submission.status,
        "review_notes": submission.review_notes,
        "created_at": submission.created_at,
        "updated_at": submission.updated_at,
    }


@router.post(
    "/submit", response_model=CommonsSubmissionResponse, status_code=status.HTTP_201_CREATED
)
async def create_submission(
    submission_data: CommonsSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Submit a new entity to the public commons.

    Submissions go through a moderation workflow before being published.
    """
    submission = CommonsSubmission(
        submitter_id=current_user.id,
        entity_type=submission_data.entity_type,
        entity_payload=submission_data.entity_payload,
        source_reference=submission_data.source_reference,
        status="pending",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return build_submission_response(submission)


@router.get("/my-submissions", response_model=CommonsSubmissionsListResponse)
async def get_my_submissions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    entity_type_filter: Optional[str] = Query(None, description="Filter by entity type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's submissions to the commons.

    Returns a paginated list of submissions made by the authenticated user.
    """
    query = db.query(CommonsSubmission).filter(CommonsSubmission.submitter_id == current_user.id)

    if status_filter:
        query = query.filter(CommonsSubmission.status == status_filter)
    if entity_type_filter:
        query = query.filter(CommonsSubmission.entity_type == entity_type_filter)

    total = query.count()
    submissions = query.order_by(desc(CommonsSubmission.created_at)).offset(skip).limit(limit).all()

    submission_responses = [build_submission_response(sub) for sub in submissions]

    return {
        "submissions": submission_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }


@router.patch("/submissions/{submission_id}", response_model=CommonsSubmissionResponse)
async def update_submission(
    submission_id: str,
    submission_data: CommonsSubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a submission (only allowed for pending submissions).

    Users can only update their own pending submissions.
    """
    submission = db.query(CommonsSubmission).filter(CommonsSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    if submission.submitter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own submissions",
        )

    if submission.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update submission with status '{submission.status}'. Only pending submissions can be updated.",
        )

    if submission_data.entity_payload is not None:
        submission.entity_payload = submission_data.entity_payload
    if submission_data.source_reference is not None:
        submission.source_reference = submission_data.source_reference

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return build_submission_response(submission)
