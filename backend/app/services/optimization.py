"""
Optimization service for finding sources and suggesting crafts.

This service implements algorithms for:
- Finding sources for items (checking stocks, players, universe sources)
- Suggesting crafts to produce target items
- Analyzing resource gaps for crafts
"""

from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc
from sqlalchemy import nullslast

from app.models.item import Item
from app.models.item_stock import ItemStock
from app.models.location import Location
from app.models.resource_source import (
    ResourceSource,
    SOURCE_TYPE_PLAYER_STOCK,
    SOURCE_TYPE_UNIVERSE_LOCATION,
    SOURCE_TYPE_TRADING_POST,
)
from app.models.blueprint import Blueprint
from app.models.craft import Craft
from app.models.craft_ingredient import CraftIngredient
from app.models.organization_member import OrganizationMember
from app.schemas.optimization import (
    SourceOption,
    FindSourcesRequest,
    FindSourcesResponse,
    CraftSuggestion,
    SuggestCraftsRequest,
    SuggestCraftsResponse,
    ResourceGapItem,
    ResourceGapResponse,
)


class OptimizationService:
    """Service for optimization algorithms."""

    def __init__(self, db: Session, current_user_id: str):
        """
        Initialize optimization service.

        Args:
            db: Database session
            current_user_id: Current user UUID
        """
        self.db = db
        self.current_user_id = current_user_id

    def find_sources_for_item(self, request: FindSourcesRequest) -> FindSourcesResponse:
        """
        Find sources for a specific item.

        Algorithm priority:
        1. Own stock (user and organization locations)
        2. Other players' stocks (if permissions allow)
        3. Universe sources (trading posts, locations)

        Sources are sorted by:
        - Cost (lower is better, owned stock = 0)
        - Reliability (higher is better for universe sources)
        - Availability (can we get enough quantity)

        Args:
            request: FindSourcesRequest with item_id and required_quantity

        Returns:
            FindSourcesResponse with sorted list of source options
        """
        # Get item
        item = self.db.query(Item).filter(Item.id == request.item_id).first()
        if not item:
            raise ValueError(f"Item with id '{request.item_id}' not found")

        sources: List[SourceOption] = []

        # 1. Check own stock (user and organization locations)
        accessible_location_ids = self._get_accessible_location_ids(request.organization_id)
        if accessible_location_ids:
            stocks = (
                self.db.query(ItemStock)
                .options(joinedload(ItemStock.location))
                .filter(
                    ItemStock.item_id == request.item_id,
                    ItemStock.location_id.in_(accessible_location_ids),
                )
                .all()
            )

            for stock in stocks:
                available = stock.available_quantity
                if available > 0:
                    needed = min(request.required_quantity, available)
                    sources.append(
                        SourceOption(
                            source_type="stock",
                            location_id=stock.location_id,
                            location_name=stock.location.name if stock.location else None,
                            source_id=None,
                            source_identifier=None,
                            available_quantity=float(available),
                            cost_per_unit=0.0,
                            total_cost=0.0,
                            reliability_score=None,
                            metadata=None,
                        )
                    )

        # 2. Check other players' stocks (if requested and permissions allow)
        # Note: For now, we'll only check if the player has explicitly shared stock info
        # via resource_sources with source_type=player_stock
        if request.include_player_stocks:
            player_sources = (
                self.db.query(ResourceSource)
                .filter(
                    ResourceSource.item_id == request.item_id,
                    ResourceSource.source_type == SOURCE_TYPE_PLAYER_STOCK,
                )
                .order_by(desc(ResourceSource.reliability_score))
                .limit(request.max_sources)
                .all()
            )

            for source in player_sources:
                if source.available_quantity > 0:
                    needed = min(request.required_quantity, source.available_quantity)
                    cost_per_unit = source.cost_per_unit or Decimal("0")
                    sources.append(
                        SourceOption(
                            source_type="player_stock",
                            location_id=source.location_id,
                            location_name=(source.location.name if source.location else None),
                            source_id=source.id,
                            source_identifier=source.source_identifier,
                            available_quantity=float(source.available_quantity),
                            cost_per_unit=float(cost_per_unit),
                            total_cost=float(cost_per_unit * needed),
                            reliability_score=(
                                float(source.reliability_score)
                                if source.reliability_score
                                else None
                            ),
                            metadata=source.source_metadata,
                        )
                    )

        # 3. Check universe sources (trading posts, locations)
        universe_query = (
            self.db.query(ResourceSource)
            .options(joinedload(ResourceSource.location))
            .filter(
                ResourceSource.item_id == request.item_id,
                ResourceSource.source_type.in_(
                    [SOURCE_TYPE_UNIVERSE_LOCATION, SOURCE_TYPE_TRADING_POST]
                ),
            )
        )

        if request.min_reliability is not None:
            universe_query = universe_query.filter(
                ResourceSource.reliability_score >= request.min_reliability
            )

        universe_sources = (
            universe_query.order_by(
                desc(ResourceSource.reliability_score),
                nullslast(ResourceSource.cost_per_unit.asc()),
            )
            .limit(request.max_sources)
            .all()
        )

        for source in universe_sources:
            if source.available_quantity > 0:
                needed = min(request.required_quantity, source.available_quantity)
                cost_per_unit = source.cost_per_unit or Decimal("0")
                sources.append(
                    SourceOption(
                        source_type=source.source_type,
                        location_id=source.location_id,
                        location_name=(source.location.name if source.location else None),
                        source_id=source.id,
                        source_identifier=source.source_identifier,
                        available_quantity=float(source.available_quantity),
                        cost_per_unit=float(cost_per_unit),
                        total_cost=float(cost_per_unit * needed),
                        reliability_score=(
                            float(source.reliability_score) if source.reliability_score else None
                        ),
                        metadata=source.source_metadata,
                    )
                )

        # Sort sources by priority:
        # 1. Own stock (cost=0) first
        # 2. Then by cost ascending
        # 3. Then by reliability descending
        sources.sort(
            key=lambda s: (
                s.cost_per_unit,  # Own stock (0) comes first
                -(s.reliability_score or 0.0),  # Higher reliability is better
            )
        )

        # Limit to max_sources
        sources = sources[: request.max_sources]

        # Calculate totals
        total_available = sum(s.available_quantity for s in sources)
        has_sufficient = total_available >= request.required_quantity

        return FindSourcesResponse(
            item_id=request.item_id,
            item_name=item.name,
            required_quantity=float(request.required_quantity),
            sources=sources,
            total_available=float(total_available),
            has_sufficient=has_sufficient,
        )

    def suggest_crafts(self, request: SuggestCraftsRequest) -> SuggestCraftsResponse:
        """
        Suggest crafts to produce a target item.

        Algorithm:
        1. Find all blueprints that produce the target item
        2. For each blueprint, check ingredient availability
        3. Calculate how many times to craft to reach target quantity
        4. Sort by feasibility (all ingredients available first, then by crafting time)

        Args:
            request: SuggestCraftsRequest with target_item_id and target_quantity

        Returns:
            SuggestCraftsResponse with craft suggestions
        """
        # Get target item
        target_item = self.db.query(Item).filter(Item.id == request.target_item_id).first()
        if not target_item:
            raise ValueError(f"Item with id '{request.target_item_id}' not found")

        # Find blueprints that produce this item
        blueprints = (
            self.db.query(Blueprint)
            .filter(Blueprint.output_item_id == request.target_item_id)
            .all()
        )

        suggestions: List[CraftSuggestion] = []

        accessible_location_ids = self._get_accessible_location_ids(request.organization_id)

        for blueprint in blueprints:
            # Parse blueprint ingredients
            blueprint_data = blueprint.blueprint_data or {}
            ingredients_data = blueprint_data.get("ingredients", [])

            if not ingredients_data:
                # Skip blueprints without ingredients
                continue

            # Check ingredient availability
            all_available = True
            ingredient_info = []

            for ing_data in ingredients_data:
                if ing_data.get("optional", False):
                    continue  # Skip optional ingredients for availability check

                item_id = ing_data["item_id"]
                required_qty = Decimal(str(ing_data["quantity"]))

                # Check stock availability
                if accessible_location_ids:
                    total_available = (
                        self.db.query(ItemStock)
                        .filter(
                            ItemStock.item_id == item_id,
                            ItemStock.location_id.in_(accessible_location_ids),
                        )
                        .all()
                    )
                    available = sum(stock.available_quantity for stock in total_available)
                else:
                    available = Decimal("0")

                ingredient_info.append(
                    {
                        "item_id": item_id,
                        "quantity": float(required_qty),
                        "available": float(available),
                    }
                )

                if available < required_qty:
                    all_available = False

            # Calculate how many times to craft
            # For simplicity, assume we craft enough times to produce target quantity
            # (In a real scenario, we'd need to account for ingredient consumption)
            output_per_craft = blueprint.output_quantity
            from decimal import ROUND_UP

            suggested_count = max(
                1,
                int(
                    (request.target_quantity / output_per_craft).quantize(
                        Decimal("1"), rounding=ROUND_UP
                    )
                ),
            )
            total_output = output_per_craft * Decimal(suggested_count)

            suggestions.append(
                CraftSuggestion(
                    blueprint_id=blueprint.id,
                    blueprint_name=blueprint.name,
                    output_item_id=blueprint.output_item_id,
                    output_item_name=target_item.name,
                    output_quantity=float(output_per_craft),
                    crafting_time_minutes=blueprint.crafting_time_minutes,
                    suggested_count=suggested_count,
                    total_output=float(total_output),
                    ingredients=ingredient_info,
                    all_ingredients_available=all_available,
                )
            )

        # Sort suggestions:
        # 1. All ingredients available first
        # 2. Then by crafting time (shorter is better)
        suggestions.sort(
            key=lambda s: (
                not s.all_ingredients_available,  # True (available) sorts before False
                s.crafting_time_minutes,
            )
        )

        # Limit to max_suggestions
        suggestions = suggestions[: request.max_suggestions]

        return SuggestCraftsResponse(
            target_item_id=request.target_item_id,
            target_item_name=target_item.name,
            target_quantity=float(request.target_quantity),
            suggestions=suggestions,
        )

    def get_resource_gap(self, craft_id: str) -> ResourceGapResponse:
        """
        Analyze resource gaps for a craft.

        For each ingredient, calculates:
        - Required quantity
        - Available quantity
        - Gap quantity
        - Available sources to fill the gap

        Args:
            craft_id: Craft UUID

        Returns:
            ResourceGapResponse with gap analysis
        """
        # Get craft with ingredients
        craft = (
            self.db.query(Craft)
            .options(joinedload(Craft.blueprint))
            .filter(Craft.id == craft_id)
            .first()
        )

        if not craft:
            raise ValueError(f"Craft with id '{craft_id}' not found")

        # Get blueprint and ingredients
        blueprint = craft.blueprint
        ingredients = (
            self.db.query(CraftIngredient)
            .options(joinedload(CraftIngredient.item))
            .filter(CraftIngredient.craft_id == craft_id)
            .all()
        )

        gaps: List[ResourceGapItem] = []

        accessible_location_ids = self._get_accessible_location_ids(craft.organization_id)

        for ingredient in ingredients:
            # Calculate available quantity from stock
            available = Decimal("0")
            if accessible_location_ids:
                stocks = (
                    self.db.query(ItemStock)
                    .options(joinedload(ItemStock.location))
                    .filter(
                        ItemStock.item_id == ingredient.item_id,
                        ItemStock.location_id.in_(accessible_location_ids),
                    )
                    .all()
                )
                available = Decimal(sum(float(stock.available_quantity) for stock in stocks))

            gap = ingredient.required_quantity - available

            # Find sources to fill the gap
            sources: List[SourceOption] = []
            if gap > 0:
                # Use find_sources_for_item to get source options
                try:
                    find_request = FindSourcesRequest(
                        item_id=ingredient.item_id,
                        required_quantity=gap,
                        max_sources=10,
                        include_player_stocks=True,
                        min_reliability=None,
                        organization_id=craft.organization_id,
                    )
                    sources_response = self.find_sources_for_item(find_request)
                    sources = sources_response.sources
                except Exception:
                    # If finding sources fails, continue with empty sources
                    sources = []

            gaps.append(
                ResourceGapItem(
                    item_id=ingredient.item_id,
                    item_name=ingredient.item.name if ingredient.item else None,
                    required_quantity=float(ingredient.required_quantity),
                    available_quantity=float(available),
                    gap_quantity=float(gap),
                    sources=sources,
                )
            )

        # Sort gaps by gap quantity (largest gaps first)
        gaps.sort(key=lambda g: g.gap_quantity, reverse=True)

        total_gaps = len([g for g in gaps if g.gap_quantity > 0])
        can_proceed = all(g.gap_quantity <= 0 or len(g.sources) > 0 for g in gaps)

        return ResourceGapResponse(
            craft_id=craft_id,
            craft_status=craft.status,
            blueprint_name=blueprint.name if blueprint else None,
            gaps=gaps,
            total_gaps=total_gaps,
            can_proceed=can_proceed,
        )

    def _get_accessible_location_ids(self, organization_id: Optional[str]) -> List[str]:
        """
        Get list of location IDs accessible to the current user.

        Includes:
        - User-owned locations
        - Organization-owned locations (if user is a member)

        Args:
            organization_id: Optional organization ID to filter by

        Returns:
            List of location UUIDs
        """
        location_ids = []

        # User-owned locations
        user_locations = (
            self.db.query(Location)
            .filter(
                Location.owner_type == "user",
                Location.owner_id == self.current_user_id,
            )
            .all()
        )
        location_ids.extend([loc.id for loc in user_locations])

        # Organization-owned locations
        org_ids = []
        if organization_id:
            # Check if user is member of specified organization
            membership = (
                self.db.query(OrganizationMember)
                .filter(
                    OrganizationMember.organization_id == organization_id,
                    OrganizationMember.user_id == self.current_user_id,
                )
                .first()
            )
            if membership:
                org_ids.append(organization_id)
        else:
            # Get all organizations user is a member of
            memberships = (
                self.db.query(OrganizationMember)
                .filter(OrganizationMember.user_id == self.current_user_id)
                .all()
            )
            org_ids = [m.organization_id for m in memberships]

        if org_ids:
            org_locations = (
                self.db.query(Location)
                .filter(
                    Location.owner_type == "organization",
                    Location.owner_id.in_(org_ids),
                )
                .all()
            )
            location_ids.extend([loc.id for loc in org_locations])

        return location_ids
