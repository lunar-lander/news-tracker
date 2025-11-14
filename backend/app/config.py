"""
Configuration loader for India News Tracker
Loads configuration from YAML files and environment variables
"""

import os
from pathlib import Path
from typing import Any, Dict, List
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    database_url: str = Field(default="postgresql://newstrack:newstrack_dev_password@localhost:5432/newstrack")

    # LLM API Keys
    google_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    cohere_api_key: str = Field(default="")

    # Application
    environment: str = Field(default="development")
    port: int = Field(default=8000)
    log_level: str = Field(default="info")

    # Security
    jwt_secret: str = Field(default="dev_jwt_secret")
    encryption_key: str = Field(default="dev_encryption_key")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_config_path() -> Path:
    """Get the path to the config directory"""
    # Try to find config directory
    current_dir = Path(__file__).parent
    config_dir = current_dir.parent.parent / "config"

    if not config_dir.exists():
        raise FileNotFoundError(f"Config directory not found at {config_dir}")

    return config_dir


def load_yaml_config(filename: str) -> Dict[str, Any]:
    """Load a YAML configuration file"""
    config_path = get_config_path() / filename

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_rss_sources() -> List[Dict[str, Any]]:
    """Load RSS sources from config"""
    config = load_yaml_config("rss-sources.yaml")

    # Flatten the structure - combine all source categories
    sources = []
    for category_key, category_sources in config.items():
        if isinstance(category_sources, list):
            sources.extend(category_sources)

    return sources


def load_tags_config() -> Dict[str, Any]:
    """Load tags configuration"""
    return load_yaml_config("tags.yaml")


def load_llm_config() -> Dict[str, Any]:
    """Load LLM configuration"""
    config = load_yaml_config("llm-config.yaml")

    # Replace environment variable placeholders
    if 'primary' in config and 'api_key' in config['primary']:
        api_key = config['primary']['api_key']
        if api_key.startswith('${') and api_key.endswith('}'):
            env_var = api_key[2:-1]
            config['primary']['api_key'] = getattr(settings, env_var.lower(), '')

    if 'fallback' in config and 'api_key' in config['fallback']:
        api_key = config['fallback']['api_key']
        if api_key.startswith('${') and api_key.endswith('}'):
            env_var = api_key[2:-1]
            config['fallback']['api_key'] = getattr(settings, env_var.lower(), '')

    return config


def load_filters_config() -> Dict[str, Any]:
    """Load filters configuration"""
    return load_yaml_config("filters.yaml")


def load_dashboard_config() -> Dict[str, Any]:
    """Load dashboard configuration"""
    return load_yaml_config("dashboard-config.yaml")


def load_prompt_template(template_name: str) -> str:
    """Load a prompt template"""
    prompt_path = get_config_path() / "prompts" / template_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()
