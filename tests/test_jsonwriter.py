import pytest
import json
import numpy as np
from pathlib import Path
import jsonwriter


class TestOutputJson:
    """Tests for output_json function - converts CSV to JSON format."""

    def test_basic_csv_conversion(self, tmp_path):
        """Test converting a simple CSV file to JSON."""
        # Create a test CSV file
        csv_file = tmp_path / "test_data.csv"
        csv_data = np.array([[1.0, 100.0], [2.0, 200.0], [3.0, 300.0]])
        np.savetxt(csv_file, csv_data, delimiter=',')

        # Create output directory
        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        # Temporarily change the output path in the function
        # Since the function uses hardcoded path, we'll test the logic instead
        # by calling it and checking the output file
        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            jsonwriter.output_json(str(csv_file), "TestModel", 123.4)

            # Check that JSON file was created
            json_file = output_dir / "test_data.json"
            assert json_file.exists()

            # Read and verify JSON content
            with open(json_file, 'r') as f:
                result = json.load(f)

            assert 'xydata' in result
            assert 'Power' in result
            assert 'Modelname' in result
            assert result['Power'] == 123.4
            assert result['Modelname'] == 'TestModel'
            assert len(result['xydata']) == 3

            # Check data format
            assert result['xydata'][0]['x'] == 1.0
            assert result['xydata'][0]['y'] == 100.0
            assert result['xydata'][1]['x'] == 2.0
            assert result['xydata'][1]['y'] == 200.0

        finally:
            os.chdir(original_path)

    def test_empty_csv(self, tmp_path):
        """Test handling of empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.touch()

        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # This should handle empty file gracefully or raise appropriate error
            try:
                jsonwriter.output_json(str(csv_file), "EmptyModel", 0)
                json_file = output_dir / "empty.json"
                if json_file.exists():
                    with open(json_file, 'r') as f:
                        result = json.load(f)
                    assert 'xydata' in result
            except (ValueError, IndexError):
                # Empty CSV may raise error, which is acceptable
                pass

        finally:
            os.chdir(original_path)

    def test_large_csv(self, tmp_path):
        """Test handling of large CSV file."""
        csv_file = tmp_path / "large_data.csv"
        large_data = np.column_stack([
            np.linspace(0, 100, 1000),
            np.random.rand(1000) * 500
        ])
        np.savetxt(csv_file, large_data, delimiter=',')

        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            jsonwriter.output_json(str(csv_file), "LargeModel", 250.5)

            json_file = output_dir / "large_data.json"
            assert json_file.exists()

            with open(json_file, 'r') as f:
                result = json.load(f)

            assert len(result['xydata']) == 1000
            assert result['Power'] == 250.5

        finally:
            os.chdir(original_path)


class TestGlobCsvs:
    """Tests for glob_csvs function - batch processes multiple CSV files."""

    def test_single_csv_file(self, tmp_path):
        """Test processing a single CSV file."""
        # Create test CSV
        csv_file = tmp_path / "test1.csv"
        csv_data = np.array([[1.0, 100.0], [2.0, 200.0]])
        np.savetxt(csv_file, csv_data, delimiter=',')

        # Create output directory
        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            message = jsonwriter.glob_csvs(str(tmp_path))

            assert "converted 1 .csv files to .json" in message
            json_file = output_dir / "test1.json"
            assert json_file.exists()

        finally:
            os.chdir(original_path)

    def test_multiple_csv_files(self, tmp_path):
        """Test processing multiple CSV files."""
        # Create multiple test CSV files
        for i in range(5):
            csv_file = tmp_path / f"test{i}.csv"
            csv_data = np.array([[1.0, 100.0 + i], [2.0, 200.0 + i]])
            np.savetxt(csv_file, csv_data, delimiter=',')

        # Create output directory
        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            message = jsonwriter.glob_csvs(str(tmp_path))

            assert "converted 5 .csv files to .json" in message

            # Check that all JSON files were created
            for i in range(5):
                json_file = output_dir / f"test{i}.json"
                assert json_file.exists()

        finally:
            os.chdir(original_path)

    def test_no_csv_files(self, tmp_path):
        """Test folder with no CSV files."""
        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            message = jsonwriter.glob_csvs(str(tmp_path))

            assert "converted 0 .csv files to .json" in message

        finally:
            os.chdir(original_path)

    def test_mixed_file_types(self, tmp_path):
        """Test folder with CSV and other file types."""
        # Create CSV files
        for i in range(3):
            csv_file = tmp_path / f"data{i}.csv"
            csv_data = np.array([[1.0, 100.0], [2.0, 200.0]])
            np.savetxt(csv_file, csv_data, delimiter=',')

        # Create non-CSV files
        (tmp_path / "readme.txt").write_text("Some text")
        (tmp_path / "data.json").write_text("{}")

        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            message = jsonwriter.glob_csvs(str(tmp_path))

            # Should only process CSV files
            assert "converted 3 .csv files to .json" in message

        finally:
            os.chdir(original_path)

    def test_nested_folder_structure(self, tmp_path):
        """Test that glob_csvs only processes files in specified folder, not subfolders."""
        # Create CSV in main folder with proper 2D data
        csv_file = tmp_path / "main.csv"
        csv_data = np.array([[1.0, 100.0], [2.0, 200.0]])
        np.savetxt(csv_file, csv_data, delimiter=',')

        # Create CSV in subfolder
        subfolder = tmp_path / "subfolder"
        subfolder.mkdir()
        sub_csv = subfolder / "sub.csv"
        np.savetxt(sub_csv, csv_data, delimiter=',')

        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            message = jsonwriter.glob_csvs(str(tmp_path))

            # Should only find 1 CSV (in main folder, not subfolder)
            assert "converted 1 .csv files to .json" in message

        finally:
            os.chdir(original_path)


class TestDataIntegrity:
    """Tests for data integrity and format correctness."""

    def test_numeric_precision(self, tmp_path):
        """Test that numeric values are preserved with proper precision."""
        csv_file = tmp_path / "precision.csv"
        # Use high-precision values
        csv_data = np.array([
            [1.23456789, 100.11111111],
            [2.98765432, 200.22222222]
        ])
        np.savetxt(csv_file, csv_data, delimiter=',', fmt='%.8f')

        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            jsonwriter.output_json(str(csv_file), "PrecisionModel", 123.456789)

            json_file = output_dir / "precision.json"
            with open(json_file, 'r') as f:
                result = json.load(f)

            # Check that values are close to original (within floating-point precision)
            assert abs(result['xydata'][0]['x'] - 1.23456789) < 1e-6
            assert abs(result['xydata'][0]['y'] - 100.11111111) < 1e-6

        finally:
            os.chdir(original_path)

    def test_json_structure_validity(self, tmp_path):
        """Test that generated JSON is valid and parseable."""
        csv_file = tmp_path / "structure.csv"
        csv_data = np.array([[1.0, 100.0], [2.0, 200.0]])
        np.savetxt(csv_file, csv_data, delimiter=',')

        output_dir = tmp_path / "static" / "json"
        output_dir.mkdir(parents=True)

        original_path = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            jsonwriter.output_json(str(csv_file), "StructureModel", 150.0)

            json_file = output_dir / "structure.json"

            # Verify JSON is valid by parsing it
            with open(json_file, 'r') as f:
                result = json.load(f)

            # Verify structure
            assert isinstance(result, dict)
            assert isinstance(result['xydata'], list)
            assert all(isinstance(point, dict) for point in result['xydata'])
            assert all('x' in point and 'y' in point for point in result['xydata'])

        finally:
            os.chdir(original_path)
