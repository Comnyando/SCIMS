"""
Celery tasks for craft operations.

Handles automated craft completion based on crafting time.
"""

from datetime import datetime, timezone
from decimal import Decimal
from celery import Task
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.craft import Craft, CRAFT_STATUS_IN_PROGRESS, CRAFT_STATUS_COMPLETED
from app.models.craft_ingredient import (
    CraftIngredient,
    INGREDIENT_STATUS_RESERVED,
    INGREDIENT_STATUS_FULFILLED,
    SOURCE_TYPE_STOCK,
)
from app.models.blueprint import Blueprint
from app.models.item_stock import ItemStock
from app.models.item_history import ItemHistory
from app.models.user import User

# Import the complete logic from the router
# We'll reuse the logic but need to adapt it for background execution


def get_system_user_id(db: Session) -> str:
    """
    Get a system user ID for automated operations.

    In production, you might want to create a dedicated system user.
    For now, we'll try to find the first admin user or create a system user.
    """
    # Try to find first active user (fallback for automated operations)
    user = db.query(User).filter(User.is_active == True).first()
    if user:
        return user.id

    # If no users exist, we can't proceed
    raise ValueError("No active users found for automated craft completion")


@celery_app.task(name="app.tasks.crafts.complete_ready_crafts", bind=True)
def complete_ready_crafts(self: Task) -> dict:
    """
    Celery task to automatically complete crafts that have finished crafting.

    This task:
    1. Finds all in_progress crafts
    2. Checks if crafting time has elapsed (started_at + crafting_time_minutes <= now)
    3. Completes eligible crafts by:
       - Deducting reserved ingredient stock
       - Adding output items to output location
       - Updating craft status to completed
       - Logging all transactions

    Returns:
        dict: Summary of completed crafts
    """
    db: Session = SessionLocal()
    completed_count = 0
    errors = []

    try:
        # Get current time
        now = datetime.now(timezone.utc)

        # Find all in_progress crafts with their blueprints
        crafts = (
            db.query(Craft)
            .join(Blueprint)
            .filter(Craft.status == CRAFT_STATUS_IN_PROGRESS)
            .filter(Craft.started_at.isnot(None))
            .all()
        )

        # Get system user ID for automated operations
        try:
            system_user_id = get_system_user_id(db)
        except ValueError as e:
            db.close()
            return {
                "status": "error",
                "message": str(e),
                "completed_count": 0,
            }

        for craft in crafts:
            try:
                # Get blueprint to check crafting time
                blueprint = db.query(Blueprint).filter(Blueprint.id == craft.blueprint_id).first()
                if not blueprint:
                    errors.append(f"Craft {craft.id}: Blueprint not found")
                    continue

                # Check if crafting time has elapsed
                if not craft.started_at:
                    continue

                elapsed_time = now - craft.started_at
                elapsed_minutes = elapsed_time.total_seconds() / 60

                if elapsed_minutes < blueprint.crafting_time_minutes:
                    # Not ready yet
                    continue

                # Craft is ready to complete - perform completion
                # Load ingredients
                ingredients = (
                    db.query(CraftIngredient).filter(CraftIngredient.craft_id == craft.id).all()
                )

                # Deduct reserved stock for all reserved ingredients
                for ingredient in ingredients:
                    if (
                        ingredient.status == INGREDIENT_STATUS_RESERVED
                        and ingredient.source_type == SOURCE_TYPE_STOCK
                    ):
                        # Get stock
                        stock = (
                            db.query(ItemStock)
                            .filter(
                                ItemStock.item_id == ingredient.item_id,
                                ItemStock.location_id == ingredient.source_location_id,
                            )
                            .first()
                        )

                        if stock:
                            # Validate we have enough reserved
                            if stock.reserved_quantity >= ingredient.required_quantity:
                                # Deduct from quantity and reserved_quantity
                                stock.quantity -= ingredient.required_quantity
                                stock.reserved_quantity -= ingredient.required_quantity
                                stock.updated_by = system_user_id

                                # Log history
                                history_entry = ItemHistory(
                                    item_id=ingredient.item_id,
                                    location_id=ingredient.source_location_id,
                                    quantity_change=-ingredient.required_quantity,
                                    transaction_type="consume",
                                    performed_by=system_user_id,
                                    notes=f"Automated completion: consumed for craft {craft.id}",
                                    related_craft_id=craft.id,
                                )
                                db.add(history_entry)

                        # Mark ingredient as fulfilled
                        ingredient.status = INGREDIENT_STATUS_FULFILLED

                # Add output items to output location
                from app.routers.inventory import get_or_create_item_stock

                output_stock = get_or_create_item_stock(
                    db, blueprint.output_item_id, craft.output_location_id, system_user_id
                )
                output_stock.quantity += blueprint.output_quantity
                output_stock.updated_by = system_user_id

                # Log history for output
                output_history = ItemHistory(
                    item_id=blueprint.output_item_id,
                    location_id=craft.output_location_id,
                    quantity_change=blueprint.output_quantity,
                    transaction_type="craft",
                    performed_by=system_user_id,
                    notes=f"Automated completion: crafted from blueprint {blueprint.id}",
                    related_craft_id=craft.id,
                )
                db.add(output_history)

                # Update craft
                craft.status = CRAFT_STATUS_COMPLETED
                craft.completed_at = now

                # Commit this craft
                db.commit()
                completed_count += 1

            except Exception as e:
                # Rollback this craft's transaction
                db.rollback()
                errors.append(f"Craft {craft.id}: {str(e)}")
                continue

        return {
            "status": "success",
            "completed_count": completed_count,
            "errors": errors if errors else None,
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e),
            "completed_count": completed_count,
            "errors": errors,
        }
    finally:
        db.close()
