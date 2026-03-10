"""Tests for config module."""

import pytest
import json
from utils.config import Config


@pytest.fixture
def sample_config_file(tmp_path):
    """Create a sample config file."""
    config_file = tmp_path / "config.json"
    config_data = {
        "log_level": "INFO",
        "log_file": "logs/app.log",
        "input_dir": "input",
        "output_dir": "output"
    }
    config_file.write_text(json.dumps(config_data))
    return str(config_file)


def test_config_load(sample_config_file):
    """Test loading config from file."""
    config = Config(sample_config_file)
    assert config.get("log_level") == "INFO"
    assert config.get("input_dir") == "input"


def test_config_dict_access(sample_config_file):
    """Test dict-like access to config."""
    config = Config(sample_config_file)
    assert config["log_level"] == "INFO"
    assert config["output_dir"] == "output"


def test_config_get_with_default(sample_config_file):
    """Test get with default value."""
    config = Config(sample_config_file)
    assert config.get("nonexistent", "default_value") == "default_value"


def test_config_contains(sample_config_file):
    """Test checking if key exists in config."""
    config = Config(sample_config_file)
    assert "log_level" in config
    assert "nonexistent" not in config


def test_config_file_not_found():
    """Test config fails when file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        Config("nonexistent.json")


def test_config_invalid_json(tmp_path):
    """Test config fails with invalid JSON."""
    config_file = tmp_path / "bad.json"
    config_file.write_text("{ invalid json }")

    with pytest.raises(ValueError):
        Config(str(config_file))
