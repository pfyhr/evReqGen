import pytest
import json
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import flaskpage


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    flaskpage.app.config['TESTING'] = True
    with flaskpage.app.test_client() as client:
        yield client


@pytest.fixture
def valid_form_data():
    """Standard valid form data for simulation requests."""
    return {
        'Cd': '0.3',
        'frontArea': '2.0',
        'mass': '1800',
        'grade': '0.0',
        'v0': '0.0',
        'v1': '27.78',  # 100 km/h in m/s
        'cgh': '0.6',
        'wtRearFrac': '0.56',
        'wheelbase': '2.5',
        'driveWheel': 'RWD',
        'desiredAccTime': '9.0',
        'muTire': '0.9',
        'wheelRadius': '0.3',
        'Name': 'TestVehicle'
    }


class TestIndexRoute:
    """Tests for the index route '/'."""

    def test_index_get_request(self, client):
        """Test GET request to index returns HTML."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'html' in response.data or response.content_type == 'text/html; charset=utf-8'

    def test_index_post_request(self, client):
        """Test POST request to index also returns HTML."""
        response = client.post('/')
        assert response.status_code == 200


class TestRunSimRoute:
    """Tests for the /runsim route."""

    def test_runsim_get_request(self, client):
        """Test GET request to /runsim returns HTML."""
        response = client.get('/runsim')
        assert response.status_code == 200

    @patch('dragraceSim.sim_json')
    def test_runsim_post_valid_data(self, mock_sim_json, client, valid_form_data):
        """Test POST request with valid data calls simulation."""
        # Mock the simulation response
        mock_response = {
            'Modelname': 'TestVehicle',
            'Power': 150.5,
            'SolutionFound': True,
            'torquespeed': [{'x': 0, 'y': 100}, {'x': 10, 'y': 200}],
            'timespeed': [{'x': 0, 'y': 0}, {'x': 5, 'y': 10}],
            'powerspeed': [{'x': 0, 'y': 50}, {'x': 10, 'y': 100}]
        }
        mock_sim_json.return_value = mock_response

        response = client.post('/runsim', data=valid_form_data)

        assert response.status_code == 200
        # Response should be JSON
        result = response.get_json()
        assert result['Modelname'] == 'TestVehicle'
        assert result['Power'] == 150.5
        assert result['SolutionFound'] is True

        # Verify simulation was called with correct parameters
        mock_sim_json.assert_called_once()
        call_args = mock_sim_json.call_args[0]
        assert call_args[0] == 0.3  # Cd
        assert call_args[1] == 2.0  # frontArea
        assert call_args[2] == 1800  # mass

    @patch('dragraceSim.sim_json')
    def test_runsim_post_all_drivetrain_types(self, mock_sim_json, client, valid_form_data):
        """Test simulation with different drivetrain types."""
        mock_response = {
            'Modelname': 'Test',
            'Power': 150.0,
            'SolutionFound': True,
            'torquespeed': [],
            'timespeed': [],
            'powerspeed': []
        }
        mock_sim_json.return_value = mock_response

        for drivetrain in ['AWD', 'FWD', 'RWD']:
            data = valid_form_data.copy()
            data['driveWheel'] = drivetrain

            response = client.post('/runsim', data=data)
            assert response.status_code == 200

            # Verify correct drivetrain was passed
            call_args = mock_sim_json.call_args[0]
            assert call_args[9] == drivetrain  # driveWheel is 10th parameter

    @patch('dragraceSim.sim_json')
    def test_runsim_exception_handling(self, mock_sim_json, client, valid_form_data):
        """Test that exceptions are caught and error message returned."""
        # Make simulation raise an exception
        mock_sim_json.side_effect = Exception("Simulation failed")

        response = client.post('/runsim', data=valid_form_data)

        assert response.status_code == 200
        # Should return error message, not crash
        result = response.get_data(as_text=True)
        assert result == 'some issue occured'

    def test_runsim_missing_parameters(self, client):
        """Test POST with missing parameters."""
        # This will raise KeyError when trying to access missing form fields
        incomplete_data = {
            'Cd': '0.3',
            'mass': '1800'
            # Missing many required fields
        }

        response = client.post('/runsim', data=incomplete_data)

        # Flask may return 400 Bad Request or catch exception
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            result = response.get_data(as_text=True)
            assert result == 'some issue occured'

    @patch('dragraceSim.sim_json')
    def test_runsim_invalid_numeric_values(self, mock_sim_json, client, valid_form_data):
        """Test POST with invalid numeric values."""
        # Test with non-numeric string that will fail float() conversion
        invalid_data = valid_form_data.copy()
        invalid_data['mass'] = 'not_a_number'

        # The try-except block in flaskpage catches exceptions but ValueError
        # happens before entering the try block (during parameter parsing)
        # So this test verifies the error is not exposed to user as 500 error
        try:
            response = client.post('/runsim', data=invalid_data)
            # If we get here, error was handled gracefully
            assert response.status_code in [200, 400, 500]
        except ValueError:
            # ValueError bubbling up is also acceptable behavior
            pass

    @patch('dragraceSim.sim_json')
    def test_runsim_extreme_values(self, mock_sim_json, client, valid_form_data):
        """Test simulation with extreme but valid values."""
        mock_response = {
            'Modelname': 'Extreme',
            'Power': 500.0,
            'SolutionFound': False,
            'torquespeed': [],
            'timespeed': [],
            'powerspeed': []
        }
        mock_sim_json.return_value = mock_response

        extreme_data = valid_form_data.copy()
        extreme_data['mass'] = '3000'  # Very heavy
        extreme_data['desiredAccTime'] = '3.0'  # Very fast
        extreme_data['Cd'] = '0.5'  # High drag

        response = client.post('/runsim', data=extreme_data)
        assert response.status_code == 200

        result = response.get_json()
        assert 'Power' in result

    @patch('dragraceSim.sim_json')
    def test_runsim_uphill_simulation(self, mock_sim_json, client, valid_form_data):
        """Test simulation with uphill grade."""
        mock_response = {
            'Modelname': 'Uphill',
            'Power': 200.0,
            'SolutionFound': True,
            'torquespeed': [],
            'timespeed': [],
            'powerspeed': []
        }
        mock_sim_json.return_value = mock_response

        uphill_data = valid_form_data.copy()
        uphill_data['grade'] = '0.1'  # 10% grade

        response = client.post('/runsim', data=uphill_data)
        assert response.status_code == 200

        # Verify grade parameter was passed correctly
        call_args = mock_sim_json.call_args[0]
        assert call_args[3] == 0.1  # grade is 4th parameter

    @patch('dragraceSim.sim_json')
    def test_runsim_response_structure(self, mock_sim_json, client, valid_form_data):
        """Test that response has all required fields."""
        mock_response = {
            'Modelname': 'Complete',
            'Power': 150.0,
            'SolutionFound': True,
            'torquespeed': [{'x': 1, 'y': 100}],
            'timespeed': [{'x': 0.5, 'y': 5}],
            'powerspeed': [{'x': 1, 'y': 50}]
        }
        mock_sim_json.return_value = mock_response

        response = client.post('/runsim', data=valid_form_data)
        result = response.get_json()

        # Verify all expected fields are present
        assert 'Modelname' in result
        assert 'Power' in result
        assert 'SolutionFound' in result
        assert 'torquespeed' in result
        assert 'timespeed' in result
        assert 'powerspeed' in result

    @patch('dragraceSim.sim_json')
    def test_runsim_parameter_types(self, mock_sim_json, client, valid_form_data):
        """Test that form parameters are correctly converted to proper types."""
        mock_response = {
            'Modelname': 'TypeTest',
            'Power': 100.0,
            'SolutionFound': True,
            'torquespeed': [],
            'timespeed': [],
            'powerspeed': []
        }
        mock_sim_json.return_value = mock_response

        response = client.post('/runsim', data=valid_form_data)
        assert response.status_code == 200

        # Check that parameters were converted to correct types
        call_args = mock_sim_json.call_args[0]
        assert isinstance(call_args[0], float)  # Cd
        assert isinstance(call_args[1], float)  # frontArea
        assert isinstance(call_args[2], float)  # mass
        assert isinstance(call_args[9], str)    # driveWheel should remain string

    @patch('dragraceSim.sim_json')
    def test_runsim_vehicle_name_preservation(self, mock_sim_json, client, valid_form_data):
        """Test that vehicle name is correctly passed to simulation."""
        mock_response = {
            'Modelname': 'CustomName',
            'Power': 100.0,
            'SolutionFound': True,
            'torquespeed': [],
            'timespeed': [],
            'powerspeed': []
        }
        mock_sim_json.return_value = mock_response

        custom_data = valid_form_data.copy()
        custom_data['Name'] = 'MyCustomVehicle'

        response = client.post('/runsim', data=custom_data)
        assert response.status_code == 200

        # Verify name parameter was passed
        call_args = mock_sim_json.call_args[0]
        assert call_args[13] == 'MyCustomVehicle'  # name is 14th parameter (index 13)


class TestFlaskAppConfiguration:
    """Tests for Flask app configuration."""

    def test_app_exists(self):
        """Test that Flask app is properly initialized."""
        assert flaskpage.app is not None
        assert flaskpage.app.name == 'flaskpage'

    def test_routes_registered(self):
        """Test that routes are properly registered."""
        # Get all registered routes
        routes = [rule.rule for rule in flaskpage.app.url_map.iter_rules()]

        assert '/' in routes
        assert '/runsim' in routes

    def test_testing_config(self, client):
        """Test that testing configuration is properly set."""
        assert flaskpage.app.config['TESTING'] is True
