# SCIMS - Star Citizen Inventory Management System

A comprehensive web-based inventory management system for Star Citizen organizations, designed to help players track resources, plan crafting operations, optimize resource acquisition, and integrate with external tools.

## Features

### Core Pillars

1. **Inventory Tracking & Location Awareness**
   - Track resources and items across multiple locations
   - Real-time inventory state management
   - Location-aware storage tracking (stations, ships, player inventories)

2. **Planning & Goal Management**
   - Plan crafting operations from recipes
   - Track in-progress crafts with real-time status
   - Set and monitor organizational goals with multi-item tracking
   - Track completion outcomes and progress automatically

3. **Resource Optimization Engine**
   - Automatic source determination for materials
   - Smart prioritization: current stocks → other players' available stocks → in-universe sources
   - Cost/benefit analysis for resource acquisition

4. **Open Integration Framework**
   - API-first design with comprehensive REST endpoints
   - Webhook support for real-time updates
   - Data import/export capabilities (CSV, JSON)
   - External tool integration support

5. **Analytics & Improvement**
   - User consent-based analytics with privacy safeguards
   - Usage event tracking (blueprint usage, goal creation, inventory updates)
   - Recipe statistics and popularity tracking
   - Analytics dashboard with insights
   - Privacy-first: IP anonymization, consent management, transparent data collection

## Technology Stack

- **Backend:** FastAPI (Python 3.11+), PostgreSQL 15+, Redis, Celery
- **Frontend:** React 18+ with TypeScript, Vite
- **Infrastructure:** Docker Compose, Nginx
- **Database:** SQLAlchemy ORM, Alembic migrations
- **Authentication:** JWT tokens

## Prerequisites

- **Docker & Docker Compose** (recommended for quick setup)
  - Docker Desktop or Docker Engine 20.10+
  - Docker Compose v2.0+
- **Git** for cloning the repository
- **Optional (for local development):**
  - Python 3.11+ (for backend development)
  - Node.js 20+ and pnpm (for frontend development)

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Comnyando/SCIMS.git
   cd SCIMS
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration if needed
   ```

3. **Start all services:**
   ```bash
   docker compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost/api/v1
   - API Documentation: http://localhost/api/docs
   - Backend Health Check: http://localhost/api/v1/health

### Development Mode

The default `docker-compose.yml` runs in development mode with:
- Hot-reload enabled for both frontend and backend
- Volume mounts for live code changes
- Development-friendly logging

### Production Mode

For a production-like setup:
```bash
docker compose -f docker-compose.prod.yml up --build -d
```

**Note:** Ensure you've configured proper environment variables and secrets before running in production.

## Project Structure

```
SCIMS/
├── backend/              # FastAPI backend application
│   ├── app/             # Application code
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── config.py    # Configuration management
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic
│   ├── alembic/         # Database migrations
│   ├── tests/           # Backend tests
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend application
│   ├── src/            # Source code
│   │   ├── components/ # React components
│   │   ├── pages/      # Page components
│   │   ├── services/   # API services
│   │   ├── hooks/      # React hooks
│   │   └── types/      # TypeScript types
│   ├── public/         # Static assets
│   └── package.json    # Node.js dependencies
├── nginx/              # Nginx configuration
│   └── default.conf    # Reverse proxy config
├── planning/           # Architecture and planning docs
├── docker-compose.yml  # Development Docker Compose
├── docker-compose.prod.yml  # Production Docker Compose
└── .env.example        # Environment variables template
```

## Services

The application runs the following services:

- **PostgreSQL** (port 5432) - Primary database
- **Redis** (port 6379) - Caching and task queue broker
- **Backend API** (port 8000) - FastAPI application
- **Frontend** (port 5173) - Vite dev server (dev mode)
- **Nginx** (ports 80/443) - Reverse proxy and static file server

## Environment Variables

Copy `.env.example` to `.env` and configure as needed. Key variables include:

- Database connection settings
- Redis connection settings
- JWT secrets (generate secure values for production)
- CORS origins
- API URLs

See `.env.example` for a complete list with descriptions.

## Development

### Local Development (Without Docker)

See individual README files for detailed setup:
- [Backend Development Setup](backend/README.md)
- [Frontend Development Setup](frontend/README.md)

### Common Docker Commands

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# Rebuild and start
docker compose up --build

# Stop all services
docker compose down

# View logs
docker compose logs -f [service-name]

# Execute commands in containers
docker compose exec backend python -m alembic upgrade head
docker compose exec frontend pnpm install
```

### Using the `dc` Alias

If you've set up the `dc` alias (see [PowerShell alias setup](#)), you can use:
```bash
dc up --build
dc ps
dc logs -f backend
dc down
```

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory. See [Documentation Index](docs/README.md) for a complete guide.

### Quick Links

- [Installation Guide](docs/getting-started/installation.md) - Complete setup instructions
- [API Usage Examples](docs/examples/api-usage.md) - Practical API examples
- [Deployment Guide](docs/deployment/README.md) - Production deployment
- [Testing Guide](docs/development/testing.md) - Running and writing tests
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute

### User Guides

- [Inventory Management](docs/user-guide/inventory.md) - Managing items and locations
- [Crafting System](docs/user-guide/crafting.md) - Creating and using blueprints
- [Goals & Progress](docs/user-guide/goals.md) - Setting and tracking goals
- [Analytics & Privacy](docs/user-guide/analytics.md) - Analytics features and consent
- [Resource Optimization](docs/user-guide/optimization.md) - Optimization engine
- [Integrations](docs/user-guide/integrations.md) - External integrations
- [Public Commons](docs/user-guide/commons.md) - Community-shared content
- [FAQ](docs/user-guide/faq.md) - Frequently asked questions

## API Documentation

When the backend is running, interactive API documentation is available at:
- **Swagger UI:** http://localhost/api/docs
- **ReDoc:** http://localhost/api/redoc

## Current Status

**Phase 0: Foundation Setup** ✅
- ✅ Repository structure
- ✅ Docker development environment
- ✅ Basic backend and frontend setup
- ✅ Nginx reverse proxy configuration

**Phase 2: Inventory Core** ✅
- ✅ Database schema and migrations
- ✅ Authentication system (JWT-based)
- ✅ Core inventory tracking API
- ✅ Inventory adjustment and transfer operations
- ✅ Stock reservation system
- ✅ Transaction history and audit trail
- ✅ React frontend with TypeScript
- ✅ Blueprint.js component library integration
- ✅ Items, Locations, and Inventory management pages

### Inventory Management Features

The inventory management system is now fully operational:

- **Multi-Location Tracking**: Track items across stations, ships, warehouses, and player inventories
- **Real-Time Stock Levels**: View current quantity, reserved quantity, and available quantity
- **Inventory Adjustments**: Add or remove items with automatic history logging
- **Item Transfers**: Move items between locations with validation
- **Stock Reservations**: Reserve items for planned operations (e.g., crafting)
- **Access Control**: Role-based permissions (viewer, member, owner)
- **Transaction History**: Complete audit trail of all inventory changes
- **Filtering & Search**: Find items by name, location, or ID

**Phase 5: Goals & Analytics** ✅
- ✅ Multi-item goal tracking system
- ✅ Automatic progress calculation and completion detection
- ✅ Analytics foundation with consent management
- ✅ Usage statistics and recipe analytics
- ✅ Privacy safeguards and data anonymization

### Crafting & Blueprints Features

The Blueprints System allows you to:

- **Create Blueprints**: Define crafting recipes with ingredients, output items, and crafting times
- **Browse Blueprints**: Search and filter blueprints by category, visibility, and output item
- **Share Blueprints**: Make blueprints public for community sharing or keep them private
- **Blueprint Details**: View complete blueprint information including ingredients and usage statistics
- **Popular Blueprints**: Discover the most-used blueprints from the community
- **Blueprint Validation**: Automatic validation ensures all referenced items exist
- **Access Control**: Private blueprints are only visible to creators; public blueprints are visible to all authenticated users

All blueprints support:
- Multiple ingredients with customizable quantities
- Optional ingredients for flexible recipes
- Categorization (Weapons, Components, Food, Materials, etc.)
- Usage tracking for popularity metrics
- Full CRUD operations (Create, Read, Update, Delete)

### Goals & Tracking Features

The Goals System enables:

- **Multi-Item Goals**: Track multiple items simultaneously in a single goal
- **Automatic Progress Calculation**: Real-time progress tracking across all accessible inventory locations
- **Progress Visualization**: Individual item progress bars and overall goal completion
- **Automatic Completion**: Goals marked complete when all items reach their targets
- **Personal & Organization Goals**: Create goals for yourself or your organization
- **Target Dates**: Set optional deadlines with countdown tracking
- **Goal Status Tracking**: Active, Completed, and Cancelled states

### Analytics & Privacy Features

The Analytics System provides:

- **Consent-Based Tracking**: Optional analytics that requires explicit user consent
- **Usage Statistics**: View aggregated usage data (events, top blueprints, goal creation patterns)
- **Recipe Analytics**: Detailed statistics for blueprint usage and completion rates
- **Privacy Safeguards**: IP anonymization, user agent truncation, no personal data collection
- **Transparent Control**: Easy consent management with clear explanations of data collection
- **Analytics Dashboard**: Visualize usage patterns and trends

**Phase 6: Integration Framework** ✅
- ✅ Integration service backend
- ✅ Data import/export (CSV, JSON)
- ✅ Webhook support
- ✅ Integration management UI

**Phase 6.5: Public Commons & Moderation** ✅
- ✅ Commons submission system
- ✅ Moderation workflow
- ✅ Public API endpoints
- ✅ Tag management
- ✅ Duplicate detection

**Phase 7: Polish & Production Readiness** 🚧
- ✅ Sub-phase 7.1: Comprehensive Testing (82% coverage)
- 🚧 Sub-phase 7.2: Documentation (in progress)
- ⏳ Sub-phase 7.3: Security & Performance
- ⏳ Sub-phase 7.4: Production Deployment

See [Implementation Roadmap](planning/implementation-roadmap.md) for the complete development plan.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code of conduct
- Development workflow
- Coding standards
- Testing requirements
- Pull request process

Quick start:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

[To be determined]

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Project Repository:** [https://github.com/Comnyando/SCIMS](https://github.com/Comnyando/SCIMS)
