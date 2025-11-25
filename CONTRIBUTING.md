# Contributing to SCIMS

Thank you for your interest in contributing to SCIMS! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background or experience level.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept feedback gracefully

### Unacceptable Behavior

- Harassment or discrimination
- Personal attacks
- Trolling or inflammatory comments
- Any other unprofessional conduct

## Getting Started

### Prerequisites

- Git
- Docker and Docker Compose (recommended)
- Or: Python 3.11+, Node.js 20+, PostgreSQL 15+, Redis 7+

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/SCIMS.git
   cd SCIMS
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/Comnyando/SCIMS.git
   ```

### Development Setup

See [Installation Guide](docs/getting-started/installation.md) for complete setup instructions.

Quick start with Docker:
```bash
cp .env.example .env
docker compose up -d
```

## Development Workflow

### Branch Naming

Use descriptive branch names:
- `feature/add-user-profiles`
- `fix/inventory-calculation-bug`
- `docs/update-api-documentation`
- `refactor/optimize-database-queries`

### Commit Messages

Follow conventional commit format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(inventory): add bulk inventory adjustment endpoint

fix(crafts): correct ingredient reservation calculation

docs(api): update authentication examples
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following coding standards
   - Add tests for new features
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   pytest tests/

   # Frontend tests (when available)
   cd frontend
   pnpm test

   # Linting
   cd backend
   black app/
   mypy app/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Use clear title and description
   - Reference related issues
   - Include screenshots if UI changes
   - Ensure CI checks pass

7. **Respond to Feedback**
   - Address review comments
   - Make requested changes
   - Keep discussion constructive

## Coding Standards

### Python (Backend)

- **Style**: Follow PEP 8
- **Formatting**: Use Black (line length 100)
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Use Google-style docstrings

**Example:**
```python
def calculate_inventory_total(
    location_id: str,
    db: Session,
) -> Decimal:
    """
    Calculate total inventory value for a location.

    Args:
        location_id: UUID of the location
        db: Database session

    Returns:
        Total inventory value as Decimal

    Raises:
        HTTPException: If location not found
    """
    # Implementation
```

### TypeScript/React (Frontend)

- **Style**: Follow ESLint configuration
- **Formatting**: Use Prettier
- **Type Safety**: Use TypeScript strictly
- **Components**: Use functional components with hooks

**Example:**
```typescript
interface InventoryItemProps {
  itemId: string;
  quantity: number;
  onUpdate: (id: string, quantity: number) => void;
}

export function InventoryItem({
  itemId,
  quantity,
  onUpdate,
}: InventoryItemProps): JSX.Element {
  // Implementation
}
```

### Database

- **Migrations**: Use Alembic for all schema changes
- **Naming**: Use snake_case for tables and columns
- **Indexes**: Add indexes for foreign keys and frequently queried columns

## Testing

### Backend Tests

- **Framework**: pytest
- **Coverage**: Maintain >80% coverage
- **Location**: `backend/tests/`
- **Naming**: `test_*.py` files, `test_*` functions

**Running Tests:**
```bash
cd backend
pytest tests/                    # Run all tests
pytest tests/test_auth.py        # Run specific file
pytest tests/ -v --cov=app      # With coverage
```

### Writing Tests

- Test both success and failure cases
- Use fixtures from `conftest.py`
- Mock external dependencies
- Test edge cases

**Example:**
```python
def test_create_item_success(client, auth_headers):
    """Test successful item creation."""
    response = client.post(
        "/api/v1/items",
        headers=auth_headers,
        json={"name": "Test Item", "category": "Test"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"
```

## Documentation

### Code Documentation

- **Docstrings**: All public functions and classes
- **Comments**: Explain "why", not "what"
- **Type Hints**: Use throughout

### User Documentation

- Update user guides when adding features
- Add examples for new functionality
- Include troubleshooting sections

### API Documentation

- FastAPI auto-generates from docstrings
- Add examples to endpoint docstrings
- Update OpenAPI metadata in `main.py`

## Submitting Changes

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] No linter errors
- [ ] Commit messages follow convention

### Pull Request Checklist

- [ ] Clear title and description
- [ ] Related issues referenced
- [ ] Screenshots (for UI changes)
- [ ] Breaking changes documented
- [ ] Migration instructions (if needed)

### Review Process

1. **Automated Checks**: CI runs tests and linting
2. **Code Review**: Maintainers review code
3. **Feedback**: Address review comments
4. **Approval**: At least one maintainer approval
5. **Merge**: Squash and merge (preferred)

## Issue Reporting

### Bug Reports

Include:
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, versions, etc.
- **Screenshots**: If applicable
- **Logs**: Relevant error messages

### Feature Requests

Include:
- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other solutions considered
- **Additional Context**: Any other relevant information

### Issue Templates

Use GitHub issue templates when available:
- Bug Report
- Feature Request
- Documentation
- Question

## Getting Help

- **Documentation**: Check [docs/](docs/) directory
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Questions**: Ask in issues (use "question" label)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Appreciated by the community!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to SCIMS! 🚀

