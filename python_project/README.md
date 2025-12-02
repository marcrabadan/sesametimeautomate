# Sesame Time Automation

Automation tool for Sesame Time tracking system using Poetry for dependency management.

## Prerequisites

- Python 3.9+
- Poetry (install from https://python-poetry.org/docs/#installation)

## Installation

1. Clone the repository
2. Navigate to the project directory:
   ```bash
   cd /Users/marc.rabadan/Documents/MyProjects/sesame_automate/python_project
   ```

3. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

4. Copy the environment file and configure your credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your Sesame credentials
   ```

## Usage

### Using Poetry

Run the application using Poetry:
```bash
poetry run sesame-automate
```

Or activate the virtual environment and run directly:
```bash
poetry shell
python -m sesame_automate.main
```

### Development

Install development dependencies:
```bash
poetry install --with dev
```

Run tests:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=sesame_automate --cov-report=html
```

Run specific test file:
```bash
poetry run pytest tests/test_login_runnable.py
```

Run tests with specific markers:
```bash
poetry run pytest -m "not slow"  # Skip slow tests
poetry run pytest -m "unit"      # Run only unit tests
```

Format code:
```bash
poetry run black .
```

Lint code:
```bash
poetry run flake8
```

## Environment Variables

Set these variables in your `.env` file:

```env
BASE_URL=https://back-eu2.sesametime.com
SESAME_EMAIL=your.email@example.com
SESAME_PASSWORD=your_password

# Optional: Cron schedules for automation
IN_TIME_CRON=0 9 * * 1-5
OUT_TIME_CRON=0 18 * * 1-5
BREAK_START_CRON=0 13 * * 1-5
BREAK_END_CRON=0 14 * * 1-5
BREAK_NAME=Lunch
```

## Project Structure

```
sesame_automate/
├── models/
│   ├── runnable.py          # Base abstract class
│   └── runnable_sequence.py # Pipeline implementation
└── runnables/
    ├── sesame_time_login_runnable.py
    ├── sesame_time_me_info_runnable.py
    ├── sesame_time_check_in_runnable.py
    ├── sesame_time_check_out_runnable.py
    ├── sesame_time_work_break_runnable.py
    └── sesame_time_assigned_work_check_types_runnable.py
```