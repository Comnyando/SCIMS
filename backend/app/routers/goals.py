"""
Goals router for managing goals and tracking progress.

This router provides endpoints for:
- Creating and managing goals
- Calculating goal progress
- Detecting goal completion
- Tracking goal status
"""

from typing import Optional
from math import ceil
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func as sql_func, false, literal

from app.database import get_db
from app.models.goal import Goal, GOAL_STATUS_ACTIVE, GOAL_STATUS_COMPLETED, GOAL_STATUS_CANCELLED
from app.models.goal_item import GoalItem
from app.models.item import Item
from app.models.item_stock import ItemStock
from app.models.location import Location
from app.models.organization_member import OrganizationMember
from app.models.ship import Ship
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalProgress,
    GoalProgressResponse,
    GoalItemCreate,
    GoalItemProgress,
    GoalItemResponse,
)
from app.routers.inventory import check_location_access_for_inventory
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/goals", tags=["goals"])


def build_goal_response(goal: Goal) -> dict:
    """
    Build a goal response dictionary including goal_items.

    This helper ensures consistent response structure across all endpoints.
    """
    # Eager load goal_items if not already loaded
    if goal.goal_items is None:
        goal.goal_items = []

    # Build goal_items response
    goal_items_response = []
    for goal_item in goal.goal_items:
        goal_item_dict = {
            "id": str(goal_item.id),
            "item_id": goal_item.item_id,
            "target_quantity": float(goal_item.target_quantity),
            "item": (
                {
                    "id": goal_item.item.id,
                    "name": goal_item.item.name,
                    "description": goal_item.item.description,
                    "category": goal_item.item.category,
                }
                if goal_item.item
                else None
            ),
        }
        goal_items_response.append(goal_item_dict)

    # Build main goal response
    response_dict = {
        "id": str(goal.id),
        "name": goal.name,
        "description": goal.description,
        "organization_id": goal.organization_id,
        "created_by": goal.created_by,
        "goal_items": goal_items_response,
        "target_date": goal.target_date,
        "status": goal.status,
        "created_at": goal.created_at,
        "updated_at": goal.updated_at,
        "progress_data": goal.progress_data if goal.progress_data is not None else {},
        "organization": None,
        "creator": None,
    }

    return response_dict


def get_accessible_location_ids(
    current_user: User, db: Session, organization_id: Optional[str] = None
) -> list[str]:
    """
    Get list of location IDs accessible to the current user.

    If organization_id is provided, only returns locations for that organization.
    Otherwise returns all locations accessible to the user (user-owned, org-owned, ship-owned).
    """
    query = db.query(Location)

    # Canonical locations are always accessible (public read)
    canonical_locations = Location.is_canonical == True

    # User-owned locations
    user_owned = Location.owner_type == "user"
    user_owned = user_owned & (Location.owner_id == current_user.id)

    # Organization-owned locations
    org_memberships = (
        db.query(OrganizationMember.organization_id)
        .filter(OrganizationMember.user_id == current_user.id)
        .distinct()
        .all()
    )
    org_ids = [str(m[0]) for m in org_memberships]

    # Filter by specific organization if provided
    if organization_id:
        if organization_id not in org_ids and organization_id != current_user.id:
            # User doesn't have access to this organization
            return []
        org_ids = [organization_id]

    org_owned = Location.owner_type == "organization"
    if org_ids:
        org_owned = org_owned & Location.owner_id.in_(org_ids)
    else:
        org_owned = literal(False)  # type: ignore[assignment]

    # Ship-owned locations
    ship_locations = Location.owner_type == "ship"
    user_ships_query = db.query(Ship.cargo_location_id).filter(
        Ship.owner_type == "user", Ship.owner_id == current_user.id
    )
    user_ship_ids = [str(row[0]) for row in user_ships_query.all() if row[0]]

    org_ship_ids = []
    if org_ids:
        org_ships_query = db.query(Ship.cargo_location_id).filter(
            Ship.owner_type == "organization", Ship.owner_id.in_(org_ids)
        )
        org_ship_ids = [str(row[0]) for row in org_ships_query.all() if row[0]]

    accessible_ship_ids = user_ship_ids + org_ship_ids

    if accessible_ship_ids:
        ship_owned = ship_locations & Location.id.in_(accessible_ship_ids)
    else:
        ship_owned = literal(False)  # type: ignore[assignment]

    # Combine filters
    query = query.filter(or_(canonical_locations, user_owned, org_owned, ship_owned))

    # Filter in-memory for fine-grained access control
    accessible_locations = []
    for location in query.all():
        if check_location_access_for_inventory(location, current_user, db, "viewer"):
            accessible_locations.append(location.id)

    return accessible_locations


def calculate_item_quantity(
    item_id: str,
    current_user: User,
    db: Session,
    organization_id: Optional[str] = None,
) -> Decimal:
    """
    Calculate total available quantity of an item across all accessible locations.

    Returns the sum of (quantity - reserved_quantity) for the item across all
    locations accessible to the user (or organization if specified).
    """
    accessible_location_ids = get_accessible_location_ids(current_user, db, organization_id)

    if not accessible_location_ids:
        return Decimal("0")

    # Sum available quantities (quantity - reserved_quantity) across accessible locations
    total = (
        db.query(
            sql_func.coalesce(
                sql_func.sum(ItemStock.quantity - ItemStock.reserved_quantity), Decimal("0")
            )
        )
        .filter(
            ItemStock.item_id == item_id,
            ItemStock.location_id.in_(accessible_location_ids),
        )
        .scalar()
    )

    return Decimal(str(total)) if total is not None else Decimal("0")


def calculate_goal_progress(goal: Goal, current_user: User, db: Session) -> GoalProgress:
    """
    Calculate progress for a goal with multiple items.

    Calculates progress for each item and aggregates overall progress.
    Returns progress information including percentage and completion status.
    """
    item_progress_list: list[GoalItemProgress] = []
    total_current = Decimal("0")
    total_target = Decimal("0")

    # Calculate progress for each goal item
    for goal_item in goal.goal_items:
        current_qty = calculate_item_quantity(
            goal_item.item_id,
            current_user,
            db,
            goal.organization_id,
        )
        target_qty = goal_item.target_quantity

        total_current += current_qty
        total_target += target_qty

        # Calculate per-item progress
        item_progress_pct = float((current_qty / target_qty) * 100) if target_qty > 0 else 0.0
        item_progress_pct = min(100.0, max(0.0, item_progress_pct))
        item_completed = current_qty >= target_qty

        item_progress_list.append(
            GoalItemProgress(
                item_id=goal_item.item_id,
                current_quantity=current_qty,
                target_quantity=target_qty,
                progress_percentage=item_progress_pct,
                is_completed=item_completed,
            )
        )

    # Calculate overall progress percentage
    overall_progress_pct = float((total_current / total_target) * 100) if total_target > 0 else 0.0
    overall_progress_pct = min(100.0, max(0.0, overall_progress_pct))

    # Goal is completed when ALL items are at or above their targets
    all_completed = (
        all(item.is_completed for item in item_progress_list) if item_progress_list else False
    )

    # Calculate days remaining if target_date is set
    days_remaining = None
    if goal.target_date:
        now = datetime.now(timezone.utc)
        if goal.target_date.tzinfo is None:
            target = goal.target_date.replace(tzinfo=timezone.utc)
        else:
            target = goal.target_date
        delta = target - now
        days_remaining = max(0, delta.days) if delta.days > 0 else None

    return GoalProgress(
        current_quantity=total_current,
        target_quantity=total_target,
        progress_percentage=overall_progress_pct,
        is_completed=all_completed,
        days_remaining=days_remaining,
        item_progress=item_progress_list,
    )


def check_goal_completion(goal: Goal, progress: GoalProgress, db: Session) -> bool:
    """
    Check if goal should be marked as completed and update status if needed.

    Returns True if status was changed to completed.
    """
    if goal.status == GOAL_STATUS_ACTIVE and progress.is_completed:
        goal.status = GOAL_STATUS_COMPLETED
        # Update progress_data with completion info
        if goal.progress_data is None:
            goal.progress_data = {}
        goal.progress_data.update(
            {
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "current_quantity": float(progress.current_quantity),
                "progress_percentage": progress.progress_percentage,
            }
        )
        db.commit()
        return True
    return False


def validate_goal_access(goal: Goal, current_user: User, db: Session) -> None:
    """
    Validate that the current user has access to the goal.

    User can access goal if:
    - They created it (created_by == current_user.id)
    - They are a member of the organization (if organization_id is set)
    """
    if goal.created_by == current_user.id:
        return

    # If goal belongs to organization, check membership
    if goal.organization_id:
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == goal.organization_id,
                OrganizationMember.user_id == current_user.id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this goal",
            )
    else:
        # Goal doesn't belong to organization and user didn't create it
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this goal",
        )


@router.get("", response_model=dict)
async def list_goals(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    organization_id: Optional[str] = Query(None, description="Filter by organization UUID"),
    sort_by: Optional[str] = Query(
        "created_at", description="Sort field (created_at, target_date, name)"
    ),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List goals with optional filtering and pagination.

    Access Control:
    - Users can only see goals they created or goals in organizations they belong to
    """
    query = db.query(Goal)

    # Apply access control: only goals user created or organization goals they're in
    user_org_ids = [
        str(m.organization_id)
        for m in db.query(OrganizationMember)
        .filter(OrganizationMember.user_id == current_user.id)
        .all()
    ]

    # Build access control filter
    if user_org_ids:
        query = query.filter(
            or_(
                Goal.created_by == current_user.id,
                Goal.organization_id.in_(user_org_ids),
            )
        )
    else:
        query = query.filter(Goal.created_by == current_user.id)

    # Apply filters
    if status_filter:
        query = query.filter(Goal.status == status_filter)
    if organization_id:
        query = query.filter(Goal.organization_id == organization_id)

    # Apply sorting
    if sort_by:
        sort_column = getattr(Goal, sort_by, Goal.created_at)
    else:
        sort_column = Goal.created_at
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column)

    # Get total count
    total = query.count()

    # Apply pagination - eager load goal_items
    from sqlalchemy.orm import joinedload

    goals = (
        query.options(joinedload(Goal.goal_items).joinedload(GoalItem.item))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Build response
    goal_responses = [build_goal_response(goal) for goal in goals]

    return {
        "goals": goal_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new goal.

    This will:
    1. Validate items exist in goal_items
    2. Validate organization if provided (user must be member)
    3. Create goal with status 'active'
    4. Create GoalItem records
    """
    # Validate goal_items
    item_ids = [item.item_id for item in goal_data.goal_items]
    items = db.query(Item).filter(Item.id.in_(item_ids)).all()
    found_ids = {str(item.id) for item in items}
    missing_ids = [iid for iid in item_ids if iid not in found_ids]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Items not found: {', '.join(missing_ids)}",
        )

    # Validate organization if provided
    if goal_data.organization_id:
        from app.models.organization import Organization

        org = db.query(Organization).filter(Organization.id == goal_data.organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id '{goal_data.organization_id}' not found",
            )
        # Check user is member of organization
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == goal_data.organization_id,
                OrganizationMember.user_id == current_user.id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this organization",
            )

    # Create goal
    new_goal = Goal(
        name=goal_data.name,
        description=goal_data.description,
        organization_id=goal_data.organization_id,
        created_by=current_user.id,
        target_date=goal_data.target_date,
        status=GOAL_STATUS_ACTIVE,
    )
    db.add(new_goal)
    db.flush()  # Flush to get goal.id

    # Create GoalItem records
    for item_data in goal_data.goal_items:
        goal_item = GoalItem(
            goal_id=new_goal.id,
            item_id=item_data.item_id,
            target_quantity=item_data.target_quantity,
        )
        db.add(goal_item)

    db.commit()
    db.refresh(new_goal)

    # Calculate initial progress
    progress = calculate_goal_progress(new_goal, current_user, db)
    new_goal.progress_data = {
        "current_quantity": float(progress.current_quantity),
        "progress_percentage": progress.progress_percentage,
        "is_completed": progress.is_completed,
        "last_calculated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Check completion
    check_goal_completion(new_goal, progress, db)
    db.refresh(new_goal)

    # Eager load goal_items for response
    from sqlalchemy.orm import joinedload

    goal_with_items = (
        db.query(Goal)
        .options(joinedload(Goal.goal_items).joinedload(GoalItem.item))
        .filter(Goal.id == new_goal.id)
        .first()
    )

    if not goal_with_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found after creation",
        )

    # Build response
    response_dict = build_goal_response(goal_with_items)
    return GoalResponse.model_validate(response_dict)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get goal details by ID."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id '{goal_id}' not found",
        )

    # Check access
    validate_goal_access(goal, current_user, db)

    # Eager load goal_items for response
    from sqlalchemy.orm import joinedload

    goal_with_items = (
        db.query(Goal)
        .options(joinedload(Goal.goal_items).joinedload(GoalItem.item))
        .filter(Goal.id == goal_id)
        .first()
    )

    if not goal_with_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id '{goal_id}' not found",
        )

    # Build response
    response_dict = build_goal_response(goal_with_items)
    return GoalResponse.model_validate(response_dict)


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a goal by ID.

    Only allowed for active goals. Completed goals can be updated but won't recalculate progress.
    Cancelled goals cannot be updated.
    """
    goal = db.query(Goal).filter(Goal.id == goal_id).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id '{goal_id}' not found",
        )

    # Check access
    validate_goal_access(goal, current_user, db)

    # Don't allow updating cancelled goals
    if goal.status == GOAL_STATUS_CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a cancelled goal",
        )

    # Validate goal_items if being updated
    if goal_data.goal_items is not None:
        item_ids = [item.item_id for item in goal_data.goal_items]
        items = db.query(Item).filter(Item.id.in_(item_ids)).all()
        found_ids = {str(item.id) for item in items}
        missing_ids = [iid for iid in item_ids if iid not in found_ids]
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Items not found: {', '.join(missing_ids)}",
            )

    # Validate organization if being updated
    if goal_data.organization_id:
        from app.models.organization import Organization

        org = db.query(Organization).filter(Organization.id == goal_data.organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id '{goal_data.organization_id}' not found",
            )
        # Check user is member
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == goal_data.organization_id,
                OrganizationMember.user_id == current_user.id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this organization",
            )

    # Update fields (excluding goal_items which is handled separately)
    update_dict = goal_data.model_dump(exclude_unset=True, exclude={"goal_items"})
    for field, value in update_dict.items():
        setattr(goal, field, value)

    # Update goal_items if provided (replaces all existing)
    if goal_data.goal_items is not None:
        # Delete existing goal_items
        db.query(GoalItem).filter(GoalItem.goal_id == goal.id).delete()
        # Create new goal_items
        for item_data in goal_data.goal_items:
            goal_item = GoalItem(
                goal_id=goal.id,
                item_id=item_data.item_id,
                target_quantity=item_data.target_quantity,
            )
            db.add(goal_item)

    # Recalculate progress if goal is active and has items
    has_items = goal.goal_items and len(goal.goal_items) > 0
    if goal.status == GOAL_STATUS_ACTIVE and has_items:
        progress = calculate_goal_progress(goal, current_user, db)
        if goal.progress_data is None:
            goal.progress_data = {}
        goal.progress_data.update(
            {
                "current_quantity": float(progress.current_quantity),
                "progress_percentage": progress.progress_percentage,
                "is_completed": progress.is_completed,
                "last_calculated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        check_goal_completion(goal, progress, db)

    db.commit()
    db.refresh(goal)

    # Eager load goal_items for response
    from sqlalchemy.orm import joinedload

    goal_with_items = (
        db.query(Goal)
        .options(joinedload(Goal.goal_items).joinedload(GoalItem.item))
        .filter(Goal.id == goal.id)
        .first()
    )

    if not goal_with_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id '{goal.id}' not found",
        )

    # Build response
    response_dict = build_goal_response(goal_with_items)
    return GoalResponse.model_validate(response_dict)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a goal by ID.

    Only allowed for active or cancelled goals.
    """
    goal = db.query(Goal).filter(Goal.id == goal_id).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id '{goal_id}' not found",
        )

    # Check access
    validate_goal_access(goal, current_user, db)

    # Only allow deletion for active or cancelled goals
    if goal.status == GOAL_STATUS_COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a completed goal. Cancel it first if you want to remove it.",
        )

    db.delete(goal)
    db.commit()

    return None


@router.get("/{goal_id}/progress", response_model=GoalProgressResponse)
async def get_goal_progress(
    goal_id: str,
    recalculate: bool = Query(False, description="Force recalculation of progress"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get goal progress information.

    Returns current progress including quantity, percentage, and completion status.
    By default, uses cached progress_data. Set recalculate=True to force recalculation.
    """
    # Eager load goal_items for progress calculation
    from sqlalchemy.orm import joinedload

    goal = db.query(Goal).options(joinedload(Goal.goal_items)).filter(Goal.id == goal_id).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id '{goal_id}' not found",
        )

    # Check access
    validate_goal_access(goal, current_user, db)

    # Calculate progress
    progress = calculate_goal_progress(goal, current_user, db)

    # Update progress_data if recalculating or if goal is active
    if recalculate or goal.status == GOAL_STATUS_ACTIVE:
        if goal.progress_data is None:
            goal.progress_data = {}
        goal.progress_data.update(
            {
                "current_quantity": float(progress.current_quantity),
                "progress_percentage": progress.progress_percentage,
                "is_completed": progress.is_completed,
                "last_calculated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        check_goal_completion(goal, progress, db)
        db.commit()
        db.refresh(goal)

    # Parse last_calculated_at from progress_data
    last_calculated_at = None
    if goal.progress_data and "last_calculated_at" in goal.progress_data:
        try:
            last_calculated_at = datetime.fromisoformat(
                goal.progress_data["last_calculated_at"].replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            pass

    return GoalProgressResponse(
        goal_id=str(goal.id),
        status=goal.status,
        progress=progress,
        last_calculated_at=last_calculated_at,
    )
