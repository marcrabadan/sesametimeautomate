# Sesame Time Automate

An automation tool for the Sesame Time tracking system that handles automatic check-ins, check-outs, and break management through scheduled cron jobs.

## Overview

Sesame Time Automate streamlines time tracking by automating routine operations like employee check-ins, check-outs, and break management. Instead of manual interactions with the Sesame Time system, this tool runs scheduled jobs that handle these tasks automatically based on configurable cron schedules.

## Features

- **Automated Check-In**: Automatically check employees in at configured times
- **Automated Check-Out**: Automatically check employees out at configured times
- **Break Management**: Automatically start and end work breaks on schedule
- **State Tracking**: Maintains employee work state throughout the day
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Error Handling**: Graceful error handling with automatic recovery
- **Runnable Chain Pattern**: Composable task execution using a runnable sequence pattern

## Project Structure

```
sesametimeautomate/
├── python_project/
│   ├── sesame_automate/
│   │   ├── main.py                    # Application entry point with scheduler
│   │   ├── models/
│   │   │   ├── runnable_sequence.py   # Runnable pattern implementation
│   │   │   └── enums/
│   │   │       └── state.py           # Work state enumeration
│   │   └── runnables/
│   │       ├── sesame_time_login_runnable.py
│   │       ├── sesame_time_me_info_runnable.py
│   │       ├── sesame_time_work_break_runnable.py
│   │       ├── sesame_time_assigned_work_check_types_runnable.py
│   │       ├── sesame_time_check_in_runnable.py
│   │       └── sesame_time_check_out_runnable.py
│   ├── pyproject.toml
│   └── pytest.ini
└── README.md
```

## Installation

### Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sesametimeautomate
   ```

2. Navigate to the project directory:
   ```bash
   cd python_project
   ```

3. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

## Configuration

Create a `.env` file in the `python_project` directory with the environment variables used by the application.

Notes about cron fields and formats
- The scheduler uses standard crontab expressions in the form: `minute hour day month weekday`.
- Use a site like https://crontab.guru to build and verify expressions.
- `IN_TIME_CRON` and `OUT_TIME_CRON` may contain multiple cron expressions separated by a comma (`,`) to schedule the same job at several times. Do not include extra commas; avoid spaces around the comma for reliability (for example: `3 9 * * 1-4,0 8 * * 5`).
- `BREAK_START_CRON` and `BREAK_END_CRON` expect a single cron expression.
- `TIME_ZONE` controls the scheduler timezone (e.g., `Europe/Madrid`, `America/New_York`).

Example `.env` file:

```env
# API / authentication
BASE_URL=https://back-eu2.sesametime.com
COOKIE_DOMAIN=back-eu2.sesametime.com
SESAME_TIME_USERNAME=your_username_here
SESAME_TIME_PASSWORD=your_password_here

# Scheduler configuration
TIME_ZONE=Europe/Madrid

# Cron schedules (standard crontab format: minute hour day month weekday)
# - IN_TIME_CRON and OUT_TIME_CRON can contain multiple comma-separated crons.
# - BREAK_START_CRON and BREAK_END_CRON are single crons.
# Examples:
#   - Workdays at 09:03 (Mon–Thu) and at 08:00 on Friday:
#       IN_TIME_CRON=3 9 * * 1-4,0 8 * * 5
#   - Check out at 18:03 (Mon–Thu) and at 15:00 on Friday:
#       OUT_TIME_CRON=3 18 * * 1-4,0 15 * * 5
IN_TIME_CRON=3 9 * * 1-4,0 8 * * 5
OUT_TIME_CRON=3 18 * * 1-4,0 15 * * 5
BREAK_START_CRON=0 13 * * 1-4
BREAK_END_CRON=0 14 * * 1-4

# Optional settings
REMOTE_WORK_DAYS=Tuesday, Thursday, Friday
BREAK_NAME=Comiendo
```

### Environment Variables Explained

| Variable | Description | Required |
|----------|-------------|----------|
| `SESAME_TIME_API_KEY` | API key for Sesame Time service | Yes |
| `SESAME_TIME_USERNAME` | Username for Sesame Time login | Yes |
| `SESAME_TIME_PASSWORD` | Password for Sesame Time login | Yes |
| `TIME_ZONE` | Timezone for scheduler (e.g., Europe/Stockholm, America/New_York) | Yes |
| `IN_TIME_CRON` | Cron expression for check-in schedule | Yes |
| `OUT_TIME_CRON` | Cron expression for check-out schedule | Yes |
| `BREAK_START_CRON` | Cron expression for break start | Yes |
| `BREAK_END_CRON` | Cron expression for break end | Yes |

## Usage

### Running the Application

Start the automation service:

```bash
poetry run sesame-automate
```

Or run the main module directly:

```bash
poetry run python -m sesame_automate.main
```

The application will:
1. Initialize the scheduler with your configured timezone
2. Perform an initial welcome setup (login, fetch user info, set up break schedule, etc.)
3. Schedule background jobs according to your cron expressions
4. Run continuously and execute scheduled tasks

### Running Tests

```bash
poetry run pytest
```

Run with coverage:

```bash
poetry run pytest --cov=sesame_automate
```

## Architecture

### Runnable Pattern

This project uses a composable "runnable" pattern similar to LangChain's LCEL, allowing tasks to be chained together:

```python
# Tasks are chained using the | operator
runnable = task1 | task2 | task3
result = runnable.invoke(initial_data)
```

Each runnable receives input data, processes it, and passes the output to the next runnable in the chain.

### Available Runnables

- **SesameTimeLoginRunnable**: Authenticates with the Sesame Time API
- **SesameTimeMeInfoRunnable**: Fetches current user information
- **SesameTimeWorkBreakRunnable**: Manages work break configuration
- **SesameTimeAssignedWorkCheckTypesRunnable**: Retrieves work assignment details
- **SesameTimeCheckInRunnable**: Performs employee check-in
- **SesameTimeCheckOutRunnable**: Performs employee check-out

### Scheduled Jobs

The application runs four scheduled jobs:

1. **Check-In Job** (`IN_TIME_CRON`)
   - Logs in and checks in the employee

2. **Check-Out Job** (`OUT_TIME_CRON`)
   - Logs in and checks out the employee

3. **Break Start Job** (`BREAK_START_CRON`)
   - Starts work break period

4. **Break End Job** (`BREAK_END_CRON`)
   - Ends work break period

## Logging

Logs are written to both console and file:
- **Console**: Real-time log output
- **File**: `logs/sesame_automate.log` - Persistent log file

Log level is set to `INFO` by default. Adjust in `main.py` to change verbosity.

## Troubleshooting

### Missing Environment Variables

If you see warnings about missing cron expressions:
```
WARNING - IN_TIME_CRON not set. Please set it in the environment variables...
```

Ensure all required cron variables are set in your `.env` file.

### API Authentication Errors

Verify that your Sesame Time credentials are correct:
- Check `SESAME_TIME_USERNAME`
- Check `SESAME_TIME_PASSWORD`
- Check `SESAME_TIME_API_KEY`

### Scheduler Not Running

Ensure the application has:
- Correct timezone set (valid timezone string)
- Valid cron expressions
- Proper network connectivity to Sesame Time API

## Dependencies

- **requests** (^2.31.0) - HTTP client library
- **python-dotenv** (^1.0.0) - Environment variable management
- **apscheduler** (^3.10.4) - Job scheduling library
- **pytest** (^7.4.0) - Testing framework
- **pytest-cov** (^4.1.0) - Coverage reporting
- **requests-mock** (^1.11.0) - HTTP mocking for tests

## Development

### Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting

Format code:
```bash
poetry run black .
```

Lint code:
```bash
poetry run flake8 .
```

### Adding New Features

1. Create a new runnable class in `sesame_automate/runnables/`
2. Implement the `Runnable` interface with an `execute()` method
3. Chain it with other runnables in `main.py`
4. Add corresponding tests in the test suite

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code is formatted with Black
- No linting errors from Flake8
- Meaningful commit messages

## License

See LICENSE file for details.

## Support

For issues or questions, please open an issue in the repository.

