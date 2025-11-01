# Database Schema Documentation

This document describes the database schema for SCIMS (Star Citizen Inventory Management System). The schema is managed through SQLAlchemy models and Alembic migrations.

## Overview

The current schema focuses on core user and organization management, forming the foundation for inventory management features. The design prioritizes:

- **Flexibility**: Models can be extended without breaking existing functionality
- **Maintainability**: Clear relationships and constraints
- **Performance**: Appropriate indexes for common queries

## Schema Version

**Current Version:** `4fe1b28b8fa5` (Canonical locations support added to locations table)

## Core Tables

### users

Stores user account information and authentication data.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEXED | User email address (used for login) |
| `username` | VARCHAR(100) | UNIQUE, NULLABLE, INDEXED | Optional username for display |
| `hashed_password` | VARCHAR(255) | NULLABLE | Bcrypt/Argon2 hashed password (nullable for OAuth) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Account active status |
| `is_verified` | BOOLEAN | NOT NULL, DEFAULT false | Email verification status |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique index on `email`
- Unique index on `username` (nullable)
- Index on `email` for fast lookups

**Relationships:**
- One-to-many with `organization_members` (a user can be in multiple organizations)

**Future Considerations:**
- OAuth provider integration (add `google_id`, `discord_id`, etc.)
- Profile fields (`avatar_url`, `bio`, `preferences`)
- Last login tracking
- Two-factor authentication fields

---

### organizations

Stores organization/team information for collaborative inventory management.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `name` | VARCHAR(255) | NOT NULL, INDEXED | Organization name |
| `slug` | VARCHAR(100) | UNIQUE, NULLABLE, INDEXED | URL-friendly identifier |
| `description` | TEXT | NULLABLE | Organization description |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Index on `name` for search/filtering
- Unique index on `slug` (nullable)

**Relationships:**
- One-to-many with `organization_members` (an organization has multiple members)

**Future Considerations:**
- Billing and subscription plans
- Organization settings (theme, branding, limits)
- Public/private visibility
- Organization-level integrations and API keys

---

### organization_members

Junction table linking users to organizations with role-based access.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `organization_id` | UUID | FOREIGN KEY, NOT NULL, INDEXED | Reference to organizations table |
| `user_id` | UUID | FOREIGN KEY, NOT NULL, INDEXED | Reference to users table |
| `role` | VARCHAR(50) | NOT NULL, DEFAULT 'member', INDEXED | User role (owner, admin, member, viewer) |
| `joined_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | When user joined |

**Constraints:**
- Unique constraint on (`organization_id`, `user_id`) - prevents duplicate memberships
- Foreign key to `organizations.id` with CASCADE delete
- Foreign key to `users.id` with CASCADE delete

**Indexes:**
- Primary key on `id`
- Index on `organization_id` for org member queries
- Index on `user_id` for user's organization queries
- Index on `role` for role-based filtering
- Unique constraint index on (`organization_id`, `user_id`)

**Valid Roles:**
- `owner`: Full control, can delete organization
- `admin`: Can manage members and settings
- `member`: Can create and edit inventory items
- `viewer`: Read-only access

**Relationships:**
- Many-to-one with `organizations`
- Many-to-one with `users`

**Future Considerations:**
- Role hierarchy system (can extend roles without migration)
- Custom permissions per role
- Invitation system (pending status, invitation tokens)
- Member metadata (notes, tags, custom fields)

---

## Database Functions and Triggers

### update_updated_at_column()

PostgreSQL function that automatically updates the `updated_at` timestamp when a row is modified.

**Triggers:**
- `update_users_updated_at`: Updates `users.updated_at` on UPDATE
- `update_organizations_updated_at`: Updates `organizations.updated_at` on UPDATE
- `update_ships_updated_at`: Updates `ships.updated_at` on UPDATE

This ensures `updated_at` is always current without requiring application-level management.

---

### cleanup_old_item_history()

PostgreSQL function for cleaning up old item_history audit trail records.

**Function Signature:**
```sql
cleanup_old_item_history(retention_days INTEGER DEFAULT 30) RETURNS INTEGER
```

**Usage:**
```sql
-- Delete records older than 30 days (default)
SELECT cleanup_old_item_history();

-- Delete records older than 60 days
SELECT cleanup_old_item_history(60);
```

**Returns:** Number of records deleted.

**Purpose:** Prevents unbounded growth of the `item_history` table by removing records older than the specified retention period. Default retention is 30 days.

**Automation:** A Python script (`backend/scripts/cleanup_item_history.py`) provides a CLI interface. This will be scheduled as a Celery periodic task in Phase 3 for automatic daily cleanup.

---

## Connection Pooling

Database connections are managed through SQLAlchemy's connection pool:

- **Pool Size:** 5 connections (maintained in pool)
- **Max Overflow:** 10 additional connections
- **Pool Timeout:** 30 seconds
- **Pool Recycle:** 3600 seconds (1 hour)
- **Pre-ping:** Enabled (verifies connections before use)

These settings can be adjusted in `app/database.py`.

---

## Migration Strategy

### Current Migrations

1. **001_initial** - Initial schema with users, organizations, and organization_members tables
2. **d717c1642e4d** - Inventory tables: locations, ships, items, item_stocks, item_history
3. **4fe1b28b8fa5** - Canonical locations support: added `is_canonical`, `canonical_location_id`, `created_by` fields to locations table

### Creating New Migrations

After modifying SQLAlchemy models:

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Description of changes"

# Review and test the migration
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

### Migration Best Practices

1. **Never edit applied migrations** - Create new migrations to fix issues
2. **Always test up and down** - Ensure migrations can be rolled back
3. **Review auto-generated code** - Alembic may miss some changes
4. **Include data migrations** - When schema changes require data transformations
5. **Use descriptive messages** - Explain what changed and why

---

## ER Diagram

```
┌─────────────┐
│    users    │
├─────────────┤
│ id (PK)     │
│ email       │◄─────────┐
│ username    │          │
│ password    │          │
│ is_active   │          │
│ is_verified │          │
│ created_at  │          │
│ updated_at  │          │
└─────────────┘          │
                         │
                         │ user_id (FK)
                         │
┌─────────────────────────┼───────────────┐
│ organization_members    │               │
├─────────────────────────┼───────────────┤
│ id (PK)                 │               │
│ organization_id (FK) ───┼──┐            │
│ user_id (FK) ───────────┘  │            │
│ role                      │            │
│ joined_at                 │            │
│                           │            │
│ UNIQUE(org_id, user_id)   │            │
└───────────────────────────┼────────────┘
                            │
                            │ organization_id (FK)
                            │
                ┌───────────▼───────────────┐
                │   organizations           │
                ├───────────────────────────┤
                │ id (PK)                   │
                │ name                      │
                │ slug                      │
                │ description               │
                │ created_at                │
                │ updated_at                │
                └───────────────────────────┘
```

---

---

### locations

Stores inventory storage locations including stations, ship cargo grids, player inventories, and warehouses.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `name` | VARCHAR(255) | NOT NULL, INDEXED | Location name |
| `type` | VARCHAR(50) | NOT NULL, INDEXED | Location type: station, ship, player_inventory, warehouse |
| `owner_type` | VARCHAR(50) | NOT NULL, INDEXED | Owner type: user, organization, ship |
| `owner_id` | UUID | NOT NULL, INDEXED | Reference to the owner (user, organization, or ship) |
| `parent_location_id` | UUID | FOREIGN KEY, NULLABLE, INDEXED | Parent location for nested locations |
| `is_canonical` | BOOLEAN | NOT NULL, DEFAULT false, INDEXED | Whether this is a canonical/public location |
| `canonical_location_id` | UUID | FOREIGN KEY, NULLABLE, INDEXED | Reference to canonical location (for player locations) |
| `created_by` | UUID | FOREIGN KEY, NULLABLE, INDEXED | User who created this canonical location |
| `metadata` | JSONB | NULLABLE | Flexible location-specific data (JSON) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Creation timestamp |

**Indexes:**
- Primary key on `id`
- Index on `name` for search
- Index on `type` for filtering
- Composite index on (`owner_type`, `owner_id`) for owner queries
- Index on `parent_location_id` for hierarchy traversal
- Index on `is_canonical` for filtering canonical locations
- Index on `canonical_location_id` for finding locations at canonical locations
- Index on `created_by` for tracking canonical location creators

**Relationships:**
- Self-referential: `parent_location` → `child_locations` (hierarchical locations)
- Self-referential: `canonical_location` → `locations_at_canonical` (canonical location references)
- One-to-many with `item_stocks` (location has multiple stock records)
- One-to-many with `item_history` (location has transaction history)
- One-to-one with `ships` via `cargo_location_id` (if location is a ship's cargo grid)
- One-to-many with `ships` via `current_location_id` (ships parked at this location)
- Many-to-one with `users` via `created_by` (canonical location creator)

**Canonical Locations:**
- Canonical locations (`is_canonical = true`) are public locations that many players reference (e.g., game stations, planets)
- Canonical locations use `owner_type="system"` and are managed by admins/moderators
- Player locations can reference canonical locations via `canonical_location_id` to indicate they are "at" a canonical location
- Canonical locations are publicly readable (no authentication required) but can only be created/updated by admins

**Future Considerations:**
- Location capacity limits
- Access control per location

---

### ships

Stores ship information for ships owned by users or organizations. Ships can be moved between locations and contain their own cargo grid.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `name` | VARCHAR(255) | NOT NULL, INDEXED | Ship name |
| `ship_type` | VARCHAR(100) | NULLABLE, INDEXED | Ship type/model (e.g., Constellation, Freelancer) |
| `owner_type` | VARCHAR(50) | NOT NULL, INDEXED | Owner type: user, organization |
| `owner_id` | UUID | NOT NULL, INDEXED | Reference to the owner (user or organization) |
| `current_location_id` | UUID | FOREIGN KEY, NULLABLE, INDEXED | Current location where ship is parked/stationed |
| `cargo_location_id` | UUID | FOREIGN KEY, NOT NULL, UNIQUE | Location representing the ship cargo grid |
| `metadata` | JSONB | NULLABLE | Ship-specific data (JSON: cargo capacity, modules, etc.) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Last update timestamp |

**Constraints:**
- Foreign key to `locations.id` via `current_location_id` (SET NULL on delete)
- Foreign key to `locations.id` via `cargo_location_id` (RESTRICT on delete - prevents accidental deletion)
- Unique constraint on `cargo_location_id` (each ship has exactly one cargo grid)

**Indexes:**
- Primary key on `id`
- Index on `name` for search
- Index on `ship_type` for filtering
- Composite index on (`owner_type`, `owner_id`) for owner queries
- Index on `current_location_id` for location-based queries
- Unique index on `cargo_location_id`

**Relationships:**
- Many-to-one with `locations` via `current_location_id` (where ship is parked)
- One-to-one with `locations` via `cargo_location_id` (the ship's cargo grid location)

**Design Notes:**
- `current_location_id` is nullable to support ships in transit
- When creating a ship, the cargo location must be created first with `owner_type='ship'` and `owner_id=ships.id`
- Ships can be moved by updating `current_location_id`

---

### items

Item catalog/master data for inventory items. Defines item properties separate from stock levels.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `name` | VARCHAR(255) | NOT NULL, INDEXED | Item name |
| `description` | TEXT | NULLABLE | Item description |
| `category` | VARCHAR(100) | NULLABLE, INDEXED | Item category |
| `subcategory` | VARCHAR(100) | NULLABLE, INDEXED | Item subcategory |
| `rarity` | VARCHAR(50) | NULLABLE, INDEXED | Item rarity level |
| `metadata` | JSONB | NULLABLE | Game-specific attributes (JSON) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Creation timestamp |

**Indexes:**
- Primary key on `id`
- Index on `name` for search
- Index on `category` for filtering
- Index on `subcategory` for filtering
- Index on `rarity` for filtering

**Relationships:**
- One-to-many with `item_stocks` (item can be at multiple locations)
- One-to-many with `item_history` (item has transaction history)

---

### item_stocks

Tracks stock levels for items at specific locations, including available and reserved quantities.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `item_id` | UUID | FOREIGN KEY, NOT NULL, INDEXED | Reference to items table |
| `location_id` | UUID | FOREIGN KEY, NOT NULL, INDEXED | Reference to locations table |
| `quantity` | NUMERIC(15,3) | NOT NULL, DEFAULT 0 | Available quantity (supports fractional) |
| `reserved_quantity` | NUMERIC(15,3) | NOT NULL, DEFAULT 0 | Quantity reserved for in-progress crafts |
| `last_updated` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Timestamp of last update |
| `updated_by` | UUID | FOREIGN KEY, NULLABLE, INDEXED | Reference to users table (who updated) |

**Constraints:**
- Unique constraint on (`item_id`, `location_id`) - one stock record per item/location pair
- Foreign key to `items.id` with CASCADE delete
- Foreign key to `locations.id` with CASCADE delete
- Foreign key to `users.id` with SET NULL on delete

**Indexes:**
- Primary key on `id`
- Index on `item_id` for item queries
- Index on `location_id` for location queries
- Index on `updated_by` for user activity
- Unique constraint index on (`item_id`, `location_id`)

**Relationships:**
- Many-to-one with `items`
- Many-to-one with `locations`
- Many-to-one with `users` via `updated_by`

**Notes:**
- Available quantity = `quantity` - `reserved_quantity`
- Reserved quantity is used for in-progress crafts or planned operations

---

### item_history

Audit trail of all inventory transactions and changes.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `item_id` | UUID | FOREIGN KEY, NOT NULL, INDEXED | Reference to items table |
| `location_id` | UUID | FOREIGN KEY, NOT NULL, INDEXED | Reference to locations table |
| `quantity_change` | NUMERIC(15,3) | NOT NULL | Quantity change (positive/negative) |
| `transaction_type` | VARCHAR(50) | NOT NULL, INDEXED | Type: add, remove, transfer, craft, consume |
| `related_craft_id` | UUID | NULLABLE | Reference to related craft (FK to be added in Phase 3) |
| `performed_by` | UUID | FOREIGN KEY, NOT NULL, INDEXED | Reference to users table |
| `timestamp` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Transaction timestamp |
| `notes` | TEXT | NULLABLE | Optional notes about the transaction |

**Indexes:**
- Primary key on `id`
- Index on `item_id` for item history queries
- Index on `location_id` for location history queries
- Index on `transaction_type` for filtering by type
- Index on `performed_by` for user activity tracking
- Index on `timestamp` for time-based queries

**Relationships:**
- Many-to-one with `items`
- Many-to-one with `locations`
- Many-to-one with `users` via `performed_by`

**Transaction Types:**
- `add` - Items added to inventory
- `remove` - Items removed from inventory
- `transfer` - Items transferred between locations
- `craft` - Items produced by crafting
- `consume` - Items consumed in crafting or operations

**Data Retention:**
To prevent unbounded table growth, old records are automatically cleaned up:
- **Default retention:** 30 days
- **Cleanup function:** `cleanup_old_item_history(retention_days INTEGER DEFAULT 30)`
  - Can be called directly: `SELECT cleanup_old_item_history(30);`
  - Returns the number of deleted records
- **Cleanup script:** `backend/scripts/cleanup_item_history.py`
  - Manual cleanup: `python -m scripts.cleanup_item_history --days 30`
  - Dry run: `python -m scripts.cleanup_item_history --dry-run`
- **Future automation:** Will be scheduled as a Celery periodic task (daily) in Phase 3
- **Future enhancement:** Plans exist to aggregate old data into compressed statistics/trends before deletion, preserving analytical value while reducing storage requirements

---

## Future Schema Additions

Based on the implementation roadmap, future tables will include:

- **recipes** - Crafting recipes
- **crafts** - Crafting jobs/orders
- **craft_ingredients** - Recipe ingredient requirements
- **goals** - Inventory goals and targets
- **resource_sources** - External resource availability
- **commons_*** - Public commons moderation tables

These will be added in subsequent phases following the same patterns established here.

---

## References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- Model definitions: `backend/app/models/`
- Migration files: `backend/alembic/versions/`

