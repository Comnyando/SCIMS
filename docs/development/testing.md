# Testing Guide

This document describes the testing strategy, procedures, and best practices for the SCIMS backend.

## Overview

The SCIMS backend uses **pytest** as the testing framework with a target of **>80% code coverage**. The test suite includes unit tests, integration tests, and end-to-end flow tests.

## Test Structure

```
backend/tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── test_auth.py             # Authentication tests
├── test_items.py            # Items API tests
├── test_inventory.py        # Inventory API tests
├── test_locations.py        # Locations API tests
├── test_ships.py            # Ships API tests
├── test_blueprints.py      # Blueprints API tests
├── test_crafts.py           # Crafts API tests
├── test_goals.py            # Goals API tests
├── test_sources.py           # Resource sources tests
├── test_optimization.py     # Optimization engine tests
├── test_analytics.py        # Analytics tests
├── test_integrations.py     # Integration framework tests
├── test_import_export.py    # Import/export tests
├── test_commons.py         # Public commons tests
├── test_integration_flows.py # End-to-end flow tests
└── fixtures/               # Test data fixtures (if needed)
    └── README.md
```

## Running Tests

### Run All Tests

```bash
cd backend
pytest tests/
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html
```

This generates:
- Terminal output with coverage percentages
- HTML report in `htmlcov/index.html`

### Run Specific Test File

```bash
pytest tests/test_auth.py
```

### Run Specific Test

```bash
pytest tests/test_auth.py::TestUserRegistration::test_register_new_user
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run Tests in Parallel

```bash
pytest tests/ -n auto
```

(Requires `pytest-xdist`)

## Test Database

Tests use an **in-memory SQLite database** (`sqlite:///:memory:`) to ensure:
- Fast test execution
- Isolation between tests
- No external dependencies
- Automatic cleanup

The database is recreated for each test function, ensuring complete isolation.

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- **`db_session`**: Fresh database session for each test
- **`client`**: FastAPI test client with database override
- **`test_user`**: Basic test user
- **`other_user`**: Second test user
- **`auth_headers`**: Authentication headers for test_user
- **`test_organization`**: Test organization with test_user as owner
- **`test_items`**: Set of test items
- **`test_location`**: User-owned location
- **`test_blueprint`**: Test blueprint
- **`test_craft`**: Test craft

See `tests/fixtures/README.md` for complete fixture documentation.

## Writing Tests

### Unit Tests

Unit tests focus on individual functions and classes:

```python
def test_hash_password():
    """Test that passwords are hashed correctly."""
    password = "testpass123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert hashed.startswith("$argon2")
```

### API Endpoint Tests

API tests verify endpoint behavior:

```python
def test_create_item_success(client, auth_headers):
    """Test successful item creation."""
    response = client.post(
        "/api/v1/items",
        headers=auth_headers,
        json={
            "name": "Test Item",
            "category": "Test",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
```

### Integration Tests

Integration tests verify interactions between components:

```python
def test_craft_creation_with_reservation(client, auth_headers, test_blueprint, test_location, test_item_stocks):
    """Test creating craft with ingredient reservation."""
    response = client.post(
        "/api/v1/crafts?reserve_ingredients=true",
        headers=auth_headers,
        json={
            "blueprint_id": test_blueprint.id,
            "output_location_id": test_location.id,
        },
    )
    
    assert response.status_code == 201
    # Verify ingredients were reserved
    # ...
```

### End-to-End Flow Tests

E2E tests verify complete user workflows:

```python
def test_complete_user_to_craft_flow(client, db_session):
    """Test: User registration → org creation → inventory → craft."""
    # Step 1: User Registration
    # Step 2: Create Organization
    # Step 3: Create Items
    # Step 4: Create Location
    # Step 5: Add Inventory
    # Step 6: Create Blueprint
    # Step 7: Create Craft
    # Step 8: Start Craft
    # Step 9: Complete Craft
    # Step 10: Verify Results
```

See `test_integration_flows.py` for complete examples.

## Test Coverage

### Current Coverage

Run coverage report:

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

Current target: **>80% coverage**

### Coverage Exclusions

The following are excluded from coverage:
- Test files (`tests/`)
- Migration files (`alembic/`)
- Type checking blocks (`if TYPE_CHECKING:`)
- Repr methods (`def __repr__`)
- Error assertions (`raise AssertionError`)

### Improving Coverage

1. Identify low-coverage areas from the coverage report
2. Write tests for untested code paths
3. Focus on edge cases and error handling
4. Test both success and failure scenarios

## Best Practices

### 1. Test Isolation

Each test should be independent and not rely on other tests:

```python
# Good: Each test creates its own data
def test_create_item(client, auth_headers):
    response = client.post("/api/v1/items", ...)
    # ...

# Bad: Relies on previous test
def test_update_item(client, auth_headers):
    # Assumes item from previous test exists
    response = client.patch("/api/v1/items/123", ...)
```

### 2. Use Fixtures

Reuse fixtures instead of duplicating setup code:

```python
# Good: Use fixtures
def test_something(client, test_user, test_items):
    # ...

# Bad: Duplicate setup
def test_something(client, db_session):
    user = User(...)
    db_session.add(user)
    # ...
```

### 3. Test Both Success and Failure

Test both happy paths and error cases:

```python
def test_create_item_success(client, auth_headers):
    # Test successful creation
    ...

def test_create_item_duplicate_name(client, auth_headers):
    # Test duplicate name error
    ...

def test_create_item_unauthorized(client):
    # Test authentication required
    ...
```

### 4. Use Descriptive Test Names

Test names should clearly describe what is being tested:

```python
# Good
def test_create_item_with_duplicate_name_fails(client, auth_headers):
    ...

# Bad
def test_item1(client, auth_headers):
    ...
```

### 5. Arrange-Act-Assert Pattern

Structure tests clearly:

```python
def test_example(client, auth_headers):
    # Arrange: Set up test data
    item_data = {"name": "Test Item", "category": "Test"}
    
    # Act: Perform the action
    response = client.post("/api/v1/items", headers=auth_headers, json=item_data)
    
    # Assert: Verify the result
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"
```

### 6. Test Edge Cases

Include tests for:
- Empty inputs
- Invalid inputs
- Boundary conditions
- Missing data
- Permission errors

## Critical Test Flows

The following critical flows are tested in `test_integration_flows.py`:

1. **User Registration → Org Creation → Inventory → Craft**
   - Complete workflow from user signup to craft completion
   - Verifies data flow and state changes

2. **Recipe Sharing → Craft Planning → Execution**
   - Public blueprint sharing
   - Cross-user blueprint usage
   - Craft execution with shared recipes

3. **Integration Setup → Data Import**
   - Integration creation and configuration
   - Data export
   - Data import and validation

## Continuous Integration

Tests run automatically on:
- Every push to `main` and `develop` branches
- Every pull request

See `.github/workflows/ci.yml` for CI configuration.

## Troubleshooting

### Tests Failing Locally

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. Check database migrations are up to date:
   ```bash
   alembic upgrade head
   ```

3. Clear pytest cache:
   ```bash
   pytest --cache-clear
   ```

### Slow Tests

- Use `-n auto` for parallel execution (requires `pytest-xdist`)
- Check for unnecessary database queries
- Use fixtures instead of creating data in each test

### Coverage Not Updating

- Ensure `--cov=app` flag is used
- Check that source files are in the `app/` directory
- Verify exclusions in `pyproject.toml` are correct

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/core/testing.html)

