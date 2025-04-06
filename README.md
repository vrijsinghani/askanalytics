# AskAnalytics

AskAnalytics is a Django-based analytics platform with multi-tenancy support, built on top of the SoftUI Dashboard Pro template.

## Features

- Multi-tenancy via organizations
- User authentication and authorization
- API token management
- WebSocket support for real-time updates
- HTMX-first approach for interactive UI
- Dark mode support
- Secure file storage

## Project Structure

- `apps/` - Django applications
  - `api/` - API endpoints
  - `charts/` - Chart components
  - `common/` - Shared utilities
  - `file_manager/` - File management
  - `organizations/` - Multi-tenancy support
  - `tables/` - Table components
  - `tasks/` - Background tasks
  - `users/` - User management
  - `websockets/` - WebSocket consumers
- `core/` - Core project settings
- `docs/` - Project documentation
- `static/` - Static assets
- `templates/` - HTML templates
- `tests/` - Test suite

## Documentation

Detailed documentation can be found in the `docs/` directory:

- [Migration Plan](docs/migration-plan.md)
- [Developer Standards](docs/developer-standards.md)
- [Deployment Guide](docs/deployment-guide.md)
- [Component Conversion](docs/component-conversion.md)
- [Checklist](docs/checklist.md)
- [Memory](docs/memory.md)

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vrijsinghani/askanalytics.git
   cd askanalytics
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Create a `.env` file with your environment variables (see `.env.example`).

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
