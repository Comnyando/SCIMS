"""
Import validation utilities for CSV and JSON data.
"""

from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation
import json
import uuid


class ImportValidationError(Exception):
    """Exception raised for import validation errors."""

    def __init__(self, message: str, row_number: Optional[int] = None, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.row_number = row_number
        self.field = field


def validate_uuid(value: str, field_name: str) -> str:
    """
    Validate and return a UUID string.

    Args:
        value: UUID string to validate
        field_name: Name of the field being validated (for error messages)

    Returns:
        Valid UUID string

    Raises:
        ImportValidationError: If UUID is invalid
    """
    if not value:
        raise ImportValidationError(f"{field_name} is required")
    try:
        # Validate UUID format
        uuid.UUID(value)
        return value
    except (ValueError, AttributeError):
        raise ImportValidationError(f"Invalid UUID format for {field_name}: {value}")


def validate_decimal(value: Any, field_name: str, min_value: Optional[Decimal] = None) -> Decimal:
    """
    Validate and convert value to Decimal.

    Args:
        value: Value to validate (string, int, float, or Decimal)
        field_name: Name of the field being validated
        min_value: Optional minimum value

    Returns:
        Decimal value

    Raises:
        ImportValidationError: If value cannot be converted or doesn't meet constraints
    """
    if value is None or value == "":
        raise ImportValidationError(f"{field_name} is required")

    try:
        decimal_value = Decimal(str(value))
        if min_value is not None and decimal_value < min_value:
            raise ImportValidationError(f"{field_name} must be >= {min_value}, got {decimal_value}")
        return decimal_value
    except (ValueError, InvalidOperation, TypeError):
        raise ImportValidationError(f"Invalid decimal value for {field_name}: {value}")


def validate_int(value: Any, field_name: str, min_value: Optional[int] = None) -> int:
    """
    Validate and convert value to integer.

    Args:
        value: Value to validate
        field_name: Name of the field being validated
        min_value: Optional minimum value

    Returns:
        Integer value

    Raises:
        ImportValidationError: If value cannot be converted or doesn't meet constraints
    """
    if value is None or value == "":
        raise ImportValidationError(f"{field_name} is required")

    try:
        int_value = int(value)
        if min_value is not None and int_value < min_value:
            raise ImportValidationError(f"{field_name} must be >= {min_value}, got {int_value}")
        return int_value
    except (ValueError, TypeError):
        raise ImportValidationError(f"Invalid integer value for {field_name}: {value}")


def validate_string(
    value: Any, field_name: str, max_length: Optional[int] = None, required: bool = True
) -> Optional[str]:
    """
    Validate and return a string value.

    Args:
        value: Value to validate
        field_name: Name of the field being validated
        max_length: Optional maximum length
        required: Whether the field is required

    Returns:
        String value (or None if not required and value is empty)

    Raises:
        ImportValidationError: If validation fails
    """
    if not value or (isinstance(value, str) and value.strip() == ""):
        if required:
            raise ImportValidationError(f"{field_name} is required")
        return None

    str_value = str(value).strip()
    if max_length and len(str_value) > max_length:
        raise ImportValidationError(
            f"{field_name} exceeds maximum length of {max_length} characters"
        )
    return str_value


def validate_json_string(value: Any, field_name: str) -> Optional[Dict[str, Any]]:
    """
    Validate and parse a JSON string.

    Args:
        value: JSON string to parse
        field_name: Name of the field being validated

    Returns:
        Parsed JSON dictionary (or None if value is empty)

    Raises:
        ImportValidationError: If JSON is invalid
    """
    if not value or (isinstance(value, str) and value.strip() == ""):
        return None

    if isinstance(value, dict):
        return value

    if not isinstance(value, str):
        raise ImportValidationError(f"{field_name} must be a JSON string or dictionary")

    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError as e:
        raise ImportValidationError(f"Invalid JSON for {field_name}: {str(e)}")


def validate_item_import(row: Dict[str, Any], row_number: int) -> Dict[str, Any]:
    """
    Validate a single item import row.

    Args:
        row: Dictionary representing a CSV/JSON row
        row_number: Row number for error reporting

    Returns:
        Validated item data dictionary

    Raises:
        ImportValidationError: If validation fails
    """
    try:
        validated = {
            "id": validate_uuid(row.get("id", ""), "id"),
            "name": validate_string(row.get("name"), "name", max_length=255, required=True),
            "description": validate_string(row.get("description"), "description", required=False),
            "category": validate_string(
                row.get("category"), "category", max_length=100, required=False
            ),
            "subcategory": validate_string(
                row.get("subcategory"), "subcategory", max_length=100, required=False
            ),
            "rarity": validate_string(row.get("rarity"), "rarity", max_length=50, required=False),
            "metadata": validate_json_string(row.get("metadata"), "metadata"),
        }
        return validated
    except ImportValidationError as e:
        e.row_number = row_number
        raise


def validate_inventory_import(row: Dict[str, Any], row_number: int) -> Dict[str, Any]:
    """
    Validate a single inventory import row.

    Args:
        row: Dictionary representing a CSV/JSON row
        row_number: Row number for error reporting

    Returns:
        Validated inventory data dictionary

    Raises:
        ImportValidationError: If validation fails
    """
    try:
        validated = {
            "item_id": validate_uuid(row.get("item_id", ""), "item_id"),
            "location_id": validate_uuid(row.get("location_id", ""), "location_id"),
            "quantity": validate_decimal(row.get("quantity"), "quantity", min_value=Decimal("0")),
            "reserved_quantity": validate_decimal(
                row.get("reserved_quantity", "0"), "reserved_quantity", min_value=Decimal("0")
            ),
        }
        # Ensure reserved_quantity doesn't exceed quantity
        reserved_qty = validated["reserved_quantity"]
        qty = validated["quantity"]
        if isinstance(reserved_qty, Decimal) and isinstance(qty, Decimal) and reserved_qty > qty:
            raise ImportValidationError(
                f"reserved_quantity ({validated['reserved_quantity']}) cannot exceed quantity ({validated['quantity']})"
            )
        return validated
    except ImportValidationError as e:
        e.row_number = row_number
        raise


def validate_blueprint_import(row: Dict[str, Any], row_number: int) -> Dict[str, Any]:
    """
    Validate a single blueprint import row.

    Args:
        row: Dictionary representing a CSV/JSON row
        row_number: Row number for error reporting

    Returns:
        Validated blueprint data dictionary

    Raises:
        ImportValidationError: If validation fails
    """
    try:
        blueprint_data = validate_json_string(row.get("blueprint_data"), "blueprint_data")
        if blueprint_data is None:
            raise ImportValidationError("blueprint_data is required")

        # Validate blueprint_data structure
        if "ingredients" not in blueprint_data:
            raise ImportValidationError("blueprint_data must contain 'ingredients' array")

        if not isinstance(blueprint_data["ingredients"], list):
            raise ImportValidationError("blueprint_data.ingredients must be an array")

        validated = {
            "id": validate_uuid(row.get("id", ""), "id"),
            "name": validate_string(row.get("name"), "name", max_length=255, required=True),
            "description": validate_string(row.get("description"), "description", required=False),
            "category": validate_string(
                row.get("category"), "category", max_length=100, required=False
            ),
            "crafting_time_minutes": validate_int(
                row.get("crafting_time_minutes", 0), "crafting_time_minutes", min_value=0
            ),
            "output_item_id": validate_uuid(row.get("output_item_id", ""), "output_item_id"),
            "output_quantity": validate_decimal(
                row.get("output_quantity"), "output_quantity", min_value=Decimal("0.001")
            ),
            "is_public": (
                row.get("is_public", "").lower() == "true" if row.get("is_public") else False
            ),
            "blueprint_data": blueprint_data,
        }

        # Validate ingredients in blueprint_data
        for idx, ingredient in enumerate(blueprint_data["ingredients"]):
            if not isinstance(ingredient, dict):
                raise ImportValidationError(
                    f"blueprint_data.ingredients[{idx}] must be a dictionary"
                )
            if "item_id" not in ingredient:
                raise ImportValidationError(
                    f"blueprint_data.ingredients[{idx}] is missing 'item_id'"
                )
            validate_uuid(ingredient["item_id"], f"blueprint_data.ingredients[{idx}].item_id")
            if "quantity" not in ingredient:
                raise ImportValidationError(
                    f"blueprint_data.ingredients[{idx}] is missing 'quantity'"
                )
            validate_decimal(
                ingredient["quantity"],
                f"blueprint_data.ingredients[{idx}].quantity",
                min_value=Decimal("0.001"),
            )

        return validated
    except ImportValidationError as e:
        e.row_number = row_number
        raise
