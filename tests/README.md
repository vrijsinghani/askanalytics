# Testing Structure

This directory contains tests for the AskAnalytics project. The tests are organized into the following directories:

## Directory Structure

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for testing multiple components together
- `scripts/`: Test scripts for manual testing and verification

## Running Tests

### Unit Tests

Run all unit tests:

```bash
python manage.py test tests.unit
```

Run a specific unit test:

```bash
python manage.py test tests.unit.test_module
```

### Integration Tests

Run all integration tests:

```bash
python manage.py test tests.integration
```

Run a specific integration test:

```bash
python manage.py test tests.integration.test_module
```

### Test Scripts

Test scripts are meant to be run manually for verification purposes. They are not part of the automated test suite.

Example:

```bash
# Run the settings test script
python manage.py shell < tests/scripts/test_settings.py
```

## Writing Tests

### Unit Tests

Unit tests should focus on testing a single component in isolation. They should be fast and not depend on external services.

Example:

```python
from django.test import TestCase
from myapp.models import MyModel

class MyModelTestCase(TestCase):
    def setUp(self):
        self.model = MyModel.objects.create(name="Test")

    def test_model_name(self):
        self.assertEqual(self.model.name, "Test")
```

### Integration Tests

Integration tests should test the interaction between multiple components. They may depend on external services.

Example:

```python
from django.test import TestCase
from django.urls import reverse
from myapp.models import MyModel

class MyViewTestCase(TestCase):
    def setUp(self):
        self.model = MyModel.objects.create(name="Test")

    def test_view_returns_model(self):
        response = self.client.get(reverse('myapp:detail', args=[self.model.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.model)
```

### Test Scripts

Test scripts are Python scripts that can be run manually to verify specific functionality. They should be well-documented and include clear instructions for running them.

Example:

```python
"""
Test script to verify some functionality.

Run with: python manage.py shell < tests/scripts/my_test_script.py
"""

# Test code here
```
