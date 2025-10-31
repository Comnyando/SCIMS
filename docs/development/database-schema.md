# Database Schema Documentation

This document describes the database schema for SCIMS (Star Citizen Inventory Management System). The schema is managed through SQLAlchemy models and Alembic migrations.

## Overview

The current schema focuses on core user and organization management, forming the foundation for inventory management features. The design prioritizes:

- **Flexibility**: Models can be extended without breaking existing functionality
- **Maintainability**: Clear relationships and constraints
- **Performance**: Appropriate indexes for common queries

## Schema Version

**Current Version:** `001_initial` (Initial schema with users, organizations, and memberships)

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

This ensures `updated_at` is always current without requiring application-level management.

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

## Future Schema Additions

Based on the implementation roadmap, future tables will include:

- **locations** - Inventory storage locations (stations, ships, warehouses)
- **items** - Item catalog with metadata
- **item_stocks** - Item quantities per location
- **item_history** - Audit trail for inventory changes
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

