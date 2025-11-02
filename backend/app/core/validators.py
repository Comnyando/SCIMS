"""
Custom validators for Pydantic models.
"""

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from email_validator import validate_email, EmailNotValidError
from app.config import settings


class DevEmailStr(str):
    """
    Custom email string type that allows .local domains in development.

    In development mode, emails with .local domains are allowed.
    In production, standard email validation applies.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: str) -> str:
        """Validate email address, allowing .local in development."""
        if not isinstance(value, str):
            raise ValueError("Email must be a string")

        # Strip whitespace
        value = value.strip()
        if not value:
            raise ValueError("Email cannot be empty")

        # Basic format check: must contain exactly one @
        if value.count("@") != 1:
            raise ValueError("Email must contain exactly one @ symbol")

        # Split into local and domain parts
        parts = value.split("@")
        local_part = parts[0]
        domain_part = parts[1]

        # Validate local part exists and is not empty
        if not local_part or len(local_part) == 0:
            raise ValueError("Email local part (before @) cannot be empty")

        # Validate domain part exists and is not empty
        if not domain_part or len(domain_part) == 0:
            raise ValueError("Email domain part (after @) cannot be empty")

        # In development, allow .local domains with basic validation
        if settings.environment == "development" and value.endswith("@scims.local"):
            # Additional basic checks for .local domains in dev
            if domain_part == "scims.local" and local_part:
                # Check local part is reasonable (not just special chars)
                if local_part.replace(".", "").replace("_", "").replace("-", "").isalnum() or any(
                    c.isalnum() for c in local_part
                ):
                    return value
                else:
                    raise ValueError("Email local part contains only invalid characters")

        # For all other cases, use standard email validation
        try:
            validated = validate_email(value, check_deliverability=False)
            return validated.email
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {str(e)}")
