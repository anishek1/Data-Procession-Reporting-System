"""
Configuration Management

Loads and manages application configuration from config.json.
All configuration comes from this module, never from os.environ directly.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager — loads settings from a JSON file."""

    def __init__(self, config_file: str = "config.json"):
        """
        Load configuration from a JSON file.

        Args:
            config_file: Path to the JSON config file

        Raises:
            FileNotFoundError: If config file does not exist
            ValueError: If config file contains invalid JSON
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load (or reload) configuration from the JSON file."""
        # Ensure the config file actually exists before trying to read it
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_file}"
            )

        try:
            # Parse the JSON file directly into the internal dictionary
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a config value by key.

        Args:
            key: Configuration key
            default: Value to return if key is not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access: config['key']."""
        return self.config[key]

    def __contains__(self, key: str) -> bool:
        """Allow 'key in config' checks."""
        return key in self.config


# Module-level singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global Config instance (lazy-loaded from config.json).

    Returns:
        Shared Config instance
    """
    global _config
    # Implement lazy-loading: instantiate Config if hasn't been created yet
    if _config is None:
        _config = Config()
    return _config


def load_config(filepath: str = "config.json") -> Config:
    """
    Load (or reload) configuration from a specific file path.

    Args:
        filepath: Path to config JSON file

    Returns:
        New Config instance
    """
    global _config
    _config = Config(filepath)
    return _config
