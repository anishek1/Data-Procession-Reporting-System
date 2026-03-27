import os
from pathlib import Path
from typing import Set, Union
from core.exceptions import InvalidFileTypeError


def validate_file_type(filename: str, allowed_extensions: Set[str]) -> bool:
    """
    Validate that a file has one of the allowed extensions.

    Args:
        filename: Name of the file
        allowed_extensions: A set of allowed extensions (e.g., {".csv", ".json"}).
                            Extensions should include the leading dot.

    Returns:
        True if valid.

    Raises:
        InvalidFileTypeError: If the extension is not in the allowed list.
    """
    if not filename:
        raise ValueError("Filename cannot be empty")
        
    suffix = Path(filename).suffix.lower()
    
    # Check if the allowed extensions have the leading dot
    normalized_allowed = {ext.lower() if ext.startswith('.') else f".{ext.lower()}" for ext in allowed_extensions}
    
    if suffix not in normalized_allowed:
        raise InvalidFileTypeError(f"Unsupported file type '{suffix}'. Allowed: {', '.join(normalized_allowed)}")
        
    return True


def secure_resolve_path(base_dir: Union[str, Path], filename: str) -> Path:
    """
    Securely joins a base directory with a filename, preventing directory traversal.

    Args:
        base_dir: The directory where the file should be stored.
        filename: The name of the file.

    Returns:
        A resolved, absolute Path object.

    Raises:
        ValueError: If path traversal is detected or filename is invalid.
    """
    if not filename:
        raise ValueError("Filename cannot be empty")

    base_path = Path(base_dir).resolve()
    
    # To catch null bytes early (Python versions < 3.8 can be vulnerable, though Pathlib handles it better now)
    if '\x00' in str(filename):
        raise ValueError("Null bytes are not allowed in paths")

    # Check for direct path traversal characters
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError("Invalid filename: Directory traversal characters are not allowed")

    # Create the final path
    final_path = (base_path / filename).resolve()

    # Ensure the resolved path strictly resides within the base directory
    try:
        final_path.relative_to(base_path)
    except ValueError:
        raise ValueError("Path traversal detected: Resolved path is outside the base directory")

    return final_path
