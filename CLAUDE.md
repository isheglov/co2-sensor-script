# CO2 Sensor Script Project Guidelines

## Development Commands
- Environment setup: `python -m venv hid_env && source hid_env/bin/activate && pip install -r requirements.txt`
- Run CO2 sensor script: `python co2_sensor.py`
- Run web service: `python web_service/app.py`
- Run database creation: `python create_db.py`
- Run monitoring script (on Raspberry Pi): `python automation/monitor.py`
- Lint code: `pylint co2_sensor.py web_service/app.py automation/monitor.py`
- Run tests: `pytest tests/`
- Run single test: `pytest tests/test_co2_sensor.py::TestCO2Sensor::test_parse_data_co2`
- Test with coverage: `pytest tests/ --cov=. --cov-report=term`

## Code Style Guidelines
- Follow PEP 8 style guidelines
- Docstrings: Use Google-style for functions and classes
- Imports: Organize in order: standard library, third-party, local application
- Type hints: Document parameter types in docstrings
- Error handling: Use try/except blocks with specific exceptions, log errors appropriately
- Variable naming: Use snake_case for variables and functions, CamelCase for classes
- Constants: Use UPPERCASE_WITH_UNDERSCORES
- Database path should be accessed from environment variables via `os.getenv('DB_PATH')`
- Prefer context managers (`with` statements) for database connections where appropriate
- Testing: Write unit tests using unittest or pytest, mock external dependencies
- Always ensure there is a newline at end of file

## Continuous Integration
- All code is automatically tested via GitHub Actions
- Pull requests must pass all tests before being merged
- Two workflows run on push and pull requests:
  1. Pylint: Checks code quality
  2. Pytest: Runs tests and generates coverage reports
- CI workflow files are in `.github/workflows/`