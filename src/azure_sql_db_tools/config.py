"""
Configuration management for Azure SQL DB Tools
"""

import os
import sys
import tomllib
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration management class"""

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config_path = config_path or self._find_config_file()
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _find_config_file(self) -> str:
        """Find the config.toml file in the current directory or parent directories"""
        current_dir = Path.cwd()

        # Check current directory and parent directories
        for path in [current_dir] + list(current_dir.parents):
            config_file = path / "config.toml"
            if config_file.exists():
                return str(config_file)

        # Default to current directory
        return str(current_dir / "config.toml")

    def _load_config(self) -> None:
        """Load configuration from TOML file"""
        try:
            with open(self.config_path, "rb") as f:
                self.config = tomllib.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {self.config_path}")
            print("Using default configuration values.")
            self.config = {}
        except Exception as e:
            print(f"Error loading config file: {e}")
            sys.exit(1)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with environment variable override"""
        # Check environment variable first (format: AZURE_SQL_DB_TOOLS_SECTION_KEY)
        env_key = f"AZURE_SQL_DB_TOOLS_{section.upper()}_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Fall back to config file
        return self.config.get(section, {}).get(key, default)

    @property
    def workspace_id(self) -> str:
        """Get Azure Log Analytics workspace ID"""
        workspace_id = self.get("azure", "workspace_id")
        if not workspace_id:
            print("ERROR: No workspace_id found in config.toml [azure] section")
            print("Please add your Log Analytics workspace ID to config.toml")
            sys.exit(1)
        return str(workspace_id)

    @property
    def default_time_range(self) -> int:
        """Get default time range for queries"""
        return int(self.get("defaults", "time_range_minutes", 10))

    @property
    def slow_query_threshold(self) -> int:
        """Get default slow query threshold"""
        return int(self.get("defaults", "slow_query_threshold_ms", 5000))

    @property
    def log_level(self) -> str:
        """Get logging level"""
        return str(self.get("logging", "level", "INFO"))

    @property
    def verbose(self) -> bool:
        """Get verbose logging setting"""
        return bool(self.get("logging", "verbose", False))


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
