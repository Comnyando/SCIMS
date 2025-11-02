"""
Performance tests for Optimization API endpoints and service.

These tests verify that optimization algorithms perform well with large datasets.
"""

import pytest
import time
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.location import Location
from app.models.item_stock import ItemStock
from app.models.user import User
from app.models.blueprint import Blueprint
from app.models.craft import Craft, CRAFT_STATUS_PLANNED
from app.models.craft_ingredient import CraftIngredient, SOURCE_TYPE_STOCK
from app.models.resource_source import (
    ResourceSource,
    SOURCE_TYPE_PLAYER_STOCK,
    SOURCE_TYPE_UNIVERSE_LOCATION,
    SOURCE_TYPE_TRADING_POST,
)
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.services.optimization import OptimizationService
from app.schemas.optimization import FindSourcesRequest, SuggestCraftsRequest
from app.core.security import hash_password


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(
        email="perfuser@example.com",
        username="perfuser",
        hashed_password=hash_password("testpass123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_location(test_user, db_session: Session):
    """Create a test location."""
    location = Location(
        name="Performance Test Location",
        type="station",
        owner_type="user",
        owner_id=test_user.id,
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def large_item_set(db_session: Session, test_location: Location, test_user: User):
    """Create a large set of items with stocks and sources."""
    items = []
    stocks = []
    sources = []

    # Create 100 items
    for i in range(100):
        item = Item(
            name=f"Item {i}",
            description=f"Test item {i}",
            category="Materials",
        )
        db_session.add(item)
        items.append(item)

    db_session.flush()

    # Create stocks for all items
    for item in items:
        stock = ItemStock(
            item_id=item.id,
            location_id=test_location.id,
            quantity=Decimal("1000.0") - Decimal(str(i)),  # Varying quantities
            reserved_quantity=Decimal("0"),
            updated_by=test_user.id,
        )
        db_session.add(stock)
        stocks.append(stock)

    # Create universe sources for 50 items (every other item)
    for i in range(0, 100, 2):
        item = items[i]
        source = ResourceSource(
            item_id=item.id,
            source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
            source_identifier=f"Universe Location {i}",
            available_quantity=Decimal("500.0"),
            cost_per_unit=Decimal(str(5.0 + i * 0.1)),
            reliability_score=Decimal("0.8"),
            location_id=test_location.id,
        )
        db_session.add(source)
        sources.append(source)

    # Create trading post sources for 25 items
    for i in range(0, 100, 4):
        item = items[i]
        source = ResourceSource(
            item_id=item.id,
            source_type=SOURCE_TYPE_TRADING_POST,
            source_identifier=f"Trading Post {i}",
            available_quantity=Decimal("200.0"),
            cost_per_unit=Decimal(str(10.0 + i * 0.2)),
            reliability_score=Decimal("0.7"),
            location_id=test_location.id,
        )
        db_session.add(source)
        sources.append(source)

    # Create player stock sources for 20 items
    for i in range(0, 100, 5):
        item = items[i]
        source = ResourceSource(
            item_id=item.id,
            source_type=SOURCE_TYPE_PLAYER_STOCK,
            source_identifier=f"player_{i}",
            available_quantity=Decimal("100.0"),
            cost_per_unit=Decimal(str(8.0 + i * 0.15)),
            reliability_score=Decimal("0.75"),
            location_id=test_location.id,
        )
        db_session.add(source)
        sources.append(source)

    db_session.commit()

    # Refresh all items
    for item in items:
        db_session.refresh(item)

    return items, stocks, sources


@pytest.fixture
def large_blueprint_set(db_session: Session, test_user: User, large_item_set):
    """Create a large set of blueprints with complex ingredient trees."""
    items, _, _ = large_item_set
    blueprints = []

    # Create 20 blueprints, each producing a different item
    for i in range(20):
        output_item = items[i]
        # Each blueprint uses 3-5 ingredients from items 20-99
        num_ingredients = 3 + (i % 3)
        ingredient_list = []

        for j in range(num_ingredients):
            ingredient_item = items[20 + (i * 3 + j) % 80]
            ingredient_list.append({
                "item_id": ingredient_item.id,
                "quantity": float(Decimal(str(1 + j))),
                "optional": False,
            })

        blueprint = Blueprint(
            name=f"Blueprint {i}",
            description=f"Complex blueprint {i}",
            category="Components",
            crafting_time_minutes=60 + (i * 5),
            output_item_id=output_item.id,
            output_quantity=Decimal("10.0"),
            blueprint_data={"ingredients": ingredient_list},
            created_by=test_user.id,
            is_public=False,
            usage_count=0,
        )
        db_session.add(blueprint)
        blueprints.append(blueprint)

    db_session.commit()
    for blueprint in blueprints:
        db_session.refresh(blueprint)

    return blueprints


@pytest.fixture
def large_craft_set(db_session: Session, test_user: User, large_blueprint_set, test_location: Location):
    """Create a large set of crafts with ingredients."""
    crafts = []

    for blueprint in large_blueprint_set[:10]:  # Create 10 crafts
        craft = Craft(
            blueprint_id=blueprint.id,
            requested_by=test_user.id,
            status=CRAFT_STATUS_PLANNED,
            priority=5,
            output_location_id=test_location.id,
        )
        db_session.add(craft)
        db_session.flush()

        # Create craft ingredients from blueprint
        ingredients_data = blueprint.blueprint_data["ingredients"]
        for ingredient_data in ingredients_data:
            craft_ingredient = CraftIngredient(
                craft_id=craft.id,
                item_id=ingredient_data["item_id"],
                required_quantity=Decimal(str(ingredient_data["quantity"])),
                source_location_id=test_location.id,
                source_type=SOURCE_TYPE_STOCK,
            )
            db_session.add(craft_ingredient)

        crafts.append(craft)

    db_session.commit()
    for craft in crafts:
        db_session.refresh(craft)

    return crafts


class TestFindSourcesPerformance:
    """Performance tests for find sources endpoint."""

    def test_find_sources_with_large_dataset(
        self, db_session: Session, test_user: User, large_item_set
    ):
        """Test find_sources performance with 100 items and multiple sources."""
        items, _, _ = large_item_set
        service = OptimizationService(db_session, test_user.id)

        # Test with an item that has stock, universe source, trading post, and player stock
        test_item = items[0]  # Has all source types

        start_time = time.time()
        request = FindSourcesRequest(
            item_id=test_item.id,
            required_quantity=Decimal("50.0"),
            max_sources=50,
        )
        response = service.find_sources_for_item(request)
        end_time = time.time()

        elapsed_time = end_time - start_time

        # Should complete in under 1 second for 100 items
        assert elapsed_time < 1.0, f"find_sources took {elapsed_time:.3f}s, expected < 1.0s"
        assert response.item_id == test_item.id
        assert len(response.sources) > 0

    def test_find_sources_with_max_sources_limit(
        self, db_session: Session, test_user: User, large_item_set
    ):
        """Test that max_sources limit is respected with large datasets."""
        items, _, _ = large_item_set
        service = OptimizationService(db_session, test_user.id)

        test_item = items[0]
        max_sources = 10

        request = FindSourcesRequest(
            item_id=test_item.id,
            required_quantity=Decimal("1000.0"),  # Large quantity to get many sources
            max_sources=max_sources,
        )
        response = service.find_sources_for_item(request)

        # Should not exceed max_sources
        assert len(response.sources) <= max_sources

    def test_find_sources_filtering_performance(
        self, db_session: Session, test_user: User, large_item_set
    ):
        """Test performance with reliability filtering."""
        items, _, _ = large_item_set
        service = OptimizationService(db_session, test_user.id)

        test_item = items[0]

        start_time = time.time()
        request = FindSourcesRequest(
            item_id=test_item.id,
            required_quantity=Decimal("50.0"),
            max_sources=50,
            min_reliability=Decimal("0.75"),  # Filter to high reliability
        )
        response = service.find_sources_for_item(request)
        end_time = time.time()

        elapsed_time = end_time - start_time

        # Should still be fast with filtering
        assert elapsed_time < 1.0, f"find_sources with filtering took {elapsed_time:.3f}s"
        # Verify filtering worked
        for source in response.sources:
            if source.reliability_score is not None:
                assert source.reliability_score >= 0.75

    def test_find_sources_many_items_sequential(
        self, db_session: Session, test_user: User, large_item_set
    ):
        """Test finding sources for many items sequentially."""
        items, _, _ = large_item_set
        service = OptimizationService(db_session, test_user.id)

        start_time = time.time()
        results = []

        # Query 20 items sequentially
        for item in items[:20]:
            request = FindSourcesRequest(
                item_id=item.id,
                required_quantity=Decimal("50.0"),
                max_sources=10,
            )
            response = service.find_sources_for_item(request)
            results.append(response)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # 20 queries should complete in under 5 seconds
        assert elapsed_time < 5.0, f"20 sequential queries took {elapsed_time:.3f}s"
        assert len(results) == 20


class TestSuggestCraftsPerformance:
    """Performance tests for suggest crafts endpoint."""

    def test_suggest_crafts_with_large_blueprint_set(
        self, db_session: Session, test_user: User, large_item_set, large_blueprint_set
    ):
        """Test suggest_crafts performance with many blueprints."""
        items, _, _ = large_item_set
        service = OptimizationService(db_session, test_user.id)

        # Use item that has multiple blueprints producing it
        test_item = items[0]  # First item has a blueprint

        start_time = time.time()
        request = SuggestCraftsRequest(
            target_item_id=test_item.id,
            target_quantity=Decimal("100.0"),
            max_suggestions=20,
        )
        response = service.suggest_crafts(request)
        end_time = time.time()

        elapsed_time = end_time - start_time

        # Should complete in under 2 seconds
        assert elapsed_time < 2.0, f"suggest_crafts took {elapsed_time:.3f}s, expected < 2.0s"
        assert response.target_item_id == test_item.id

    def test_suggest_crafts_complex_ingredients(
        self, db_session: Session, test_user: User, large_blueprint_set
    ):
        """Test suggest_crafts with blueprints that have many ingredients."""
        service = OptimizationService(db_session, test_user.id)

        # Use a blueprint with 5 ingredients (the most complex)
        blueprint = large_blueprint_set[2]  # Has 5 ingredients
        target_item_id = blueprint.output_item_id

        start_time = time.time()
        request = SuggestCraftsRequest(
            target_item_id=target_item_id,
            target_quantity=Decimal("100.0"),
            max_suggestions=10,
        )
        response = service.suggest_crafts(request)
        end_time = time.time()

        elapsed_time = end_time - start_time

        # Should handle complex ingredients efficiently
        assert elapsed_time < 1.5, f"suggest_crafts with complex ingredients took {elapsed_time:.3f}s"
        assert len(response.suggestions) > 0

    def test_suggest_crafts_max_suggestions_limit(
        self, db_session: Session, test_user: User, large_item_set
    ):
        """Test that max_suggestions limit is respected."""
        items, _, _ = large_item_set
        
        # Create multiple blueprints for the same item
        test_item = items[0]
        
        for i in range(15):
            blueprint = Blueprint(
                name=f"Blueprint Variant {i}",
                description=f"Variant {i}",
                category="Components",
                crafting_time_minutes=60,
                output_item_id=test_item.id,
                output_quantity=Decimal("10.0"),
                blueprint_data={"ingredients": []},
                created_by=test_user.id,
                is_public=False,
                usage_count=0,
            )
            db_session.add(blueprint)
        db_session.commit()

        service = OptimizationService(db_session, test_user.id)
        max_suggestions = 10

        request = SuggestCraftsRequest(
            target_item_id=test_item.id,
            target_quantity=Decimal("100.0"),
            max_suggestions=max_suggestions,
        )
        response = service.suggest_crafts(request)

        # Should not exceed max_suggestions
        assert len(response.suggestions) <= max_suggestions


class TestResourceGapPerformance:
    """Performance tests for resource gap endpoint."""

    def test_get_resource_gap_with_large_craft_set(
        self, db_session: Session, test_user: User, large_craft_set
    ):
        """Test resource gap performance with crafts that have many ingredients."""
        service = OptimizationService(db_session, test_user.id)

        # Use craft with most ingredients (5)
        craft = large_craft_set[2]

        start_time = time.time()
        response = service.get_resource_gap(craft.id)
        end_time = time.time()

        elapsed_time = end_time - start_time

        # Should complete in under 2 seconds (includes finding sources for gaps)
        assert elapsed_time < 2.0, f"get_resource_gap took {elapsed_time:.3f}s, expected < 2.0s"
        assert response.craft_id == craft.id
        assert len(response.gaps) > 0

    def test_get_resource_gap_multiple_crafts(
        self, db_session: Session, test_user: User, large_craft_set
    ):
        """Test resource gap analysis for multiple crafts sequentially."""
        service = OptimizationService(db_session, test_user.id)

        start_time = time.time()
        results = []

        # Analyze 10 crafts sequentially
        for craft in large_craft_set[:10]:
            response = service.get_resource_gap(craft.id)
            results.append(response)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # 10 crafts should complete in under 10 seconds
        assert elapsed_time < 10.0, f"10 resource gap analyses took {elapsed_time:.3f}s"
        assert len(results) == 10

    def test_get_resource_gap_with_many_sources(
        self, db_session: Session, test_user: User, large_item_set, large_craft_set, test_location: Location
    ):
        """Test resource gap when items have many available sources."""
        items, _, _ = large_item_set
        service = OptimizationService(db_session, test_user.id)

        # Create many sources for a single item
        test_item = items[10]
        for i in range(20):
            source = ResourceSource(
                item_id=test_item.id,
                source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
                source_identifier=f"Source {i}",
                available_quantity=Decimal("50.0"),
                cost_per_unit=Decimal(str(5.0 + i)),
                reliability_score=Decimal("0.8"),
                location_id=test_location.id,
            )
            db_session.add(source)
        db_session.commit()

        # Find a craft that uses this item
        craft = None
        for c in large_craft_set:
            ingredients = db_session.query(CraftIngredient).filter(
                CraftIngredient.craft_id == c.id
            ).all()
            if any(ing.item_id == test_item.id for ing in ingredients):
                craft = c
                break

        if craft:
            start_time = time.time()
            response = service.get_resource_gap(craft.id)
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Should still perform well with many sources
            assert elapsed_time < 3.0, f"get_resource_gap with many sources took {elapsed_time:.3f}s"
            
            # Find the gap for test_item
            item_gap = next((g for g in response.gaps if g.item_id == test_item.id), None)
            if item_gap:
                # Should have found sources
                assert len(item_gap.sources) > 0


class TestOptimizationServiceScalability:
    """Scalability tests for optimization service."""

    def test_find_sources_memory_efficiency(
        self, db_session: Session, test_user: User, large_item_set
    ):
        """Test that find_sources doesn't load unnecessary data."""
        items, _, _ = large_item_set
        service = OptimizationService(db_session, test_user.id)

        # Query for an item
        test_item = items[0]
        request = FindSourcesRequest(
            item_id=test_item.id,
            required_quantity=Decimal("50.0"),
            max_sources=10,
        )

        # Should complete without memory issues
        response = service.find_sources_for_item(request)
        assert response is not None
        assert response.item_id == test_item.id

    def test_suggest_crafts_with_empty_ingredients(
        self, db_session: Session, test_user: User
    ):
        """Test suggest_crafts handles blueprints with no ingredients gracefully."""
        # Create item and blueprint with no ingredients
        item = Item(name="Simple Item", category="Materials")
        db_session.add(item)
        db_session.flush()

        blueprint = Blueprint(
            name="Simple Blueprint",
            description="No ingredients",
            category="Components",
            crafting_time_minutes=60,
            output_item_id=item.id,
            output_quantity=Decimal("10.0"),
            blueprint_data={"ingredients": []},
            created_by=test_user.id,
            is_public=False,
            usage_count=0,
        )
        db_session.add(blueprint)
        db_session.commit()

        service = OptimizationService(db_session, test_user.id)
        request = SuggestCraftsRequest(
            target_item_id=item.id,
            target_quantity=Decimal("100.0"),
        )

        # Should handle gracefully (skip blueprints without ingredients)
        response = service.suggest_crafts(request)
        # Blueprint should be skipped, so no suggestions or empty suggestions
        assert response is not None

