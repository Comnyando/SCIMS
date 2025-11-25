# SCIMS Documentation

Welcome to the SCIMS (Star Citizen Inventory Management System) documentation. This index will help you find the information you need.

## Quick Start

- **New Users**: Start with the [Getting Started Guide](getting-started/installation.md)
- **Developers**: See [Development Documentation](development/)
- **API Users**: Check the [API Documentation](#api-documentation) section below

## Documentation Structure

### Getting Started

- [Installation Guide](getting-started/installation.md) - Complete setup instructions for development and production

### User Guides

Step-by-step guides for using SCIMS features:

- [Inventory Management](user-guide/inventory.md) - Managing items, locations, and stock
- [Crafting System](user-guide/crafting.md) - Creating blueprints and managing crafts
- [Crafting Examples](user-guide/crafting-examples.md) - Real-world crafting scenarios
- [Goals & Progress Tracking](user-guide/goals.md) - Setting and tracking organizational goals
- [Resource Optimization](user-guide/optimization.md) - Using the optimization engine
- [Analytics & Privacy](user-guide/analytics.md) - Analytics features and consent management
- [Integrations](user-guide/integrations.md) - Setting up external integrations
- [Public Commons](user-guide/commons.md) - Community-shared content
- [FAQ](user-guide/faq.md) - Frequently asked questions
- [Email Setup](user-guide/email-setup.md) - Email provider configuration (SPF/DKIM/DMARC)

### Developer Documentation

Technical documentation for contributors and integrators:

- [Testing Guide](development/testing.md) - Running tests and writing new tests
- [Load Testing](development/load-testing.md) - Load testing with Locust and k6
- [Database Schema](development/database-schema.md) - Complete database structure
- [Performance Optimization](development/performance-optimization.md) - Performance tuning and optimization strategies
- [Email Webhook Validation](development/email-webhook-validation.md) - Validating email bounce/complaint handling
- [Backup & Restore Validation](development/backup-restore-validation.md) - Backup procedures and restore validation
- [Architecture Overview](../planning/architecture.md) - System architecture and design decisions
- [Contributing Guidelines](../CONTRIBUTING.md) - How to contribute to the project

### Deployment

- [Deployment Guide](deployment/README.md) - Production deployment procedures
- [CI/CD Setup](ci-cd-setup.md) - Continuous integration and deployment
- [Running CI Locally](running-ci-locally.md) - Testing CI checks locally

### API Documentation

#### Interactive Documentation

When the backend is running, interactive API documentation is available:

- **Swagger UI**: http://localhost:8000/docs (or http://localhost/api/docs in production)
- **ReDoc**: http://localhost:8000/redoc (or http://localhost/api/redoc in production)
- **OpenAPI JSON**: http://localhost:8000/openapi.json

#### API Usage Examples

- [API Usage Examples](examples/api-usage.md) - Complete API usage guide with examples
- [Optimization Examples](examples/optimization-examples.md) - Using the optimization API

### Additional Resources

- [Implementation Roadmap](../planning/implementation-roadmap.md) - Development timeline and phases
- [Architecture Decisions](../planning/decisions.md) - Key technical decisions
- [Contributing Guidelines](../CONTRIBUTING.md) - How to contribute to the project
- [Backend README](../backend/README.md) - Backend-specific documentation
- [Frontend README](../frontend/README.md) - Frontend-specific documentation

## Documentation Standards

All documentation follows these standards:

- **Code Examples**: All examples are tested and working
- **Step-by-Step**: Clear instructions with prerequisites listed
- **Troubleshooting**: Common issues and solutions included
- **Version Numbers**: Dependency versions are current
- **Links**: All internal and external links are verified

## Contributing to Documentation

When adding or updating documentation:

1. Follow the existing structure and format
2. Include code examples where applicable
3. Add troubleshooting sections for complex topics
4. Update this index if adding new major sections
5. Test all code examples before committing

## Getting Help

- **Issues**: Report documentation issues on GitHub
- **Questions**: Check the FAQ sections in relevant guides
- **Contributions**: See [Contributing Guidelines](../CONTRIBUTING.md)

---

**Last Updated**: See git history for latest changes

