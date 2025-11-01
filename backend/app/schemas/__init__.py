"""
Pydantic schemas package.

This module exports all Pydantic schemas for request/response validation.
"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
)
from app.schemas.organization import (
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)
from app.schemas.organization_member import (
    OrganizationMemberBase,
    OrganizationMemberCreate,
    OrganizationMemberResponse,
    OrganizationMemberWithDetails,
)
from app.schemas.auth import (
    Token,
    TokenData,
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    LoginResponse,
    RegisterResponse,
)
from app.schemas.item import (
    ItemBase,
    ItemCreate,
    ItemUpdate,
    ItemResponse,
)
from app.schemas.location import (
    LocationBase,
    LocationCreate,
    LocationUpdate,
    LocationResponse,
)
from app.schemas.ship import (
    ShipBase,
    ShipCreate,
    ShipUpdate,
    ShipResponse,
)
from app.schemas.canonical_location import (
    CanonicalLocationBase,
    CanonicalLocationCreate,
    CanonicalLocationUpdate,
    CanonicalLocationResponse,
)
from app.schemas.inventory import (
    InventoryStock,
    InventoryAdjust,
    InventoryTransfer,
    InventoryHistory,
    StockReservation,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Organization schemas
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    # OrganizationMember schemas
    "OrganizationMemberBase",
    "OrganizationMemberCreate",
    "OrganizationMemberResponse",
    "OrganizationMemberWithDetails",
    # Auth schemas
    "Token",
    "TokenData",
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "LoginResponse",
    "RegisterResponse",
    # Item schemas
    "ItemBase",
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    # Location schemas
    "LocationBase",
    "LocationCreate",
    "LocationUpdate",
    "LocationResponse",
    # Ship schemas
    "ShipBase",
    "ShipCreate",
    "ShipUpdate",
    "ShipResponse",
    # Canonical Location schemas
    "CanonicalLocationBase",
    "CanonicalLocationCreate",
    "CanonicalLocationUpdate",
    "CanonicalLocationResponse",
    # Inventory schemas
    "InventoryStock",
    "InventoryAdjust",
    "InventoryTransfer",
    "InventoryHistory",
    "StockReservation",
]
