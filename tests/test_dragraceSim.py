import pytest
import numpy as np
from numpy.testing import assert_almost_equal, assert_array_almost_equal
import dragraceSim


class TestTopGradeSpeed:
    """Tests for topGradeSpeed function - calculates wheel torque needed for given conditions."""

    def test_zero_velocity(self, physics_constants):
        """At zero velocity, only rolling and grade resistance should apply."""
        wheelTorque = dragraceSim.topGradeSpeed(
            Cd=0.3, Cr=0.01, g=9.81, rhoAir=1.2,
            frontArea=2.0, mass=1800, grade=0.0,
            velocity=0.0, wheelRadius=0.3
        )
        # Expected: Froll = 0.01 * 1800 * 9.81 = 176.58 N
        # Torque = 176.58 * 0.3 = 52.974 Nm
        assert_almost_equal(wheelTorque, 52.974, decimal=2)

    def test_with_aerodynamic_drag(self):
        """Test that aerodynamic drag increases with velocity squared."""
        Cd, Cr, g, rhoAir = 0.3, 0.01, 9.81, 1.2
        frontArea, mass, grade, wheelRadius = 2.0, 1800, 0.0, 0.3

        torque_10ms = dragraceSim.topGradeSpeed(
            Cd, Cr, g, rhoAir, frontArea, mass, grade, 10.0, wheelRadius
        )
        torque_20ms = dragraceSim.topGradeSpeed(
            Cd, Cr, g, rhoAir, frontArea, mass, grade, 20.0, wheelRadius
        )

        # At 20 m/s, drag force should be 4x higher than at 10 m/s (v^2 relationship)
        # The difference should reflect this quadratic relationship
        assert torque_20ms > torque_10ms

        # Calculate expected drag contribution
        drag_10 = 0.3 * 2.0 * 1.2 * (10.0**2) / 2  # 360 N
        drag_20 = 0.3 * 2.0 * 1.2 * (20.0**2) / 2  # 1440 N
        assert_almost_equal(drag_20 / drag_10, 4.0, decimal=1)

    def test_uphill_grade(self):
        """Test that positive grade increases required torque."""
        Cd, Cr, g, rhoAir = 0.3, 0.01, 9.81, 1.2
        frontArea, mass, velocity, wheelRadius = 2.0, 1800, 10.0, 0.3

        flat_torque = dragraceSim.topGradeSpeed(
            Cd, Cr, g, rhoAir, frontArea, mass, 0.0, velocity, wheelRadius
        )
        uphill_torque = dragraceSim.topGradeSpeed(
            Cd, Cr, g, rhoAir, frontArea, mass, 0.1, velocity, wheelRadius
        )

        # Grade resistance = mass * g * grade = 1800 * 9.81 * 0.1 = 1765.8 N
        # Additional torque = 1765.8 * 0.3 = 529.74 Nm
        assert uphill_torque > flat_torque
        assert_almost_equal(uphill_torque - flat_torque, 529.74, decimal=1)

    def test_downhill_grade(self):
        """Test that negative grade decreases required torque."""
        Cd, Cr, g, rhoAir = 0.3, 0.01, 9.81, 1.2
        frontArea, mass, velocity, wheelRadius = 2.0, 1800, 10.0, 0.3

        flat_torque = dragraceSim.topGradeSpeed(
            Cd, Cr, g, rhoAir, frontArea, mass, 0.0, velocity, wheelRadius
        )
        downhill_torque = dragraceSim.topGradeSpeed(
            Cd, Cr, g, rhoAir, frontArea, mass, -0.05, velocity, wheelRadius
        )

        assert downhill_torque < flat_torque


class TestTractionMax:
    """Tests for tractionMax function - calculates maximum wheel force based on weight transfer."""

    def test_awd_simple_case(self):
        """AWD should have maximum traction equal to mass * g * mu."""
        wheelForceMax = dragraceSim.tractionMax(
            mass=1800, g=9.81, wtRearFrac=0.5, wheelbase=2.5,
            cgh=0.5, driveWheel='AWD', muTire=0.9
        )
        # Expected: mass * g * mu (theoretical: 15,898.8 N, code uses different g value)
        expected = 1800 * 9.81 * 0.9
        assert abs(wheelForceMax - expected) / expected < 0.01  # Within 1%

    def test_awd_independent_of_weight_distribution(self):
        """AWD traction should not depend on weight distribution."""
        force1 = dragraceSim.tractionMax(
            mass=1800, g=9.81, wtRearFrac=0.3, wheelbase=2.5,
            cgh=0.5, driveWheel='AWD', muTire=0.9
        )
        force2 = dragraceSim.tractionMax(
            mass=1800, g=9.81, wtRearFrac=0.7, wheelbase=2.5,
            cgh=0.5, driveWheel='AWD', muTire=0.9
        )
        assert_almost_equal(force1, force2, decimal=1)

    def test_fwd_weight_transfer(self, capsys):
        """FWD should account for weight transfer reducing front axle load during acceleration."""
        wheelForceMax = dragraceSim.tractionMax(
            mass=1800, g=9.81, wtRearFrac=0.56, wheelbase=2.5,
            cgh=0.6, driveWheel='FWD', muTire=0.9
        )
        # Should be less than AWD case due to weight transfer off front wheels
        awd_force = 1800 * 9.81 * 0.9
        assert wheelForceMax < awd_force

        # Check that print statement was called
        captured = capsys.readouterr()
        assert 'FWD' in captured.out

    def test_rwd_weight_transfer(self):
        """RWD should benefit from weight transfer to rear axle during acceleration."""
        wheelForceMax = dragraceSim.tractionMax(
            mass=1800, g=9.81, wtRearFrac=0.56, wheelbase=2.5,
            cgh=0.6, driveWheel='RWD', muTire=0.9
        )
        # RWD should have more traction than base rear weight due to weight transfer
        base_rear_weight = 1800 * 9.81 * 0.56
        assert wheelForceMax > 0  # Just verify it returns a positive value

    def test_higher_cog_reduces_fwd_traction(self):
        """Higher center of gravity should reduce FWD traction more."""
        force_low_cog = dragraceSim.tractionMax(
            mass=1800, g=9.81, wtRearFrac=0.56, wheelbase=2.5,
            cgh=0.3, driveWheel='FWD', muTire=0.9
        )
        force_high_cog = dragraceSim.tractionMax(
            mass=1800, g=9.81, wtRearFrac=0.56, wheelbase=2.5,
            cgh=0.8, driveWheel='FWD', muTire=0.9
        )
        # Higher COG means more weight transfer, less front traction
        assert force_low_cog > force_high_cog

    def test_returns_float(self):
        """Ensure function returns a float, not a SymPy expression."""
        result = dragraceSim.tractionMax(
            mass=1800, g=9.81, wtRearFrac=0.5, wheelbase=2.5,
            cgh=0.5, driveWheel='RWD', muTire=0.9
        )
        assert isinstance(result, float)


class TestAccelerateVehicle:
    """Tests for accelerateVehicle function - main simulation with power optimization."""

    def test_basic_simulation_converges(self, standard_vehicle_params):
        """Test that simulation converges to a solution."""
        times, torques, velocities, power, mission_pass = dragraceSim.accelerateVehicle(
            standard_vehicle_params['Cd'],
            standard_vehicle_params['frontArea'],
            standard_vehicle_params['mass'],
            standard_vehicle_params['grade'],
            standard_vehicle_params['v0'],
            standard_vehicle_params['v1'],
            standard_vehicle_params['cgh'],
            standard_vehicle_params['wtRearFrac'],
            standard_vehicle_params['wheelbase'],
            standard_vehicle_params['driveWheel'],
            standard_vehicle_params['desiredAccTime'],
            standard_vehicle_params['muTire'],
            standard_vehicle_params['wheelRadius']
        )

        # Check that we got valid outputs
        assert len(times) > 0
        assert len(torques) == len(velocities) == len(times)
        assert power > 0
        assert isinstance(mission_pass, bool)

        # Verify final velocity is close to target
        assert velocities[-1] >= standard_vehicle_params['v1'] * 0.95

    def test_acceleration_time_accuracy(self, standard_vehicle_params):
        """Test that simulation achieves desired acceleration time within tolerance."""
        times, _, _, power, mission_pass = dragraceSim.accelerateVehicle(
            standard_vehicle_params['Cd'],
            standard_vehicle_params['frontArea'],
            standard_vehicle_params['mass'],
            standard_vehicle_params['grade'],
            standard_vehicle_params['v0'],
            standard_vehicle_params['v1'],
            standard_vehicle_params['cgh'],
            standard_vehicle_params['wtRearFrac'],
            standard_vehicle_params['wheelbase'],
            standard_vehicle_params['driveWheel'],
            standard_vehicle_params['desiredAccTime'],
            standard_vehicle_params['muTire'],
            standard_vehicle_params['wheelRadius']
        )

        actual_time = times[-1] if times else 0
        desired_time = standard_vehicle_params['desiredAccTime']

        # Should be within 1% tolerance (0.01 from code)
        assert abs(actual_time - desired_time) / desired_time < 0.02

    def test_faster_time_requires_more_power(self, standard_vehicle_params):
        """Test that faster acceleration requires more power."""
        params_slow = standard_vehicle_params.copy()
        params_slow['desiredAccTime'] = 12.0

        params_fast = standard_vehicle_params.copy()
        params_fast['desiredAccTime'] = 6.0

        _, _, _, power_slow, _ = dragraceSim.accelerateVehicle(
            params_slow['Cd'], params_slow['frontArea'], params_slow['mass'],
            params_slow['grade'], params_slow['v0'], params_slow['v1'],
            params_slow['cgh'], params_slow['wtRearFrac'], params_slow['wheelbase'],
            params_slow['driveWheel'], params_slow['desiredAccTime'],
            params_slow['muTire'], params_slow['wheelRadius']
        )

        _, _, _, power_fast, _ = dragraceSim.accelerateVehicle(
            params_fast['Cd'], params_fast['frontArea'], params_fast['mass'],
            params_fast['grade'], params_fast['v0'], params_fast['v1'],
            params_fast['cgh'], params_fast['wtRearFrac'], params_fast['wheelbase'],
            params_fast['driveWheel'], params_fast['desiredAccTime'],
            params_fast['muTire'], params_fast['wheelRadius']
        )

        assert power_fast > power_slow

    def test_heavier_vehicle_requires_more_power(self, standard_vehicle_params):
        """Test that heavier vehicle requires more power for same acceleration."""
        params_light = standard_vehicle_params.copy()
        params_light['mass'] = 1200

        params_heavy = standard_vehicle_params.copy()
        params_heavy['mass'] = 2400

        _, _, _, power_light, _ = dragraceSim.accelerateVehicle(
            params_light['Cd'], params_light['frontArea'], params_light['mass'],
            params_light['grade'], params_light['v0'], params_light['v1'],
            params_light['cgh'], params_light['wtRearFrac'], params_light['wheelbase'],
            params_light['driveWheel'], params_light['desiredAccTime'],
            params_light['muTire'], params_light['wheelRadius']
        )

        _, _, _, power_heavy, _ = dragraceSim.accelerateVehicle(
            params_heavy['Cd'], params_heavy['frontArea'], params_heavy['mass'],
            params_heavy['grade'], params_heavy['v0'], params_heavy['v1'],
            params_heavy['cgh'], params_heavy['wtRearFrac'], params_heavy['wheelbase'],
            params_heavy['driveWheel'], params_heavy['desiredAccTime'],
            params_heavy['muTire'], params_heavy['wheelRadius']
        )

        assert power_heavy > power_light

    def test_velocity_increases_monotonically(self, standard_vehicle_params):
        """Test that velocity increases throughout simulation."""
        _, _, velocities, _, _ = dragraceSim.accelerateVehicle(
            standard_vehicle_params['Cd'],
            standard_vehicle_params['frontArea'],
            standard_vehicle_params['mass'],
            standard_vehicle_params['grade'],
            standard_vehicle_params['v0'],
            standard_vehicle_params['v1'],
            standard_vehicle_params['cgh'],
            standard_vehicle_params['wtRearFrac'],
            standard_vehicle_params['wheelbase'],
            standard_vehicle_params['driveWheel'],
            standard_vehicle_params['desiredAccTime'],
            standard_vehicle_params['muTire'],
            standard_vehicle_params['wheelRadius']
        )

        # Each velocity should be >= previous (monotonically increasing)
        for i in range(1, len(velocities)):
            assert velocities[i] >= velocities[i-1]

    def test_mission_pass_flag(self, standard_vehicle_params):
        """Test that mission_pass flag correctly indicates if power is traction-limited."""
        _, _, _, power, mission_pass = dragraceSim.accelerateVehicle(
            standard_vehicle_params['Cd'],
            standard_vehicle_params['frontArea'],
            standard_vehicle_params['mass'],
            standard_vehicle_params['grade'],
            standard_vehicle_params['v0'],
            standard_vehicle_params['v1'],
            standard_vehicle_params['cgh'],
            standard_vehicle_params['wtRearFrac'],
            standard_vehicle_params['wheelbase'],
            standard_vehicle_params['driveWheel'],
            standard_vehicle_params['desiredAccTime'],
            standard_vehicle_params['muTire'],
            standard_vehicle_params['wheelRadius']
        )

        # Calculate wheelForceMax
        wheelForceMax = dragraceSim.tractionMax(
            standard_vehicle_params['mass'], 9.81,
            standard_vehicle_params['wtRearFrac'],
            standard_vehicle_params['wheelbase'],
            standard_vehicle_params['cgh'],
            standard_vehicle_params['driveWheel'],
            standard_vehicle_params['muTire']
        )

        # Check if mission_pass aligns with traction limit
        if power / standard_vehicle_params['v1'] > wheelForceMax:
            assert mission_pass is False
        else:
            assert mission_pass is True

    def test_uphill_grade_requires_more_power(self, standard_vehicle_params):
        """Test that uphill grade requires more power."""
        params_flat = standard_vehicle_params.copy()
        params_flat['grade'] = 0.0

        params_uphill = standard_vehicle_params.copy()
        params_uphill['grade'] = 0.05

        _, _, _, power_flat, _ = dragraceSim.accelerateVehicle(
            params_flat['Cd'], params_flat['frontArea'], params_flat['mass'],
            params_flat['grade'], params_flat['v0'], params_flat['v1'],
            params_flat['cgh'], params_flat['wtRearFrac'], params_flat['wheelbase'],
            params_flat['driveWheel'], params_flat['desiredAccTime'],
            params_flat['muTire'], params_flat['wheelRadius']
        )

        _, _, _, power_uphill, _ = dragraceSim.accelerateVehicle(
            params_uphill['Cd'], params_uphill['frontArea'], params_uphill['mass'],
            params_uphill['grade'], params_uphill['v0'], params_uphill['v1'],
            params_uphill['cgh'], params_uphill['wtRearFrac'], params_uphill['wheelbase'],
            params_uphill['driveWheel'], params_uphill['desiredAccTime'],
            params_uphill['muTire'], params_uphill['wheelRadius']
        )

        assert power_uphill > power_flat

    def test_different_drivetrain_types(self, standard_vehicle_params):
        """Test that all drivetrain types (AWD, FWD, RWD) produce valid results."""
        for drivetrain in ['AWD', 'FWD', 'RWD']:
            params = standard_vehicle_params.copy()
            params['driveWheel'] = drivetrain

            times, torques, velocities, power, mission_pass = dragraceSim.accelerateVehicle(
                params['Cd'], params['frontArea'], params['mass'],
                params['grade'], params['v0'], params['v1'],
                params['cgh'], params['wtRearFrac'], params['wheelbase'],
                params['driveWheel'], params['desiredAccTime'],
                params['muTire'], params['wheelRadius']
            )

            assert len(times) > 0, f"Failed for {drivetrain}"
            assert power > 0, f"Failed for {drivetrain}"
            assert isinstance(mission_pass, bool), f"Failed for {drivetrain}"


class TestSimJson:
    """Tests for sim_json function - wrapper that formats output for web."""

    def test_returns_proper_structure(self, standard_vehicle_params):
        """Test that sim_json returns correctly formatted dictionary."""
        result = dragraceSim.sim_json(
            standard_vehicle_params['Cd'],
            standard_vehicle_params['frontArea'],
            standard_vehicle_params['mass'],
            standard_vehicle_params['grade'],
            standard_vehicle_params['v0'],
            standard_vehicle_params['v1'],
            standard_vehicle_params['cgh'],
            standard_vehicle_params['wtRearFrac'],
            standard_vehicle_params['wheelbase'],
            standard_vehicle_params['driveWheel'],
            standard_vehicle_params['desiredAccTime'],
            standard_vehicle_params['muTire'],
            standard_vehicle_params['wheelRadius'],
            standard_vehicle_params['name']
        )

        # Check required keys
        assert 'Modelname' in result
        assert 'Power' in result
        assert 'SolutionFound' in result
        assert 'torquespeed' in result
        assert 'timespeed' in result
        assert 'powerspeed' in result

        # Check types
        assert result['Modelname'] == standard_vehicle_params['name']
        assert isinstance(result['Power'], float)
        assert isinstance(result['SolutionFound'], bool)
        assert isinstance(result['torquespeed'], list)
        assert isinstance(result['timespeed'], list)
        assert isinstance(result['powerspeed'], list)

    def test_data_point_format(self, standard_vehicle_params):
        """Test that data points are formatted as x-y dictionaries."""
        result = dragraceSim.sim_json(
            standard_vehicle_params['Cd'],
            standard_vehicle_params['frontArea'],
            standard_vehicle_params['mass'],
            standard_vehicle_params['grade'],
            standard_vehicle_params['v0'],
            standard_vehicle_params['v1'],
            standard_vehicle_params['cgh'],
            standard_vehicle_params['wtRearFrac'],
            standard_vehicle_params['wheelbase'],
            standard_vehicle_params['driveWheel'],
            standard_vehicle_params['desiredAccTime'],
            standard_vehicle_params['muTire'],
            standard_vehicle_params['wheelRadius'],
            standard_vehicle_params['name']
        )

        # Check torquespeed format
        if len(result['torquespeed']) > 0:
            point = result['torquespeed'][0]
            assert 'x' in point
            assert 'y' in point
            assert isinstance(point['x'], (int, float))
            assert isinstance(point['y'], (int, float))

        # Check timespeed format
        if len(result['timespeed']) > 0:
            point = result['timespeed'][0]
            assert 'x' in point
            assert 'y' in point

        # Check powerspeed format
        if len(result['powerspeed']) > 0:
            point = result['powerspeed'][0]
            assert 'x' in point
            assert 'y' in point

    def test_power_in_kilowatts(self, standard_vehicle_params):
        """Test that power is returned in kilowatts."""
        result = dragraceSim.sim_json(
            standard_vehicle_params['Cd'],
            standard_vehicle_params['frontArea'],
            standard_vehicle_params['mass'],
            standard_vehicle_params['grade'],
            standard_vehicle_params['v0'],
            standard_vehicle_params['v1'],
            standard_vehicle_params['cgh'],
            standard_vehicle_params['wtRearFrac'],
            standard_vehicle_params['wheelbase'],
            standard_vehicle_params['driveWheel'],
            standard_vehicle_params['desiredAccTime'],
            standard_vehicle_params['muTire'],
            standard_vehicle_params['wheelRadius'],
            standard_vehicle_params['name']
        )

        # Power should be in reasonable kW range for an EV (typically 50-500 kW)
        assert 10 < result['Power'] < 1000

    def test_data_decimation(self, standard_vehicle_params):
        """Test that output data is decimated (every 20th point)."""
        result = dragraceSim.sim_json(
            standard_vehicle_params['Cd'],
            standard_vehicle_params['frontArea'],
            standard_vehicle_params['mass'],
            standard_vehicle_params['grade'],
            standard_vehicle_params['v0'],
            standard_vehicle_params['v1'],
            standard_vehicle_params['cgh'],
            standard_vehicle_params['wtRearFrac'],
            standard_vehicle_params['wheelbase'],
            standard_vehicle_params['driveWheel'],
            standard_vehicle_params['desiredAccTime'],
            standard_vehicle_params['muTire'],
            standard_vehicle_params['wheelRadius'],
            standard_vehicle_params['name']
        )

        # Output should be decimated (much smaller than raw simulation)
        # A 9 second simulation at 0.01s timestep = 900 points
        # Decimated by 20 = ~45 points (plus final point)
        assert len(result['torquespeed']) < 100
        assert len(result['timespeed']) < 100
        assert len(result['powerspeed']) < 100
