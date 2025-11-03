"""
Export utilities for CSV and JSON generation.
"""

import csv
import json
import io
from typing import List, Dict, Any, Optional
from datetime import datetime


def export_items_to_csv(items: List[Dict[str, Any]]) -> str:
    """
    Export items to CSV format.

    Args:
        items: List of item dictionaries

    Returns:
        CSV string
    """
    if not items:
        return "id,name,description,category,subcategory,rarity,metadata,created_at\n"

    output = io.StringIO()
    fieldnames = [
        "id",
        "name",
        "description",
        "category",
        "subcategory",
        "rarity",
        "metadata",
        "created_at",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for item in items:
        row = item.copy()
        # Convert metadata dict to JSON string
        if row.get("metadata"):
            row["metadata"] = json.dumps(row["metadata"])
        # Convert datetime to ISO string
        if row.get("created_at") and isinstance(row["created_at"], datetime):
            row["created_at"] = row["created_at"].isoformat()
        writer.writerow(row)

    return output.getvalue()


def export_inventory_to_csv(inventory_items: List[Dict[str, Any]]) -> str:
    """
    Export inventory stock to CSV format.

    Args:
        inventory_items: List of inventory stock dictionaries

    Returns:
        CSV string
    """
    if not inventory_items:
        return (
            "item_id,item_name,item_category,location_id,location_name,location_type,"
            "quantity,reserved_quantity,available_quantity,last_updated,updated_by_username\n"
        )

    output = io.StringIO()
    fieldnames = [
        "item_id",
        "item_name",
        "item_category",
        "location_id",
        "location_name",
        "location_type",
        "quantity",
        "reserved_quantity",
        "available_quantity",
        "last_updated",
        "updated_by_username",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for inv_item in inventory_items:
        row = inv_item.copy()
        # Convert Decimal to string
        for field in ["quantity", "reserved_quantity", "available_quantity"]:
            if field in row and row[field] is not None:
                row[field] = str(row[field])
        # Convert datetime to ISO string
        if row.get("last_updated") and isinstance(row["last_updated"], datetime):
            row["last_updated"] = row["last_updated"].isoformat()
        writer.writerow(row)

    return output.getvalue()


def export_blueprints_to_csv(blueprints: List[Dict[str, Any]]) -> str:
    """
    Export blueprints to CSV format.

    Args:
        blueprints: List of blueprint dictionaries

    Returns:
        CSV string
    """
    if not blueprints:
        return (
            "id,name,description,category,crafting_time_minutes,output_item_id,"
            "output_quantity,is_public,blueprint_data,created_at\n"
        )

    output = io.StringIO()
    fieldnames = [
        "id",
        "name",
        "description",
        "category",
        "crafting_time_minutes",
        "output_item_id",
        "output_quantity",
        "is_public",
        "blueprint_data",
        "created_at",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for blueprint in blueprints:
        row = blueprint.copy()
        # Convert blueprint_data dict to JSON string
        if row.get("blueprint_data"):
            row["blueprint_data"] = json.dumps(row["blueprint_data"])
        # Convert Decimal to string
        if row.get("output_quantity") is not None:
            row["output_quantity"] = str(row["output_quantity"])
        # Convert boolean to string
        if row.get("is_public") is not None:
            row["is_public"] = str(row["is_public"]).lower()
        # Convert datetime to ISO string
        if row.get("created_at") and isinstance(row["created_at"], datetime):
            row["created_at"] = row["created_at"].isoformat()
        writer.writerow(row)

    return output.getvalue()


def export_items_to_json(items: List[Dict[str, Any]]) -> str:
    """
    Export items to JSON format.

    Args:
        items: List of item dictionaries

    Returns:
        JSON string
    """
    return json.dumps(items, indent=2, default=str)


def export_inventory_to_json(inventory_items: List[Dict[str, Any]]) -> str:
    """
    Export inventory stock to JSON format.

    Args:
        inventory_items: List of inventory stock dictionaries

    Returns:
        JSON string
    """
    return json.dumps(inventory_items, indent=2, default=str)


def export_blueprints_to_json(blueprints: List[Dict[str, Any]]) -> str:
    """
    Export blueprints to JSON format.

    Args:
        blueprints: List of blueprint dictionaries

    Returns:
        JSON string
    """
    return json.dumps(blueprints, indent=2, default=str)
