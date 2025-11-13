import pytest
import sys
from pathlib import Path

# Add parent directory to path so tests can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def standard_vehicle_params():
    """Standard EV parameters for testing."""
    return {
        'mass': 1800.0,
        'Cd': 0.3,
        'frontArea': 2.0,
        'grade': 0.0,
        'v0': 0.0,
        'v1': 100.0 / 3.6,  # 100 km/h in m/s
        'cgh': 0.6,
        'wtRearFrac': 0.56,
        'wheelbase': 2.5,
        'driveWheel': 'RWD',
        'desiredAccTime': 9.0,
        'muTire': 0.9,
        'wheelRadius': 0.3,
        'name': 'TestVehicle'
    }


@pytest.fixture
def light_vehicle_params():
    """Lighter EV with lower drag."""
    return {
        'mass': 1200.0,
        'Cd': 0.25,
        'frontArea': 1.8,
        'grade': 0.0,
        'v0': 0.0,
        'v1': 80.0 / 3.6,
        'cgh': 0.5,
        'wtRearFrac': 0.6,
        'wheelbase': 2.3,
        'driveWheel': 'FWD',
        'desiredAccTime': 7.0,
        'muTire': 0.85,
        'wheelRadius': 0.28,
        'name': 'LightVehicle'
    }


@pytest.fixture
def physics_constants():
    """Standard physics constants used in simulation."""
    return {
        'rhoAir': 1.2,
        'g': 9.81,
        'Cr': 0.01
    }
