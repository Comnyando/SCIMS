"""
Admin Commons router for moderation workflows.
"""

from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.commons_submission import CommonsSubmission
from app.models.commons_moderation_action import CommonsModerationAction
from app.models.commons_entity import CommonsEntity
from app.models.tag import Tag
from app.models.commons_entity_tag import CommonsEntityTag
from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.core.commons_dependencies import require_moderator
from app.schemas.commons import (
    CommonsSubmissionResponse,
    CommonsSubmissionsListResponse,
    CommonsModerationActionCreate,
    CommonsModerationActionResponse,
)
from app.config import settings
from app.utils.commons_cache import invalidate_public_cache

router = APIRouter(prefix=f"{settings.api_v1_prefix}/admin/commons", tags=["admin", "commons"])


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


@router.get("/submissions", response_model=CommonsSubmissionsListResponse)
async def list_submissions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    entity_type_filter: Optional[str] = Query(None, description="Filter by entity type"),
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """
    List submissions for moderation.

    Moderators can view all submissions and filter by status/type.
    """
    query = db.query(CommonsSubmission)

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


@router.get("/submissions/{submission_id}", response_model=CommonsSubmissionResponse)
async def get_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """Get a specific submission for moderation."""
    submission = db.query(CommonsSubmission).filter(CommonsSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    return build_submission_response(submission)


@router.post("/submissions/{submission_id}/approve", response_model=CommonsSubmissionResponse)
async def approve_submission(
    submission_id: str,
    action_data: CommonsModerationActionCreate,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """
    Approve a submission and publish it to the commons.

    Creates a commons entity and logs the moderation action.
    """
    submission = db.query(CommonsSubmission).filter(CommonsSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    if submission.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve submission with status '{submission.status}'",
        )

    # Create moderation action
    moderation_action = CommonsModerationAction(
        submission_id=submission.id,
        moderator_id=moderator.id,
        action="approve",
        action_payload=action_data.action_payload,
        notes=action_data.notes,
    )
    db.add(moderation_action)

    # Create commons entity
    commons_entity = CommonsEntity(
        entity_type=submission.entity_type,
        canonical_id=None,  # Can be set later if linking to actual items/blueprints
        data=submission.entity_payload,
        version=1,
        is_public=True,
        created_by=submission.submitter_id,
    )
    db.add(commons_entity)
    db.flush()  # Get the entity ID

    # Update submission status
    submission.status = "approved"
    submission.review_notes = action_data.notes

    db.commit()
    db.refresh(submission)
    db.refresh(commons_entity)

    # Invalidate cache for this entity type (and tags, since tags might change)
    invalidate_public_cache(entity_type=submission.entity_type)

    return build_submission_response(submission)


@router.post("/submissions/{submission_id}/reject", response_model=CommonsSubmissionResponse)
async def reject_submission(
    submission_id: str,
    action_data: CommonsModerationActionCreate,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """Reject a submission."""
    submission = db.query(CommonsSubmission).filter(CommonsSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    if submission.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject submission with status '{submission.status}'",
        )

    # Create moderation action
    moderation_action = CommonsModerationAction(
        submission_id=submission.id,
        moderator_id=moderator.id,
        action="reject",
        action_payload=action_data.action_payload,
        notes=action_data.notes,
    )
    db.add(moderation_action)

    # Update submission status
    submission.status = "rejected"
    submission.review_notes = action_data.notes

    db.commit()
    db.refresh(submission)

    return build_submission_response(submission)


@router.post(
    "/submissions/{submission_id}/request-changes", response_model=CommonsSubmissionResponse
)
async def request_changes_submission(
    submission_id: str,
    action_data: CommonsModerationActionCreate,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """Request changes on a submission (returns to pending for user to update)."""
    submission = db.query(CommonsSubmission).filter(CommonsSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    if submission.status not in ("pending", "needs_changes"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot request changes on submission with status '{submission.status}'",
        )

    # Create moderation action
    moderation_action = CommonsModerationAction(
        submission_id=submission.id,
        moderator_id=moderator.id,
        action="request_changes",
        action_payload=action_data.action_payload,
        notes=action_data.notes,
    )
    db.add(moderation_action)

    # Update submission status
    submission.status = "needs_changes"
    submission.review_notes = action_data.notes

    db.commit()
    db.refresh(submission)

    return build_submission_response(submission)


@router.post("/submissions/{submission_id}/merge", response_model=CommonsSubmissionResponse)
async def merge_submission(
    submission_id: str,
    action_data: CommonsModerationActionCreate,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """
    Merge a submission into an existing commons entity.

    Requires action_payload with 'target_entity_id' for the entity to merge into.
    """
    submission = db.query(CommonsSubmission).filter(CommonsSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    if submission.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot merge submission with status '{submission.status}'",
        )

    # Validate action_payload contains target_entity_id
    if not action_data.action_payload or "target_entity_id" not in action_data.action_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="action_payload must contain 'target_entity_id' for merge operation",
        )

    target_entity_id = action_data.action_payload["target_entity_id"]
    target_entity = db.query(CommonsEntity).filter(CommonsEntity.id == target_entity_id).first()

    if not target_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target entity not found",
        )

    # Create moderation action
    moderation_action = CommonsModerationAction(
        submission_id=submission.id,
        moderator_id=moderator.id,
        action="merge",
        action_payload=action_data.action_payload,
        notes=action_data.notes,
    )
    db.add(moderation_action)

    # Update submission status
    submission.status = "merged"
    submission.review_notes = action_data.notes

    db.commit()
    db.refresh(submission)

    return build_submission_response(submission)
