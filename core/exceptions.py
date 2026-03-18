"""
Custom Exception Classes

All DPRS-specific exceptions are defined here.
Exceptions follow a hierarchy with DPRSException as base.
"""


class DPRSException(Exception):
    """Base exception for all DPRS errors."""
    pass


class FileNotFoundError(DPRSException):
    """Raised when input file does not exist."""
    pass


class InvalidFileTypeError(DPRSException):
    """Raised when file format is not CSV or JSON."""
    pass


class SchemaValidationError(DPRSException):
    """Raised when data schema validation fails."""
    pass


class DataIntegrityError(DPRSException):
    """Raised when a data integrity check fails."""
    pass


class DataProcessingError(DPRSException):
    """Raised when a data processing operation fails."""
    pass


class ConfigurationError(DPRSException):
    """Raised when configuration is missing or invalid."""
    pass


class InvalidArgumentError(DPRSException):
    """Raised when invalid CLI arguments are provided."""
    pass

class ReportGenerationError(DPRSException):
<<<<<<< HEAD
    """Raised when report generation fails."""
=======
    """Raised when report cannot be created or saved."""
    pass

class MissingFieldError(DPRSException):
    """Raised when a required field is absent in the data."""
>>>>>>> d726596 (feat: added  config.json, exceptions.py, update logger and config, add gitignore rules)
    pass