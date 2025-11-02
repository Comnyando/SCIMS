# Implementation Roadmap
## Star Citizen Inventory Management System

This document provides a detailed, phase-by-phase implementation plan with actionable tasks. Tasks are organized by phases and sub-phases to allow flexible scheduling without time constraints.

---

## Phase 0: Foundation Setup

### Sub-phase 0.1: Repository & Project Structure

**Tasks:**
- [x] Create GitHub repository
- [x] Setup branch protection rules (main/master branch)
- [x] Create initial project structure:
  ```
  ManagementProject/
  ├── backend/
  │   ├── app/
  │   │   ├── __init__.py
  │   │   ├── main.py
  │   │   ├── config.py
  │   │   ├── database.py
  │   │   ├── models/
  │   │   ├── schemas/
  │   │   ├── fazer/
  │   │   └── services/
  │   ├── alembic/
  │   ├── tests/
  │   ├── Dockerfile
  │   └── requirements.txt
  ├── frontend/
  │   ├── src/
  │   │   ├── components/
  │   │   ├── pages/
  │   │   ├── services/
  │   │   ├── hooks/
  │   │   └── types/
  │   ├── public/
  │   ├── Dockerfile
  │   └── package.json
  ├── nginx/
  │   └── nginx.conf
  ├── docker-compose.yml
  ├── docker-compose.prod.yml
  ├── .env.example
  ├── .gitignore
  └── README.md
  ```
- [x] Create comprehensive .gitignore for Python, Node.js, Docker
- [x] Write initial README.md with project description
- [x] Create docs/ directory structure
- [x] Create root README.md with comprehensive setup instructions

### Sub-phase 0.2: Docker & Development Environment

**Tasks:**
- [x] Create docker-compose.yml with services:
  - PostgreSQL (port 5432)
  - Redis (port 6379)
  - Backend (port 8000)
  - Frontend (port 5173 - Vite default)
  - Nginx (port 80/443)
- [x] Create backend Dockerfile (multi-stage build)
- [x] Create frontend Dockerfile (multi-stage build)
- [x] Setup Nginx configuration:
  - Reverse proxy to backend API
  - Serve frontend static files
  - SSL configuration (prepared for production)
- [x] Create .env.example with all required variables
- [x] Test docker-compose up locally
- [x] Document development setup in root README.md
- [x] Create backend/README.md with backend setup instructions
- [x] Create frontend/README.md with frontend setup instructions
- [x] Create docs/getting-started/installation.md
- [x] Update root README.md with Docker setup instructions

### Sub-phase 0.3: Basic CI/CD

**Tasks:**
- [x] Create .github/workflows/ci.yml:
  - Linting (Black for Python, ESLint for TypeScript)
  - Type checking (mypy, TypeScript)
  - Basic tests (placeholder)
  - Docker image building
- [x] Setup pre-commit hooks (optional but recommended)
- [x] Test CI pipeline on GitHub

---

## Phase 1: Core Backend & Authentication

### Sub-phase 1.1: Database Schema & Migrations

**Tasks:**
- [x] Setup Alembic for database migrations
- [x] Create initial migration for:
  - users table
  - organizations table
  - organization_members table
- [x] Create SQLAlchemy models:
  - User model
  - Organization model
  - OrganizationMember model
- [x] Create Pydantic schemas for validation
- [x] Setup database connection pooling
- [x] Create seed data script (test users, orgs)
- [x] Test migrations up/down
- [x] Update backend/README.md with database setup and migration instructions
- [x] Document database schema in docs/development/database-schema.md

### Sub-phase 1.2: Authentication System

**Tasks:**
- [x] Implement password hashing (bcrypt)
- [x] Create authentication endpoints:
  - POST /api/v1/auth/register
  - POST /api/v1/auth/login
  - POST /api/v1/auth/refresh
  - GET /api/v1/auth/me
- [x] Implement JWT token generation/validation
- [x] Create authentication middleware/dependencies
- [x] Setup CORS configuration
- [x] Create basic RBAC (roles: owner, admin, member, viewer)
- [x] Write unit tests for authentication
 
---

## Phase 2: Inventory Core

### Sub-phase 2.1: Items & Locations Backend

**Tasks:**
- [x] Create database migrations for:
  - items table
  - locations table
  - ships table
  - item_stocks table
  - item_history table
- [x] Create SQLAlchemy models for all tables (Item, Location, Ship, ItemStock, ItemHistory)
- [x] Create Pydantic schemas
- [x] Implement Items API:
  - GET /api/v1/items (list, search, pagination)
  - POST /api/v1/items
  - GET /api/v1/items/{item_id}
  - PATCH /api/v1/items/{item_id}
  - DELETE /api/v1/items/{item_id}
- [x] Implement Locations API:
  - GET /api/v1/locations
  - POST /api/v1/locations
  - GET /api/v1/locations/{location_id}
  - PATCH /api/v1/locations/{location_id}
  - DELETE /api/v1/locations/{location_id}
- [x] Implement Ships API:
  - GET /api/v1/ships
  - POST /api/v1/ships
  - GET /api/v1/ships/{ship_id}
  - PATCH /api/v1/ships/{ship_id} (including moving ships between locations)
  - DELETE /api/v1/ships/{ship_id}
- [x] Write tests for Items, Locations, and Ships APIs

### Sub-phase 2.2: Inventory Management & Frontend

**Tasks:**
- [x] Implement Inventory API:
  - GET /api/v1/inventory (with filters)
  - POST /api/v1/inventory/adjust
  - POST /api/v1/inventory/transfer
  - GET /api/v1/inventory/history
- [x] Implement stock reservation logic
- [x] Create item_history logging on all changes
- [x] Setup React project structure
- [x] Create basic routing (React Router)
- [x] Implement authentication context/state
- [x] Create login/register pages
- [x] Create basic dashboard layout
- [x] Create Items list page
- [x] Create Locations management page
- [x] Create Inventory view page
- [x] Update docs/user-guide/inventory.md with usage instructions
- [x] Update root README.md with inventory management features
- [x] Add API endpoint examples to backend/README.md
- [x] Add initial user-facing guide sections for inventory UI
- [~] Onboarding/tour system deferred - will be implemented during UI redesign phase
- [x] Implement initial onboarding scaffold (tour placeholders)

---

## Phase 3: Planning & Crafting

### Sub-phase 3.1: Blueprints System

**Tasks:**
- [x] Create database migration for blueprints table
- [x] Create Blueprint model and schemas
- [x] Implement Blueprints API:
  - [x] GET /api/v1/blueprints
  - [x] POST /api/v1/blueprints
  - [x] GET /api/v1/blueprints/{blueprint_id}
  - [x] PATCH /api/v1/blueprints/{blueprint_id}
  - [x] DELETE /api/v1/blueprints/{blueprint_id}
  - [x] GET /api/v1/blueprints/popular
  - [x] GET /api/v1/blueprints/by-item/{item_id}
- [x] Implement blueprint validation (check item IDs exist)
- [x] Implement blueprint sharing (public/private)
- [x] Write tests for Blueprints API
- [x] Create frontend Blueprint browser page
- [x] Create Blueprint detail/view page
- [x] Create Blueprint creation/edit form
- [x] Update docs/user-guide/crafting.md with blueprint and craft management
- [x] Update root README.md with crafting features

### Sub-phase 3.2: Crafts Management Backend

**Tasks:**
- [x] Create database migrations for:
  - crafts table
  - craft_ingredients table
- [x] Create models and schemas
- [x] Implement Crafts API:
  - GET /api/v1/crafts
  - POST /api/v1/crafts
  - GET /api/v1/crafts/{craft_id}
  - PATCH /api/v1/crafts/{craft_id}
  - DELETE /api/v1/crafts/{craft_id}
  - POST /api/v1/crafts/{craft_id}/start
  - POST /api/v1/crafts/{craft_id}/complete
  - GET /api/v1/crafts/{craft_id}/progress
- [x] Implement ingredient reservation on craft creation
- [x] Implement stock deduction on craft completion
- [x] Create Celery task for automated craft completion (timed)
- [x] Write tests for Crafts API
- [x] Schedule periodic item_history cleanup task (Celery periodic task, runs daily)
- [ ] Implement ingredient reservation on craft creation
- [ ] Implement stock deduction on craft completion
- [ ] Create Celery task for automated craft completion (timed)
- [ ] Write tests for Crafts API
- [ ] Schedule periodic item_history cleanup task (Celery periodic task, runs daily)

### Sub-phase 3.3: Crafts Management Frontend

**Tasks:**
- [x] Create Craft queue page
- [x] Create Craft creation wizard (select recipe, set location, etc.)
- [x] Create Craft detail page with progress tracking
- [x] Implement real-time updates (WebSocket or polling) - Using polling via React Query
- [x] Create craft status indicators
- [x] Add filtering and sorting to craft list
- [x] Update docs/user-guide/crafting.md with craft tracking features
- [x] Add crafting examples to documentation (crafting-examples.md)

**Note:** Frontend testing and guided tours deferred until UI redesign phase (after backend completion).

---

## Phase 4: Optimization Engine

### Sub-phase 4.1: Source Tracking System

**Tasks:**
- [x] Create database migrations for:
  - resource_sources table
  - source_verification_log table
- [x] Create models and schemas
- [x] Implement Resource Sources API:
  - GET /api/v1/sources
  - POST /api/v1/sources
  - GET /api/v1/sources/{source_id}
  - PATCH /api/v1/sources/{source_id}
  - POST /api/v1/sources/{source_id}/verify
- [x] Implement reliability scoring algorithm
- [x] Create source verification workflow
- [x] Write tests

### Sub-phase 4.2: Optimization Algorithms

**Tasks:**
- [x] Design optimization algorithm:
  - Check current stocks first
  - Check other players' stocks (with permissions)
  - Check universe sources
  - Calculate costs/benefits
- [x] Implement POST /api/v1/optimization/find-sources endpoint
- [x] Implement POST /api/v1/optimization/suggest-crafts endpoint
- [x] Implement GET /api/v1/optimization/resource-gap/{craft_id}
- [x] Create optimization service class
- [x] Write comprehensive tests for algorithms
- [x] Performance test with large datasets
- [x] Update docs/user-guide/optimization.md with optimization features
- [x] Document optimization algorithms and source finding logic
- [x] Add examples of optimization usage

### Sub-phase 4.3: Optimization Frontend

**Tasks:**
- [x] Create optimization results display component
- [x] Create resource gap visualization
- [x] Create source recommendation cards
- [x] Integrate optimization into craft creation flow
- [x] Create optimization settings page
- [x] Add cost/benefit indicators
- [x] Update docs/user-guide/optimization.md with UI instructions
- [x] Add optimization workflow examples

**Note:** Frontend testing and guided tours deferred until UI redesign phase.

---

## Future Enhancement Notes

### Organization Roles & Permissions (Post-MVP)

**Quartermaster Role:**
- Create a "Quartermaster" role level for organizations (between regular member and admin)
- Quartermasters should have permissions to:
  - Allocate and modify organization stock/inventory
  - Allocate resources to organization crafts and projects
  - Approve/reject resource requisitions (see below)
  - View organization resource reports
  - Manage organization resource sources
- Quartermasters should NOT have permissions to:
  - Modify organization settings
  - Add/remove members (unless also granted)
  - Delete organization
- Implementation considerations:
  - Extend `OrganizationMember` model with `role` field (owner, admin, quartermaster, member, viewer)
  - Update RBAC system to support role-based permissions
  - Add role assignment/management endpoints
  - Update access control checks throughout inventory, crafts, and optimization endpoints

**Resource Requisition System:**
- Create a requisition system for requesting resources from:
  - Organization stock (when user is not a quartermaster/admin)
  - Other players' shared resources
  - Organization projects/crafts requiring additional resources
- Requisition workflow:
  - Users can create requisitions specifying:
    - Requested items and quantities
    - Source (org stock, player stock, project allocation)
    - Purpose/justification
    - Priority level
  - Requisitions require approval by:
    - Organization quartermaster(s)
    - Organization admin(s)
    - Project lead (for project-specific requisitions)
  - Approval workflow:
    - Requisitions can be approved, rejected, or modified
    - Approvals can have comments/notes
    - Multi-level approval possible (quartermaster → admin)
    - Automatic fulfillment upon approval (if resources available)
    - Notifications for requester and approvers
- Implementation considerations:
  - New `requisitions` table with fields:
    - `id`, `requester_id`, `organization_id` (nullable), `project_id` (nullable)
    - `status` (pending, approved, rejected, fulfilled, cancelled)
    - `requested_items` (JSONB), `priority`, `purpose`
    - `approved_by`, `approved_at`, `approval_notes`
    - `fulfilled_at`, `created_at`, `updated_at`
  - Requisition approval API endpoints
  - Integration with inventory system for fulfillment
  - Notification system for status changes
  - Requisition history and audit trail

---

## Phase 5: Goals & Analytics

### Sub-phase 5.1: Goals System

**Tasks:**
- [ ] Create database migration for goals table
- [ ] Create Goal model and schemas
- [ ] Implement Goals API:
  - GET /api/v1/goals
  - POST /api/v1/goals
  - GET /api/v1/goals/{goal_id}
  - PATCH /api/v1/goals/{goal_id}
  - DELETE /api/v1/goals/{goal_id}
- [ ] Implement goal progress calculation
- [ ] Implement goal completion detection
- [ ] Write tests
- [ ] Create frontend Goals page
- [ ] Create Goal creation/edit form
- [ ] Create Goal progress visualization
- [ ] Update docs/user-guide/goals.md with usage

**Note:** Frontend testing and guided tours deferred until UI redesign phase.

### Sub-phase 5.2: Analytics Foundation

**Tasks:**
- [ ] Create database migrations for:
  - usage_events table
  - recipe_usage_stats table
- [ ] Create models and schemas
- [ ] Implement consent management:
  - User consent flag
  - Consent API endpoints
- [ ] Create usage event logging middleware
- [ ] Implement Analytics API:
  - GET /api/v1/analytics/usage-stats (if consented)
  - GET /api/v1/analytics/recipe-stats/{recipe_id}
- [ ] Create Celery task for stats aggregation
- [ ] Implement privacy safeguards (anonymization)
- [ ] Write tests
- [ ] Create frontend consent management UI
- [ ] Create basic analytics dashboard (if consented)
- [ ] Update docs/user-guide/goals.md with goal management
- [ ] Document analytics features and consent management
- [ ] Update root README.md with goals and analytics features

---

## Phase 6: Integration고ramework

### Sub-phase 6.1: Integration Service Backend

**Tasks:**
- [ ] Create database migrations for:
  - integrations table
  - integration_logs table
- [ ] Create models and schemas
- [ ] Implement Integrations API:
  - GET /api/v1/integrations
  - POST /api/v1/integrations
  - GET /api/v1/integrations/{integration_id}
  - PATCH /api/v1/integrations/{integration_id}
  - DELETE /api/v1/integrations/{integration_id}
  - POST /api/v1/integrations/{integration_id}/test
  - GET /api/v1/integrations/{integration_id}/logs
- [ ] Create webhook handler endpoint
- [ ] Implement API key encryption/storage
- [ ] Create integration framework (base class for integrations)
- [ ] Write tests

### Sub-phase 6.2: Data Import/Export & Frontend

**Tasks:**
- [ ] Implement CSV import/export:
  - Items CSV
  - Inventory CSV
  - Recipes CSV
- [ ] Implement JSON import/export
- [ ] Create import validation
- [ ] Create export filters
- [ ] Write tests
- [ ] Create frontend Integration management page
- [ ] Create webhook configuration UI
- [ ] Create import/export UI
- [ ] Create integration testing interface
- [ ] Update docs/user-guide/integrations.md with integration setup
- [ ] Document import/export formats and procedures

- [ ] Add integration examples and webhook configuration

**Note:** Frontend testing and guided tours deferred until UI redesign phase.

---

## Phase 6.5: Public Commons & Moderation

### Sub-phase 6.3: Commons Backend & Public Endpoints

**Tasks:**
- [ ] Create database migrations:
  - commons_submissions, commons_moderation_actions
  - commons_entities, commons_entity_tags, tags
  - entity_aliases, duplicate_groups
- [ ] Implement submission API:
  - POST /api/v1/commons/submit
  - GET /api/v1/commons/my-submissions
  - PATCH /api/v1/commons/submissions/{id}
- [ ] Implement admin moderation API:
  - GET /api/v1/admin/commons/submissions?status=pending
  - POST approve/reject/request-changes/merge
- [ ] Implement public read APIs:
  - /public/items, /public/recipes, /public/locations, /public/tags, /public/search
- [ ] Add Redis caching for public catalogs; cache-bust on publish
- [ ] Add rate limiting and abuse protection
- [ ] Write backend tests for workflows (submit → approve → publish)
- [ ] Update docs: data model, API endpoints, moderation lifecycle

### Sub-phase 6.4: Commons Admin Frontend & UX

**Tasks:**
- [ ] Build Moderation Dashboard (queue, filters, bulk actions)
- [ ] Build Submission Detail (diff view, actions)
- [ ] Build Public Entity Manager (list/search/tags/version)
- [ ] Build Tag Manager (CRUD/merge)
- [ ] Build Duplicate Finder UI (review/confirm merges)
- [ ] Add user-facing submission UI with guidelines
- [ ] Update docs/user-guide with submission guidelines & admin guide

**Note:** Frontend testing and guided tours deferred until UI redesign phase.

---

## Phase 7: Polish & Production Readiness

### Sub-phase 7.1: Comprehensive Testing

**Tasks:**
- [ ] Achieve >80% backend test coverage
- [ ] Write integration tests for critical flows:
  - User registration → org creation → inventory → craft
  - Recipe sharing → craft planning → execution
  - Integration setup → data import
- [ ] Setup E2E tests with Playwright/Cypress
- [ ] Create test data fixtures
- [ ] Document testing procedures

**Note:** Frontend test coverage and onboarding/tutorial flows deferred until UI redesign phase.

### Sub-phase 7.2: Documentation

**Tasks:**
- [ ] Complete OpenAPI/Swagger documentation
- [ ] Write user documentation:
  - Getting started guide
  - Feature guides
  - FAQ
- [ ] Write developer documentation:
  - Setup guide
  - Architecture overview
  - Contributing guidelines
- [ ] Create API usage examples
- [ ] Create deployment guides
- [ ] Update all README files (root, backend, frontend)
- [ ] Review and ensure all documentation is comprehensive
- [ ] Add code examples throughout documentation
- [ ] Create docs/README.md as documentation index
- [ ] Add troubleshooting sections to all guides
- [ ] Document deployment procedures in docs/deployment/
- [ ] Finalize all user guide sections
- [ ] Publish in-app tutorial content and screenshots to docs/user-guide/onboarding.md
- [ ] Add email provider setup guide: SPF/DKIM/DMARC, webhooks, env vars
- [ ] Add Public Commons documentation: submission, moderation, publishing, takedown

### Sub-phase 7.3: Security & Performance

**Tasks:**
- [ ] Security audit:
  - Dependency vulnerability scan
  - SQL injection testing
  - XSS testing
  - Authentication bypass testing
- [ ] Implement rate limiting
- [ ] Add security headers
- [ ] Performance optimization:
  - Database query optimization
  - Add Redis caching for frequent queries
  - Frontend bundle optimization
  - Image optimization
- [ ] Load testing with Locust/k6
- [ ] Fix performance bottlenecks
- [ ] Validate email bounces/complaints webhook and suppression list behavior
- [ ] Validate backup/restore drill in staging (weekly automated restore)

### Sub-phase 7.4: Production Deployment

**Tasks:**
- [ ] Create production docker-compose configuration
- [ ] Setup production environment variables
- [ ] Configure SSL certificates (Let's Encrypt)
  - [ ] Deploy Certbot container sharing `/etc/letsencrypt` with Nginx
  - [ ] Configure HTTP-01 challenge location in Nginx (port 80 open)
  - [ ] Or configure DNS-01 challenge with Cloudflare API token
  - [ ] Automate renewal (cron) and `nginx -s reload` post-renewal
  - [ ] Enforce HTTPS (301), set HSTS (short max-age initially)
  - [ ] Validate with staging CA before production issuance
- [ ] Setup database backups:
  - Daily pg_dump -Fc to Restic repo (local or S3-compatible)
  - Restic retention: 7 daily, 4 weekly, 3 monthly
  - Weekly automated restore verification job
- [ ] Setup Redis RDB snapshot schedule
- [ ] Configure backup failure alerts (Alertmanager/email)
- [ ] Configure SSL certificates (Let's Encrypt)
- [ ] Setup monitoring:
  - Application health checks
  - Error tracking (Sentry)
  - Basic metrics collection
- [ ] Create deployment runbook
- [ ] Perform production deployment
- [ ] Smoke testing in production
- [ ] Create rollback procedure
- [ ] Verify email sending in production and DNS status (SPF/DKIM/DMARC)
- [ ] Configure Nginx for static assets: gzip/Brotli, HTTP/2, ETag, Cache-Control
- [ ] Enable asset hashing and immutable caching in build
- [ ] (Optional) Configure Cloudflare: proxy, cache rules for /assets/*, TLS, Brotli
- [ ] (Optional) Configure MinIO/R2 for large assets with CDN in front
- [ ] Configure rate limiting for /public and /commons endpoints
- [ ] Setup cache-busting hooks for publish/unpublish
- [ ] Add admin roles (curator/moderator) and RBAC policies

---

## Milestone Checklist

### MVP Ready (End of Phase 3)
- [ ] Users can register and login
- [ ] Organizations can be created and managed
- [ ] Items and locations can be managed
- [ ] Inventory can be tracked and adjusted
- [ ] Recipes can be created and shared
- [ ] Crafts can be planned and tracked
- [ ] Basic UI is functional and usable

### Beta Ready (End of Phase 5)
- [ ] Optimization engine provides source recommendations
- [ ] Goals can be set and tracked
- [ ] Analytics foundation is in place
- [ ] User consent is properly managed
- [ ] Most critical bugs are fixed
- [ ] Basic documentation is complete

### Production Ready (End of Phase 7)
- [ ] Comprehensive test coverage
- [ ] Security hardened
- [ ] Performance optimized
- [ ] Documentation complete
- [ ] Production deployment successful
- [ ] Monitoring in place
- [ ] Backup procedures working

---

## Risk Mitigation

**Technical Risks:**
- **Risk:** FastAPI/React learning curve
  - **Mitigation:** Start with simple examples, allocate extra time for learning
- **Risk:** Database performance with large datasets
  - **Mitigation:** Early indexing strategy, performance testing from Phase 2
- **Risk:** Complexity of optimization algorithms
  - **Mitigation:** Start with simple algorithms, iterate and improve

**Timeline Risks:**
- **Risk:** Scope creep
  - **Mitigation:** Strict adherence to phases, new features go to backlog
- **Risk:** Underestimated task complexity
  - **Mitigation:** Build buffer time into each phase, prioritize MVP features

**Deployment Risks:**
- **Risk:** Production deployment issues
  - **Mitigation:** Thorough testing in staging environment, documented rollback procedure

---

## Success Metrics

**Technical Metrics:**
- Test coverage >80% (backend), >70% (frontend)
- API response time <200ms (p95)
- Page load time <2 seconds
- Zero critical security vulnerabilities
- 99.9% uptime (post-launch)

**User Metrics (Post-Launch):**
- User registration rate
- Active users per week
- Recipes created per user
- Crafts completed per user
- Integration usage rate

---

**End of Implementation Roadmap**

