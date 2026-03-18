"""Tests for logger module."""

import logging
from utils.logger import setup_logger
from utils.logger import get_logger


def test_logger_creation():
    """Test logger is created successfully."""
    logger = setup_logger("test_logger", log_level="INFO")
    assert logger is not None
    assert isinstance(logger, logging.Logger)


def test_logger_name():
    """Test logger has correct name."""
    logger = setup_logger("my_app", log_level="INFO")
    assert logger.name == "my_app"


def test_logger_log_level():
    """Test logger has correct log level."""
    logger = setup_logger("test", log_level="DEBUG")
    assert logger.level == logging.DEBUG


def test_logger_file_handler(tmp_path):
    """Test logger creates log file."""
    log_file = tmp_path / "test.log"
    logger = setup_logger(
        "test_file",
        log_level="INFO",
        log_file=str(log_file)
    )

    logger.info("Test message")

    # Check log file was created
    assert log_file.exists()

    # Check log file contains message
    content = log_file.read_text()
    assert "Test message" in content


def test_logger_multiple_calls(tmp_path):
    """Test creating logger multiple times."""
    log_file = tmp_path / "multi.log"
    logger1 = setup_logger("app1", log_file=str(log_file))
    logger2 = setup_logger("app2", log_file=str(log_file))

    logger1.info("From logger 1")
    logger2.info("From logger 2")

    content = log_file.read_text()
    assert "From logger 1" in content
    assert "From logger 2" in content

def test_get_logger_uses_config():
    """Test get_logger returns a configured logger."""
    logger = get_logger("dprs")
    assert logger is not None
    assert isinstance(logger, logging.Logger)