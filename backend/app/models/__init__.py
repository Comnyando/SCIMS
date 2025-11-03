"""
Database models package.

This module exports all SQLAlchemy models for the application.
Importing this module ensures all models are registered with SQLAlchemy's
declarative base, which is required for Alembic migrations.
"""

from app.models.base import Base
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.location import Location
from app.models.item import Item
from app.models.item_stock import ItemStock
from app.models.item_history import ItemHistory
from app.models.ship import Ship
from app.models.blueprint import Blueprint
from app.models.craft import Craft
from app.models.craft_ingredient import CraftIngredient
from app.models.resource_source import ResourceSource
from app.models.source_verification_log import SourceVerificationLog
from app.models.goal import Goal
from app.models.goal_item import GoalItem
from app.models.usage_event import UsageEvent
from app.models.recipe_usage_stats import RecipeUsageStats
from app.models.integration import Integration
from app.models.integration_log import IntegrationLog
from app.models.commons_submission import CommonsSubmission
from app.models.commons_moderation_action import CommonsModerationAction
from app.models.commons_entity import CommonsEntity
from app.models.commons_entity_tag import CommonsEntityTag
from app.models.tag import Tag
from app.models.entity_alias import EntityAlias
from app.models.duplicate_group import DuplicateGroup

__all__ = [
    "Base",
    "User",
    "Organization",
    "OrganizationMember",
    "Location",
    "Item",
    "ItemStock",
    "ItemHistory",
    "Ship",
    "Blueprint",
    "Craft",
    "CraftIngredient",
    "ResourceSource",
    "SourceVerificationLog",
    "Goal",
    "GoalItem",
    "UsageEvent",
    "RecipeUsageStats",
    "Integration",
    "IntegrationLog",
    "CommonsSubmission",
    "CommonsModerationAction",
    "CommonsEntity",
    "CommonsEntityTag",
    "Tag",
    "EntityAlias",
    "DuplicateGroup",
]
