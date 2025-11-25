# Test Fixtures

This directory contains reusable test data fixtures for the SCIMS test suite.

## Overview

Test fixtures are defined in `conftest.py` and provide reusable test data that can be used across multiple test files. This ensures consistency and reduces code duplication.

## Available Fixtures

### User Fixtures

- **`test_user`**: Creates a basic test user with email `testuser@example.com`
- **`other_user`**: Creates a second test user with email `otheruser@example.com`
- **`auth_headers`**: Returns authentication headers for `test_user`

### Organization Fixtures

- **`test_organization`**: Creates a test organization with `test_user` as owner
- **`test_org_location`**: Creates a location owned by `test_organization`

### Item & Inventory Fixtures

- **`test_items`**: Creates a set of 4 test items (Iron Ore, Steel Ingot, Component A, Component B)
- **`test_location`**: Creates a user-owned location (Test Station)
- **`test_item_stocks`**: Creates item stocks for all test items at test_location with 100.0 quantity each

### Blueprint & Craft Fixtures

- **`test_blueprint`**: Creates a private blueprint that produces Steel Ingot from Iron Ore
- **`test_public_blueprint`**: Creates a public blueprint for sharing
- **`test_craft`**: Creates a planned craft from `test_blueprint`

### Integration Fixtures

- **`test_integration`**: Creates a test webhook integration

## Usage Example

```python
def test_something(client, test_user, test_organization, test_items):
    """Example test using multiple fixtures."""
    # test_user, test_organization, and test_items are automatically available
    response = client.get("/api/v1/items", headers=auth_headers)
    assert response.status_code == 200
```

## Database Session

All fixtures use the `db_session` fixture which provides a fresh database session for each test. The database is automatically cleaned up after each test.

## Creating Custom Fixtures

When creating new fixtures:

1. Add them to `conftest.py`
2. Use `@pytest.fixture` decorator
3. Accept `db_session` as a parameter if database access is needed
4. Use other fixtures as dependencies if needed
5. Document the fixture in this README

Example:

```python
@pytest.fixture
def custom_fixture(test_user, db_session):
    """Create a custom test fixture."""
    # Create test data
    item = Item(name="Custom Item", category="Test")
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item
```

