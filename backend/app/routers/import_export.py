"""
Import/Export router for data import and export operations.

Supports CSV and JSON formats for:
- Items
- Inventory stock
- Blueprints (recipes)
"""

import csv
import io
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_db
from app.models.item import Item
from app.models.location import Location
from app.models.item_stock import ItemStock
from app.models.blueprint import Blueprint
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.import_export import ExportFilters, ImportResponse
from app.schemas.item import ItemCreate, ItemResponse
from app.schemas.blueprint import BlueprintCreate
from app.utils.export import (
    export_items_to_csv,
    export_inventory_to_csv,
    export_blueprints_to_csv,
    export_items_to_json,
    export_inventory_to_json,
    export_blueprints_to_json,
)
from app.utils.import_validation import (
    validate_item_import,
    validate_inventory_import,
    validate_blueprint_import,
    ImportValidationError,
)
from app.routers.inventory import check_location_access_for_inventory
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/import-export", tags=["import-export"])


# ==================== Export Endpoints ====================


@router.get("/items.csv")
async def export_items_csv(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export items to CSV format."""
    query = db.query(Item)

    # Apply filters
    if category:
        query = query.filter(Item.category == category)

    # Get all items (no pagination for export)
    items = query.order_by(Item.name).all()

    # Convert to dict format
    items_data = [
        {
            "id": str(item.id),
            "name": item.name,
            "description": item.description,
            "category": item.category,
            "subcategory": item.subcategory,
            "rarity": item.rarity,
            "metadata": item.metadata,
            "created_at": item.created_at,
        }
        for item in items
    ]

    csv_content = export_items_to_csv(items_data)

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=items_export.csv"},
    )


@router.get("/items.json")
async def export_items_json(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export items to JSON format."""
    query = db.query(Item)

    # Apply filters
    if category:
        query = query.filter(Item.category == category)

    # Get all items
    items = query.order_by(Item.name).all()

    # Convert to dict format
    items_data = [
        {
            "id": str(item.id),
            "name": item.name,
            "description": item.description,
            "category": item.category,
            "subcategory": item.subcategory,
            "rarity": item.rarity,
            "metadata": item.metadata,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in items
    ]

    json_content = export_items_to_json(items_data)

    return JSONResponse(
        content=json.loads(json_content),
        headers={"Content-Disposition": "attachment; filename=items_export.json"},
    )


@router.get("/inventory.csv")
async def export_inventory_csv(
    location_id: Optional[str] = Query(None, description="Filter by location ID"),
    item_id: Optional[str] = Query(None, description="Filter by item ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export inventory stock to CSV format."""
    from app.routers.inventory import list_inventory

    # Use the existing inventory list endpoint logic but get all results
    # We'll build a simplified query here
    query = (
        db.query(ItemStock, Item, Location)
        .join(Item, ItemStock.item_id == Item.id)
        .join(Location, ItemStock.location_id == Location.id)
    )

    # Apply filters
    if location_id:
        query = query.filter(ItemStock.location_id == location_id)
    if item_id:
        query = query.filter(ItemStock.item_id == item_id)

    # Get accessible locations
    from app.routers.goals import get_accessible_location_ids

    accessible_location_ids = get_accessible_location_ids(current_user, db)
    if accessible_location_ids:
        query = query.filter(ItemStock.location_id.in_(accessible_location_ids))
    else:
        # No accessible locations, return empty
        csv_content = export_inventory_to_csv([])
        return StreamingResponse(
            io.BytesIO(csv_content.encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=inventory_export.csv"},
        )

    results = query.all()

    # Build inventory data
    inventory_data = []
    for stock, item, location in results:
        # Check fine-grained access
        if check_location_access_for_inventory(location, current_user, db, "viewer"):
            inventory_data.append(
                {
                    "item_id": str(item.id),
                    "item_name": item.name,
                    "item_category": item.category,
                    "location_id": str(location.id),
                    "location_name": location.name,
                    "location_type": location.type,
                    "quantity": stock.quantity,
                    "reserved_quantity": stock.reserved_quantity,
                    "available_quantity": stock.quantity - stock.reserved_quantity,
                    "last_updated": stock.last_updated,
                    "updated_by_username": None,  # Would need to join with user table
                }
            )

    csv_content = export_inventory_to_csv(inventory_data)

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_export.csv"},
    )


@router.get("/inventory.json")
async def export_inventory_json(
    location_id: Optional[str] = Query(None, description="Filter by location ID"),
    item_id: Optional[str] = Query(None, description="Filter by item ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export inventory stock to JSON format."""
    # Reuse CSV logic but return JSON
    query = (
        db.query(ItemStock, Item, Location)
        .join(Item, ItemStock.item_id == Item.id)
        .join(Location, ItemStock.location_id == Location.id)
    )

    if location_id:
        query = query.filter(ItemStock.location_id == location_id)
    if item_id:
        query = query.filter(ItemStock.item_id == item_id)

    from app.routers.goals import get_accessible_location_ids

    accessible_location_ids = get_accessible_location_ids(current_user, db)
    if accessible_location_ids:
        query = query.filter(ItemStock.location_id.in_(accessible_location_ids))
    else:
        json_content = export_inventory_to_json([])
        return JSONResponse(
            content=json.loads(json_content),
            headers={"Content-Disposition": "attachment; filename=inventory_export.json"},
        )

    results = query.all()

    inventory_data = []
    for stock, item, location in results:
        if check_location_access_for_inventory(location, current_user, db, "viewer"):
            inventory_data.append(
                {
                    "item_id": str(item.id),
                    "item_name": item.name,
                    "item_category": item.category,
                    "location_id": str(location.id),
                    "location_name": location.name,
                    "location_type": location.type,
                    "quantity": str(stock.quantity),
                    "reserved_quantity": str(stock.reserved_quantity),
                    "available_quantity": str(stock.quantity - stock.reserved_quantity),
                    "last_updated": stock.last_updated.isoformat() if stock.last_updated else None,
                    "updated_by_username": None,
                }
            )

    json_content = export_inventory_to_json(inventory_data)

    return JSONResponse(
        content=json.loads(json_content),
        headers={"Content-Disposition": "attachment; filename=inventory_export.json"},
    )


@router.get("/blueprints.csv")
async def export_blueprints_csv(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export blueprints to CSV format."""
    query = db.query(Blueprint)

    # Apply access control: only public blueprints or user's own
    query = query.filter(
        or_(
            Blueprint.is_public == True,  # noqa: E712
            Blueprint.created_by == current_user.id,
        )
    )

    # Apply filters
    if category:
        query = query.filter(Blueprint.category == category)
    if is_public is not None:
        query = query.filter(Blueprint.is_public == is_public)

    blueprints = query.order_by(Blueprint.name).all()

    # Convert to dict format
    blueprints_data = []
    for bp in blueprints:
        blueprints_data.append(
            {
                "id": str(bp.id),
                "name": bp.name,
                "description": bp.description,
                "category": bp.category,
                "crafting_time_minutes": bp.crafting_time_minutes,
                "output_item_id": bp.output_item_id,
                "output_quantity": bp.output_quantity,
                "is_public": bp.is_public,
                "blueprint_data": bp.blueprint_data if bp.blueprint_data else {"ingredients": []},
                "created_at": bp.created_at,
            }
        )

    csv_content = export_blueprints_to_csv(blueprints_data)

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=blueprints_export.csv"},
    )


@router.get("/blueprints.json")
async def export_blueprints_json(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export blueprints to JSON format."""
    query = db.query(Blueprint)

    query = query.filter(
        or_(
            Blueprint.is_public == True,  # noqa: E712
            Blueprint.created_by == current_user.id,
        )
    )

    if category:
        query = query.filter(Blueprint.category == category)
    if is_public is not None:
        query = query.filter(Blueprint.is_public == is_public)

    blueprints = query.order_by(Blueprint.name).all()

    # Convert to dict format
    blueprints_data = []
    for bp in blueprints:
        blueprints_data.append(
            {
                "id": str(bp.id),
                "name": bp.name,
                "description": bp.description,
                "category": bp.category,
                "crafting_time_minutes": bp.crafting_time_minutes,
                "output_item_id": bp.output_item_id,
                "output_quantity": str(bp.output_quantity),
                "is_public": bp.is_public,
                "blueprint_data": bp.blueprint_data if bp.blueprint_data else {"ingredients": []},
                "created_at": bp.created_at.isoformat() if bp.created_at else None,
            }
        )

    json_content = export_blueprints_to_json(blueprints_data)

    return JSONResponse(
        content=json.loads(json_content),
        headers={"Content-Disposition": "attachment; filename=blueprints_export.json"},
    )


# ==================== Import Endpoints ====================


@router.post("/items/import", response_model=ImportResponse)
async def import_items(
    file: UploadFile = File(..., description="CSV or JSON file to import"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Import items from CSV or JSON file."""
    content = await file.read()
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""

    # Parse file based on extension
    if file_extension == "csv":
        # Parse CSV
        csv_content = content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)
    elif file_extension == "json":
        # Parse JSON
        rows = json.loads(content.decode("utf-8"))
        if not isinstance(rows, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON file must contain an array of items",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Use CSV or JSON",
        )

    imported_count = 0
    failed_count = 0
    errors = []

    for idx, row in enumerate(rows, start=1):
        try:
            validated_data = validate_item_import(row, idx)

            # Check if item already exists (by ID if provided, or by name)
            existing_item = None
            if validated_data.get("id"):
                existing_item = db.query(Item).filter(Item.id == validated_data["id"]).first()
            else:
                # If no ID provided, check by name
                existing_item = db.query(Item).filter(Item.name == validated_data["name"]).first()

            if existing_item:
                # Update existing item
                for key, value in validated_data.items():
                    if key != "id" and value is not None:
                        setattr(existing_item, key, value)
                db.add(existing_item)
            else:
                # Create new item (generate ID if not provided)
                item_data = ItemCreate(**validated_data)
                new_item = Item(
                    id=validated_data.get("id") or None,  # Let DB generate if not provided
                    name=item_data.name,
                    description=item_data.description,
                    category=item_data.category,
                    subcategory=item_data.subcategory,
                    rarity=item_data.rarity,
                    metadata=item_data.metadata,
                )
                db.add(new_item)

            imported_count += 1

        except ImportValidationError as e:
            failed_count += 1
            errors.append(
                {
                    "row_number": e.row_number or idx,
                    "field": e.field,
                    "message": e.message,
                }
            )
        except Exception as e:
            failed_count += 1
            errors.append({"row_number": idx, "field": None, "message": str(e)})

    db.commit()

    return ImportResponse(
        success=failed_count == 0,
        imported_count=imported_count,
        failed_count=failed_count,
        errors=errors,
    )


@router.post("/inventory/import", response_model=ImportResponse)
async def import_inventory(
    file: UploadFile = File(..., description="CSV or JSON file to import"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Import inventory stock from CSV or JSON file."""
    content = await file.read()
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""

    if file_extension == "csv":
        csv_content = content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)
    elif file_extension == "json":
        rows = json.loads(content.decode("utf-8"))
        if not isinstance(rows, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON file must contain an array of inventory items",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Use CSV or JSON",
        )

    imported_count = 0
    failed_count = 0
    errors = []

    for idx, row in enumerate(rows, start=1):
        try:
            validated_data = validate_inventory_import(row, idx)

            # Verify item and location exist and are accessible
            item = db.query(Item).filter(Item.id == validated_data["item_id"]).first()
            if not item:
                raise ImportValidationError(
                    f"Item with id '{validated_data['item_id']}' not found", row_number=idx
                )

            location = (
                db.query(Location).filter(Location.id == validated_data["location_id"]).first()
            )
            if not location:
                raise ImportValidationError(
                    f"Location with id '{validated_data['location_id']}' not found", row_number=idx
                )

            # Check access
            if not check_location_access_for_inventory(location, current_user, db, "member"):
                raise ImportValidationError(
                    f"No access to location '{location.name}'", row_number=idx
                )

            # Get or create ItemStock
            stock = (
                db.query(ItemStock)
                .filter(
                    ItemStock.item_id == validated_data["item_id"],
                    ItemStock.location_id == validated_data["location_id"],
                )
                .first()
            )

            if not stock:
                from decimal import Decimal

                stock = ItemStock(
                    item_id=validated_data["item_id"],
                    location_id=validated_data["location_id"],
                    quantity=Decimal("0"),
                    reserved_quantity=Decimal("0"),
                    updated_by=current_user.id,
                )
                db.add(stock)

            stock.quantity = validated_data["quantity"]
            stock.reserved_quantity = validated_data["reserved_quantity"]
            db.add(stock)

            imported_count += 1

        except ImportValidationError as e:
            failed_count += 1
            errors.append(
                {
                    "row_number": e.row_number or idx,
                    "field": e.field,
                    "message": e.message,
                }
            )
        except Exception as e:
            failed_count += 1
            errors.append({"row_number": idx, "field": None, "message": str(e)})

    db.commit()

    return ImportResponse(
        success=failed_count == 0,
        imported_count=imported_count,
        failed_count=failed_count,
        errors=errors,
    )


@router.post("/blueprints/import", response_model=ImportResponse)
async def import_blueprints(
    file: UploadFile = File(..., description="CSV or JSON file to import"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Import blueprints from CSV or JSON file."""
    content = await file.read()
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""

    if file_extension == "csv":
        csv_content = content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)
    elif file_extension == "json":
        rows = json.loads(content.decode("utf-8"))
        if not isinstance(rows, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON file must contain an array of blueprints",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Use CSV or JSON",
        )

    imported_count = 0
    failed_count = 0
    errors = []

    for idx, row in enumerate(rows, start=1):
        try:
            validated_data = validate_blueprint_import(row, idx)

            # Verify output item exists
            output_item = db.query(Item).filter(Item.id == validated_data["output_item_id"]).first()
            if not output_item:
                raise ImportValidationError(
                    f"Output item with id '{validated_data['output_item_id']}' not found",
                    row_number=idx,
                )

            # Verify all ingredient items exist
            for ing_idx, ingredient in enumerate(validated_data["blueprint_data"]["ingredients"]):
                ing_item = db.query(Item).filter(Item.id == ingredient["item_id"]).first()
                if not ing_item:
                    raise ImportValidationError(
                        f"Ingredient item with id '{ingredient['item_id']}' not found",
                        row_number=idx,
                    )

            # Check if blueprint already exists
            existing_bp = None
            if validated_data.get("id"):
                existing_bp = (
                    db.query(Blueprint).filter(Blueprint.id == validated_data["id"]).first()
                )
            else:
                existing_bp = (
                    db.query(Blueprint)
                    .filter(Blueprint.name == validated_data["name"])
                    .filter(Blueprint.created_by == current_user.id)
                    .first()
                )

            if existing_bp:
                # Update existing blueprint
                existing_bp.name = validated_data["name"]
                existing_bp.description = validated_data["description"]
                existing_bp.category = validated_data["category"]
                existing_bp.crafting_time_minutes = validated_data["crafting_time_minutes"]
                existing_bp.output_item_id = validated_data["output_item_id"]
                existing_bp.output_quantity = validated_data["output_quantity"]
                existing_bp.is_public = validated_data["is_public"]
                existing_bp.blueprint_data = validated_data["blueprint_data"]

                db.add(existing_bp)
            else:
                # Create new blueprint
                blueprint_data = BlueprintCreate(**validated_data)
                new_bp = Blueprint(
                    id=validated_data.get("id") or None,
                    name=blueprint_data.name,
                    description=blueprint_data.description,
                    category=blueprint_data.category,
                    crafting_time_minutes=blueprint_data.crafting_time_minutes,
                    output_item_id=blueprint_data.output_item_id,
                    output_quantity=blueprint_data.output_quantity,
                    blueprint_data=blueprint_data.blueprint_data,
                    is_public=blueprint_data.is_public,
                    created_by=current_user.id,
                )
                db.add(new_bp)

            imported_count += 1

        except ImportValidationError as e:
            failed_count += 1
            errors.append(
                {
                    "row_number": e.row_number or idx,
                    "field": e.field,
                    "message": e.message,
                }
            )
        except Exception as e:
            failed_count += 1
            errors.append({"row_number": idx, "field": None, "message": str(e)})

    db.commit()

    return ImportResponse(
        success=failed_count == 0,
        imported_count=imported_count,
        failed_count=failed_count,
        errors=errors,
    )
