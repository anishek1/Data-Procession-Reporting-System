import pytest
import os
from pathlib import Path
from utils.file_utils import validate_file_type, secure_resolve_path
from core.exceptions import InvalidFileTypeError


def test_validate_file_type_success():
    assert validate_file_type("test.csv", {".csv", ".json"}) is True
    assert validate_file_type("test.json", {"csv", "json"}) is True
    assert validate_file_type("TEST.CSV", {".csv"}) is True
    assert validate_file_type(".hidden.csv", {".csv"}) is True


def test_validate_file_type_failure():
    with pytest.raises(InvalidFileTypeError):
        validate_file_type("test.exe", {".csv", ".json"})
    with pytest.raises(InvalidFileTypeError):
        validate_file_type("test", {".csv"})
        

def test_validate_file_type_empty():
    with pytest.raises(ValueError, match="Filename cannot be empty"):
        validate_file_type("", {".csv"})
    with pytest.raises(ValueError, match="Filename cannot be empty"):
        validate_file_type(None, {".csv"})


def test_secure_resolve_path_success(tmp_path):
    base_dir = tmp_path / "uploads"
    base_dir.mkdir()
    
    resolved = secure_resolve_path(base_dir, "test.csv")
    assert resolved == (base_dir / "test.csv").resolve()


def test_secure_resolve_path_traversal(tmp_path):
    base_dir = tmp_path / "uploads"
    base_dir.mkdir()
    
    with pytest.raises(ValueError, match="Directory traversal characters are not allowed"):
        secure_resolve_path(base_dir, "../test.csv")
        
    with pytest.raises(ValueError, match="Directory traversal characters are not allowed"):
        secure_resolve_path(base_dir, "test/../../test.csv")
        
    with pytest.raises(ValueError, match="Directory traversal characters are not allowed"):
        secure_resolve_path(base_dir, "/etc/passwd")
        
    with pytest.raises(ValueError, match="Directory traversal characters are not allowed"):
        secure_resolve_path(base_dir, "\\Windows\\System32\\cmd.exe")


def test_secure_resolve_path_null_bytes(tmp_path):
    base_dir = tmp_path / "uploads"
    base_dir.mkdir()
    
    with pytest.raises(ValueError, match="Null bytes are not allowed in paths"):
        secure_resolve_path(base_dir, "test.csv\x00")


def test_secure_resolve_path_empty_filename(tmp_path):
    base_dir = tmp_path / "uploads"
    base_dir.mkdir()
    
    with pytest.raises(ValueError, match="Filename cannot be empty"):
        secure_resolve_path(base_dir, "")
