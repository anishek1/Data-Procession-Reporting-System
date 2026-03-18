import pytest
from unittest.mock import patch
from typing import Dict, Any

from cli.main import main
from core.exceptions import DPRSException

@pytest.fixture
def mock_sys_argv(monkeypatch):
    """Allows simulating command-line arguments."""
    fake_argv = ['main.py']
    import sys
    monkeypatch.setattr(sys, 'argv', fake_argv)
    yield fake_argv

@patch('cli.main.load_file')
@patch('cli.main.compute_statistics')
@patch('cli.main.ReportGenerator')
class TestCLI:

    def test_load_command(self, mock_generator, mock_compute, mock_load, mock_sys_argv):
        mock_sys_argv.extend(['load', '--file', 'data.csv'])
        
        main()
        
        mock_load.assert_called_once_with('data.csv')
        mock_compute.assert_not_called()

    def test_summary_command(self, mock_generator, mock_compute, mock_load, mock_sys_argv):
        mock_sys_argv.extend(['summary'])
        mock_compute.return_value = {"key": "val"}
        mock_gen_instance = mock_generator.return_value
        
        main()
        
        mock_compute.assert_called_once()
        mock_gen_instance.display_summary_to_console.assert_called_once_with({"key": "val"})

    def test_report_command(self, mock_generator, mock_compute, mock_load, mock_sys_argv):
        mock_sys_argv.extend(['report', '--type', 'text'])
        mock_compute.return_value = {"key": "val"}
        mock_gen_instance = mock_generator.return_value
        mock_gen_instance.generate_text_report.return_value = "output/report.txt"
        
        main()
        
        mock_compute.assert_called_once()
        mock_gen_instance.generate_text_report.assert_called_once_with({"key": "val"})

    def test_export_command(self, mock_generator, mock_compute, mock_load, mock_sys_argv):
        mock_sys_argv.extend(['export', '--format', 'json'])
        mock_compute.return_value = {"key": "val"}
        mock_gen_instance = mock_generator.return_value
        mock_gen_instance.generate_json_report.return_value = "output/export.json"
        
        main()
        
        mock_compute.assert_called_once()
        mock_gen_instance.generate_json_report.assert_called_once_with({"key": "val"})

    @patch('cli.main.sys.exit')
    @patch('cli.main.logger.error')
    def test_error_handling(self, mock_log_error, mock_sys_exit, mock_generator, mock_compute, mock_load, mock_sys_argv):
        mock_sys_argv.extend(['load', '--file', 'invalid.csv'])
        mock_load.side_effect = DPRSException("Mock exception")
        
        main()
        
        mock_log_error.assert_called_once()
        mock_sys_exit.assert_called_once_with(1)
