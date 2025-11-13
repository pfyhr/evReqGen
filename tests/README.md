# Test Suite for evReqGen

This directory contains comprehensive tests for the Electric Vehicle Requirements Generator (evReqGen) application.

## Test Structure

- `test_dragraceSim.py` - Tests for physics simulation and optimization algorithms
- `test_jsonwriter.py` - Tests for CSV to JSON data conversion utilities
- `test_flaskpage.py` - Tests for Flask web application endpoints
- `conftest.py` - Shared pytest fixtures and configuration

## Running Tests

### Install Dependencies

First, install the required testing dependencies:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see the coverage report.

### Run Specific Test Files

```bash
# Test only physics simulation
pytest tests/test_dragraceSim.py

# Test only Flask routes
pytest tests/test_flaskpage.py

# Test only data conversion
pytest tests/test_jsonwriter.py
```

### Run Specific Test Classes

```bash
pytest tests/test_dragraceSim.py::TestTopGradeSpeed
pytest tests/test_dragraceSim.py::TestAccelerateVehicle
```

### Run Specific Tests

```bash
pytest tests/test_dragraceSim.py::TestTopGradeSpeed::test_zero_velocity
```

### Verbose Output

```bash
pytest -v
```

### Show Print Statements

```bash
pytest -s
```

## Test Coverage

The test suite aims for high coverage of:

1. **Physics Functions** (`dragraceSim.py`)
   - `topGradeSpeed()` - Wheel torque calculations
   - `tractionMax()` - Weight transfer and traction limits
   - `accelerateVehicle()` - Main simulation with power optimization
   - `sim_json()` - Output formatting for web interface

2. **Data Conversion** (`jsonwriter.py`)
   - `output_json()` - CSV to JSON conversion
   - `glob_csvs()` - Batch file processing

3. **Web API** (`flaskpage.py`)
   - Route handlers
   - Parameter parsing
   - Error handling

## Key Test Categories

### Unit Tests
- Individual function behavior
- Edge cases and boundary conditions
- Parameter validation
- Numeric precision

### Integration Tests
- End-to-end simulation workflow
- Flask API with mocked simulation
- File I/O operations

### Physics Validation Tests
- Aerodynamic drag (v² relationship)
- Rolling resistance
- Grade resistance
- Weight transfer dynamics
- Drivetrain types (AWD, FWD, RWD)

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `standard_vehicle_params` - Default EV parameters
- `light_vehicle_params` - Lightweight vehicle configuration
- `physics_constants` - Standard physics constants

## Continuous Integration

Tests should be run in CI/CD pipelines before merging pull requests:

```bash
pytest --cov=. --cov-fail-under=80
```

This ensures at least 80% code coverage is maintained.

## Writing New Tests

When adding new functionality:

1. Add corresponding tests in the appropriate test file
2. Use descriptive test names: `test_<what>_<condition>_<expected>`
3. Include docstrings explaining what is being tested
4. Use fixtures for common test data
5. Test both success and failure cases
6. Verify edge cases and boundary conditions

## Troubleshooting

### Import Errors

If you get import errors, make sure the parent directory is in the Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Missing Dependencies

Install all required packages:

```bash
pip install flask numpy sympy matplotlib pytest pytest-cov pytest-mock
```

### Test Failures

Run with verbose output to see detailed failure information:

```bash
pytest -vv --tb=long
```
