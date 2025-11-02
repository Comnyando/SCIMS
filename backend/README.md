# SCIMS Backend

FastAPI-based backend for the Star Citizen Inventory Management System.

## Technology Stack

- **Framework:** FastAPI 0.115+
- **Python:** 3.11+
- **Database:** PostgreSQL 15+ with SQLAlchemy 2.0 ORM
- **Caching/Queue:** Redis 7+ with Celery 5.4
- **Migrations:** Alembic
- **Validation:** Pydantic 2.9
- **Server:** Uvicorn (ASGI)

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)
- pip or poetry for dependency management

## Development Setup

### Using Docker (Recommended)

The backend runs automatically when you start the Docker Compose stack:

```bash
docker compose up backend
```

The backend will be available at `http://localhost:8000` and auto-reloads on code changes.

### Local Setup (Without Docker)

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp ../.env.example .env
   # Edit .env with your local database and Redis settings
   ```

4. **Ensure PostgreSQL and Redis are running:**
   - PostgreSQL should be accessible at the `DATABASE_URL` from your `.env`
   - Redis should be accessible at the `REDIS_URL` from your `.env`

5. **Run database migrations:**
   ```bash
   # Apply all pending migrations
   alembic upgrade head
   
   # (Optional) Seed the database with test data
   python scripts/seed_data.py
   
   # (Optional) Create developer user with admin permissions (LOCAL ONLY)
   python scripts/create_dev_user.py
   ```

6. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Environment Variables

Key environment variables (see `.env.example` for complete list):

```env
# Database
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/scims

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
JWT_ALGORITHM=HS256

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Settings and configuration
│   ├── database.py          # Database connection and session management
│   ├── models/              # SQLAlchemy database models
│   ├── schemas/             # Pydantic schemas for validation
│   ├── services/            # Business logic layer
│   └── fazer/               # Future feature modules
├── alembic/                 # Database migration scripts
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
└── Dockerfile               # Docker build configuration
```

## Running the Backend

### Development Mode

```bash
# With Docker
docker compose up backend

# Local
uvicorn app.main:app --reload
```

### Production Mode

```bash
# With Docker
docker compose -f ../docker-compose.prod.yml up backend

# Local
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

When the backend is running, interactive documentation is available:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Database Management

### Running Migrations

The project uses Alembic for database migrations. All migration files are stored in `alembic/versions/`.

#### Initial Setup

**Option 1: Using Docker (Recommended)**

1. **Ensure Docker containers are running:**
   ```bash
   docker compose up -d db
   ```

2. **Apply all migrations:**
   ```bash
   # From project root
   docker compose exec backend alembic upgrade head
   
   # Or use the helper script (PowerShell)
   .\backend\scripts\run_migrations.ps1 upgrade head
   
   # Or use the helper script (Bash)
   ./backend/scripts/run_migrations.sh upgrade head
   ```
   
   **Note:** If you get "alembic: command not found", rebuild the container:
   ```bash
   docker compose build backend
   ```

3. **(Optional) Seed test data:**
   ```bash
   docker compose exec backend python scripts/seed_data.py
   ```

4. **(Optional) Create developer user (LOCAL DEVELOPMENT ONLY):**
   ```bash
   # Using PowerShell (Windows)
   .\backend\scripts\create_dev_user.ps1
   
   # Using bash (Linux/Mac)
   ./backend/scripts/create_dev_user.sh
   
   # Or directly
   docker compose exec backend python -m scripts.create_dev_user
   ```
   
   This creates a developer account:
   - **Email:** `dev@scims.local`
   - **Username:** `dev`
   - **Password:** `dev123`
   - **Status:** Active & Verified
   - **Permissions:** Owner of all organizations
   
   **⚠️ WARNING:** This script only works in development environment and should NEVER be run in production!

**Option 2: Local Development**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Apply all migrations:**
   ```bash
   alembic upgrade head
   ```

3. **(Optional) Seed test data:**
   ```bash
   python scripts/seed_data.py
   ```
   
This creates:
- 4 test users (admin, owner, member, viewer)
- 2 test organizations
- Sample memberships

#### Common Migration Commands

**Using Docker:**
```bash
# Apply all pending migrations
docker compose exec backend alembic upgrade head

# Create a new migration (after modifying models)
docker compose exec backend alembic revision --autogenerate -m "Description of changes"

# View migration history
docker compose exec backend alembic history

# Show current database revision
docker compose exec backend alembic current

# Rollback one migration
docker compose exec backend alembic downgrade -1

# Or use helper scripts (from project root):
.\backend\scripts\run_migrations.ps1 upgrade head
.\backend\scripts\run_migrations.ps1 current
.\backend\scripts\run_migrations.ps1 history
```

**Note:** If you get "alembic: command not found", the container needs to be rebuilt to include Alembic:
```bash
docker compose build backend
```

**Local Development:**
```bash
# Create a new migration (after modifying models)
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Apply migrations to a specific revision
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# View migration history
alembic history

# Show current database revision
alembic current

# Show pending migrations
alembic heads
```

#### Creating Migrations

After modifying SQLAlchemy models:

1. **Auto-generate migration:**
   ```bash
   alembic revision --autogenerate -m "Add new field to User model"
   ```

2. **Review the generated migration** in `alembic/versions/`:
   - Check that all changes are correct
   - Add data migrations if needed (e.g., backfilling new fields)
   - Ensure downgrade() properly reverses the changes

3. **Test the migration:**
   ```bash
   # Apply migration
   alembic upgrade head
   
   # Test rollback
   alembic downgrade -1
   
   # Re-apply
   alembic upgrade head
   ```

#### Migration Best Practices

- **Never edit existing migration files** that have been applied to production
- **Always test migrations** up and down before committing
- **Review auto-generated migrations** - Alembic may not detect all changes
- **Use descriptive migration messages** that explain what changed and why
- **Include data migrations** if schema changes require data transformations

### Database Connection & Connection Pooling

The database connection is managed in `app/database.py` using SQLAlchemy 2.0 with connection pooling.

**Connection Pool Configuration:**
- `pool_size`: 5 connections (maintained in pool)
- `max_overflow`: 10 additional connections (beyond pool_size)
- `pool_timeout`: 30 seconds (wait time for connection)
- `pool_recycle`: 3600 seconds (recycle connections after 1 hour)
- `pool_pre_ping`: Enabled (verify connections before use)

These settings balance performance and resource usage. They can be adjusted in `app/database.py` or made configurable via environment variables in the future.

**Using Database Sessions in FastAPI:**

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

### Seeding Development Data

The seed script (`scripts/seed_data.py`) creates sample data for development:

**Test Users:**
- `admin@scims.test` / `admin123` (admin role)
- `owner@scims.test` / `owner123` (owner role)
- `member@scims.test` / `member123` (member role)
- `viewer@scims.test` / `viewer123` (viewer role)

**Test Organizations:**
- Test Organization (slug: `test-org`)
- Another Organization (slug: `another-org`)

Run the seed script:
```bash
python scripts/seed_data.py
```

**Note:** The seed script is idempotent - it will skip existing records, so it's safe to run multiple times.

### Creating a Developer User

For local development, you can create a dedicated developer user with full admin permissions:

```bash
# From project root using helper script (PowerShell)
.\backend\scripts\create_dev_user.ps1

# From project root using helper script (bash)
./backend/scripts/create_dev_user.sh

# Or directly in Docker container
docker compose exec backend python -m scripts.create_dev_user

# Or locally (if running without Docker)
python backend/scripts/create_dev_user.py
```

**Developer Account Credentials:**
- **Email:** `dev@scims.local`
- **Username:** `dev`
- **Password:** `dev123`

**Permissions:**
- Active and verified account
- Owner role in all existing organizations
- Owner role in automatically created "Developer Organization"

**⚠️ IMPORTANT NOTES:**
- This script **ONLY runs in development environment** - it will refuse to run in production
- The script is idempotent - safe to run multiple times (will update existing user if needed)
- The developer user will be added as owner to all existing and future organizations
- This user is intended for local development only and should never exist in production databases

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Common Development Tasks

### Adding a New API Endpoint

1. Create or update schema in `app/schemas/`
2. Add endpoint in `app/main.py` or appropriate router module
3. Add business logic in `app/services/` if needed
4. Update API documentation tags and descriptions

Example:
```python
from fastapi import APIRouter
from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter(prefix="/api/v1/items", tags=["items"])

@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    # Implementation
    pass
```

### Creating Database Models

1. Create model in `app/models/`
2. Create corresponding Pydantic schemas in `app/schemas/`
3. Generate migration: `alembic revision --autogenerate -m "Add Item model"`
4. Review and apply migration: `alembic upgrade head`

### Adding Environment Variables

1. Add variable to `app/config.py` Settings class
2. Update `.env.example` with the new variable
3. Document in this README if needed

## API Endpoint Examples

### Inventory API

The inventory API provides endpoints for managing stock levels, transfers, and reservations.

#### List Inventory

Get inventory stock levels with optional filters:

```bash
# List all inventory (with pagination)
GET /api/v1/inventory?skip=0&limit=50

# Filter by item ID
GET /api/v1/inventory?item_id=550e8400-e29b-41d4-a716-446655440000

# Filter by location ID
GET /api/v1/inventory?location_id=550e8400-e29b-41d4-a716-446655440000

# Search by item name
GET /api/v1/inventory?search=quantum

# Combined filters
GET /api/v1/inventory?item_id=550e8400-e29b-41d4-a716-446655440000&location_id=550e8400-e29b-41d4-a716-446655440000&skip=0&limit=50
```

**Response:**
```json
{
  "items": [
    {
      "item_id": "550e8400-e29b-41d4-a716-446655440000",
      "location_id": "660e8400-e29b-41d4-a716-446655440000",
      "quantity": 100,
      "reserved_quantity": 25,
      "available_quantity": 75,
      "item_name": "Quantum Fuel",
      "item_category": "Consumables",
      "location_name": "New Babbage Landing Zone",
      "location_type": "station",
      "last_updated": "2024-01-01T12:00:00Z",
      "updated_by_username": "admin"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50,
  "pages": 1
}
```

#### Adjust Inventory

Add or remove items from inventory:

```bash
POST /api/v1/inventory/adjust
Content-Type: application/json
Authorization: Bearer <token>

{
  "item_id": "550e8400-e29b-41d4-a716-446655440000",
  "location_id": "660e8400-e29b-41d4-a716-446655440000",
  "quantity_change": 10,
  "notes": "Restocked from trading post"
}
```

**Positive `quantity_change`** adds items, **negative** removes items.

**Response:**
```json
{
  "item_id": "550e8400-e29b-41d4-a716-446655440000",
  "location_id": "660e8400-e29b-41d4-a716-446655440000",
  "quantity": 110,
  "reserved_quantity": 25,
  "available_quantity": 85,
  "item_name": "Quantum Fuel",
  "item_category": "Consumables",
  "location_name": "New Babbage Landing Zone",
  "location_type": "station",
  "last_updated": "2024-01-01T12:05:00Z",
  "updated_by_username": "admin"
}
```

#### Transfer Items

Move items between locations:

```bash
POST /api/v1/inventory/transfer
Content-Type: application/json
Authorization: Bearer <token>

{
  "item_id": "550e8400-e29b-41d4-a716-446655440000",
  "from_location_id": "660e8400-e29b-41d4-a716-446655440000",
  "to_location_id": "770e8400-e29b-41d4-a716-446655440000",
  "quantity": 50,
  "notes": "Moving to ship cargo"
}
```

**Response:**
```json
{
  "message": "Successfully transferred 50 items",
  "from_location": {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "name": "New Babbage Landing Zone",
    "quantity": 60,
    "available_quantity": 35
  },
  "to_location": {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "name": "Ship Cargo Bay",
    "quantity": 50,
    "available_quantity": 50
  }
}
```

#### Reserve Stock

Reserve items for planned operations (e.g., crafting):

```bash
POST /api/v1/inventory/reserve
Content-Type: application/json
Authorization: Bearer <token>

{
  "item_id": "550e8400-e29b-41d4-a716-446655440000",
  "location_id": "660e8400-e29b-41d4-a716-446655440000",
  "quantity": 30
}
```

**Response:** Updated inventory stock with increased `reserved_quantity`.

#### Unreserve Stock

Release previously reserved items:

```bash
POST /api/v1/inventory/unreserve
Content-Type: application/json
Authorization: Bearer <token>

{
  "item_id": "550e8400-e29b-41d4-a716-446655440000",
  "location_id": "660e8400-e29b-41d4-a716-446655440000",
  "quantity": 30
}
```

#### Get Inventory History

View transaction history:

```bash
# Get all history
GET /api/v1/inventory/history?skip=0&limit=50

# Filter by item
GET /api/v1/inventory/history?item_id=550e8400-e29b-41d4-a716-446655440000

# Filter by location
GET /api/v1/inventory/history?location_id=660e8400-e29b-41d4-a716-446655440000

# Filter by transaction type
GET /api/v1/inventory/history?transaction_type=transfer
```

**Response:**
```json
{
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "item_id": "550e8400-e29b-41d4-a716-446655440000",
      "location_id": "660e8400-e29b-41d4-a716-446655440000",
      "quantity_change": 10,
      "transaction_type": "adjust",
      "performed_by": "admin",
      "notes": "Restocked from trading post",
      "timestamp": "2024-01-01T12:05:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50,
  "pages": 1
}
```

### Items API

#### List Items

```bash
GET /api/v1/items?skip=0&limit=50&search=quantum&category=Consumables
```

### Locations API

#### List Locations

```bash
GET /api/v1/locations?skip=0&limit=50&type=station&search=babbage
```

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `docker compose ps db`
- Check `DATABASE_URL` format: `postgresql+psycopg://user:pass@host:port/dbname`
- Ensure database exists and user has proper permissions

### Import Errors

- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python path: ensure you're in the backend directory

### CORS Issues

- Verify `CORS_ORIGINS` includes your frontend URL
- Check browser console for specific CORS errors
- Ensure backend and frontend URLs match configuration

## Next Steps

- [ ] Set up Alembic migrations for database schema
- [ ] Implement authentication endpoints
- [ ] Create user and organization models
- [ ] Add API versioning middleware

See the [Implementation Roadmap](../planning/implementation-roadmap.md) for detailed development tasks.

