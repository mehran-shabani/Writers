# Contributing to Writers Notetaker

Thank you for your interest in contributing to Writers Notetaker! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## Getting Started

1. **Fork the repository** and clone your fork:
   ```bash
   git clone https://github.com/yourusername/writers-notetaker.git
   cd writers-notetaker
   ```

2. **Set up the development environment**:
   ```bash
   cp .env.example .env
   make build
   make up
   make migrate
   ```

3. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

## Development Workflow

1. Make your changes in your feature branch
2. Write or update tests as needed
3. Ensure all tests pass: `make test`
4. Ensure code quality checks pass (linting, formatting)
5. Commit your changes following our [commit message conventions](#commit-messages)
6. Push to your fork and submit a pull request

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This leads to more readable messages and allows us to generate changelogs automatically.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (white-space, formatting, etc)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Changes to build system or dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files

### Scopes

Use the service name or area of change:
- `asr`: ASR service changes
- `nlp`: NLP service changes
- `backend`: Backend API changes
- `frontend`: Frontend changes
- `worker`: Celery worker changes
- `infra`: Infrastructure changes
- `docs`: Documentation changes

### Examples

```bash
feat(asr): add support for Persian dialect detection

fix(nlp): resolve memory leak in text processing pipeline

docs(readme): update installation instructions for GPU setup

refactor(backend): simplify authentication middleware

perf(worker): optimize task queue processing

test(nlp): add integration tests for summarization endpoint
```

### Breaking Changes

For breaking changes, add `BREAKING CHANGE:` in the footer or append `!` after the type/scope:

```bash
feat(api)!: change authentication endpoint structure

BREAKING CHANGE: The /auth/login endpoint now requires email instead of username
```

## Pull Request Process

1. **Update documentation**: Ensure README and relevant docs reflect your changes
2. **Add tests**: All new features must include appropriate tests
3. **Pass CI checks**: Ensure all automated checks pass
4. **Request review**: Assign reviewers familiar with the affected services
5. **Address feedback**: Respond to review comments and make necessary changes
6. **Squash commits** (if requested): We may ask you to squash commits before merging

### PR Title Format

Use the same conventional commit format for PR titles:
```
feat(nlp): add Persian text summarization
```

## Coding Standards

### Python (Backend, Workers, Services)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where applicable
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `pylint` or `flake8` for linting

### TypeScript/JavaScript (Frontend)

- Follow the project's ESLint configuration
- Use TypeScript for all new code
- Follow React best practices and hooks guidelines
- Use Prettier for formatting

### Docker

- Multi-stage builds where appropriate
- Minimize image size
- Use `.dockerignore` files
- Pin dependency versions

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run tests for specific service
make test-backend
make test-frontend
make test-asr
make test-nlp

# Run with coverage
make test-coverage
```

### Writing Tests

- Write unit tests for all business logic
- Write integration tests for API endpoints
- Write end-to-end tests for critical user flows
- Aim for >80% code coverage for new code
- Use meaningful test names that describe what's being tested

### Test Structure

```python
def test_feature_name_should_expected_behavior():
    # Arrange
    setup_test_data()
    
    # Act
    result = function_to_test()
    
    # Assert
    assert result == expected_value
```

## Documentation

- Update README.md for user-facing changes
- Update docs/ for architectural or API changes
- Include inline comments for complex logic
- Update API documentation if endpoints change

## Service-Specific Guidelines

### ASR Service
- Test with various audio formats and qualities
- Consider GPU memory constraints
- Document performance characteristics

### NLP Service
- Test with Persian text samples
- Validate UTF-8 encoding handling
- Document model versions and requirements

### Frontend
- Ensure responsive design
- Test in major browsers
- Follow accessibility guidelines (WCAG 2.1)

### Backend API
- Follow RESTful conventions
- Version API endpoints appropriately
- Document all endpoints in OpenAPI/Swagger format

## Getting Help

- Check existing documentation in `/docs`
- Search existing issues and discussions
- Ask questions in GitHub Discussions
- Reach out to maintainers if needed

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Writers Notetaker! 🎉

