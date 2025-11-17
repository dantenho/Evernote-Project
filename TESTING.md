# Testing Documentation

## Overview

This project has comprehensive test coverage (99.03%) for the Django learning application backend. The test suite includes unit tests, integration tests, and admin interface tests.

## Test Statistics

- **Total Tests**: 108
- **Coverage**: 99.03%
- **Test Files**: 3
- **Testing Framework**: pytest with pytest-django

## Test Structure

```
learning/tests/
├── __init__.py
├── factories.py           # Factory Boy factories for test data
├── test_models.py         # Unit tests for all 6 models (61 tests)
├── test_admin.py          # Admin interface tests (43 tests)
└── test_integration.py    # Integration tests (18 tests)
```

## Running Tests

### Run All Tests
```bash
python -m pytest
```

### Run Specific Test File
```bash
python -m pytest learning/tests/test_models.py
python -m pytest learning/tests/test_admin.py
python -m pytest learning/tests/test_integration.py
```

### Run Tests with Coverage Report
```bash
python -m pytest --cov=learning --cov-report=term-missing --cov-report=html
```

### Run Tests by Marker
```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Run all tests except slow ones
python -m pytest -m "not slow"
```

### Run Tests in Parallel
```bash
python -m pytest -n auto
```

## Test Categories

### Model Tests (test_models.py)

Comprehensive unit tests for all 6 models:

1. **Area Model** (7 tests)
   - String representation
   - Ordering functionality
   - Field validation
   - Cascade deletion

2. **Topico Model** (6 tests)
   - Foreign key relationships
   - Cascade deletion
   - Ordering within parent

3. **Trilha Model** (7 tests)
   - Multi-level cascade deletion
   - Related name access
   - Ordering

4. **Passo Model** (10 tests)
   - Content type choices (LESSON/QUIZ)
   - Optional fields
   - Conditional relationships

5. **Questao Model** (6 tests)
   - Question-to-quiz relationships
   - Cascade deletion

6. **Alternativa Model** (8 tests)
   - Correct/incorrect alternatives
   - Boolean logic validation

7. **Model Relationships** (3 tests)
   - Full cascade delete chains
   - Complex hierarchies
   - Related name bidirectional access

### Admin Interface Tests (test_admin.py)

Tests for Django admin configuration:

1. **Admin Registration** (7 tests)
   - All models registered
   - Correct admin classes applied

2. **Admin Configuration** (20 tests)
   - List display fields
   - List filters
   - Inline configurations

3. **Dynamic Behavior** (6 tests)
   - Conditional inlines (quiz vs lesson)
   - Multi-level filtering

4. **Admin Relationships** (5 tests)
   - Inline display functionality
   - Related object access

5. **Ordering** (5 tests)
   - Inline ordering by order field

### Integration Tests (test_integration.py)

End-to-end workflow tests:

1. **Learning Path Creation** (3 tests)
   - Complete hierarchy creation
   - Quiz with questions and alternatives
   - Multi-area platform

2. **Cascade Deletion** (3 tests)
   - Full hierarchy deletion
   - Selective deletion
   - Quiz deletion with all related objects

3. **Learning Path Navigation** (3 tests)
   - Ordered content traversal
   - Cross-hierarchy queries
   - Filtering by content type

4. **Quiz Validation** (2 tests)
   - Valid quiz structure
   - Multiple questions per quiz

5. **Content Organization** (3 tests)
   - Reordering content
   - Moving content between parents
   - Complex multi-level hierarchies

6. **Data Integrity** (4 tests)
   - Orphan prevention
   - Bidirectional relationships
   - Bulk operations
   - Transaction rollback

## Test Coverage Report

```
Name                   Stmts   Miss   Cover   Missing
-----------------------------------------------------
learning/__init__.py       0      0 100.00%
learning/admin.py         51      0 100.00%
learning/models.py        51      0 100.00%
learning/views.py          1      1   0.00%   1
-----------------------------------------------------
TOTAL                    103      1  99.03%
```

The only uncovered line is in `views.py` which contains only an import statement (views are not yet implemented).

## Continuous Integration

Tests automatically run on:
- Every push to `main`, `develop`, or `claude/**` branches
- Every pull request to `main` or `develop`

### CI/CD Workflow

The GitHub Actions workflow:
1. Sets up Python 3.11 and 3.12
2. Installs dependencies
3. Runs database migrations
4. Executes all tests with coverage
5. Uploads coverage reports
6. Checks coverage threshold (80% minimum)
7. Runs code quality checks (flake8, black, isort)

## Test Data Factories

Factory Boy factories provide convenient test data generation:

```python
from learning.tests.factories import (
    AreaFactory,
    TopicoFactory,
    TrilhaFactory,
    LessonFactory,
    QuizFactory,
    QuestaoFactory,
    AlternativaFactory,
    CorrectAlternativaFactory,
)

# Create test data
area = AreaFactory(title="Python")
quiz = QuizFactory()
question = QuestaoFactory(step=quiz)
correct = CorrectAlternativaFactory(question=question)
```

## Writing New Tests

### Example Model Test

```python
@pytest.mark.django_db
@pytest.mark.unit
class TestMyModel:
    def test_my_feature(self):
        """Test description."""
        obj = MyModelFactory()
        assert obj.field == expected_value
```

### Example Integration Test

```python
@pytest.mark.django_db
@pytest.mark.integration
class TestMyWorkflow:
    def test_complete_workflow(self):
        """Test complete workflow."""
        # Create hierarchy
        area = AreaFactory()
        topico = TopicoFactory(area=area)
        # Test workflow
        assert area.topics.count() == 1
```

## Best Practices

1. **Use Factories**: Always use Factory Boy factories instead of creating models directly
2. **Mark Tests**: Use `@pytest.mark.unit` or `@pytest.mark.integration` markers
3. **Database Access**: Use `@pytest.mark.django_db` for tests that need database access
4. **Descriptive Names**: Use clear, descriptive test function names
5. **Test Isolation**: Each test should be independent and not rely on other tests
6. **Coverage**: Aim for 80%+ coverage on new code

## Debugging Tests

### Run with verbose output
```bash
python -m pytest -vv
```

### Run with print statements
```bash
python -m pytest -s
```

### Run specific test
```bash
python -m pytest learning/tests/test_models.py::TestAreaModel::test_create_area
```

### Stop on first failure
```bash
python -m pytest -x
```

### Debug with pdb
```bash
python -m pytest --pdb
```

## Future Test Additions

As the application grows, consider adding:

1. **View/API Tests**: When views and APIs are implemented
2. **Authentication Tests**: When user authentication is added
3. **Performance Tests**: For database query optimization
4. **Load Tests**: For API endpoint performance
5. **Security Tests**: For permission and validation testing
