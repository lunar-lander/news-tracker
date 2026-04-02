"""
Configuration loader for India News Tracker
Loads configuration from YAML files and environment variables
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database (atomic parts — no assembled URL with secrets in defaults)
    postgres_user: str = Field(default="newstrack")
    postgres_password: str = Field(default="")
    postgres_db: str = Field(default="newstrack")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5433)

    @property
    def database_url(self) -> str:
        """Assemble DATABASE_URL at runtime from parts."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

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

    # CORS
    cors_origins: str = Field(default="*")  # Comma-separated origins, or * for dev

    class Config:
        # Local dev: ../../../.env relative to backend/app/config.py
        # Docker:    /app/.env via volume mount
        _local = Path(__file__).resolve().parent.parent.parent / ".env"
        env_file = str(_local) if _local.is_file() else "/app/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def validate_production(self):
        """Raise if running production with insecure defaults"""
        if self.environment == "production":
            if self.jwt_secret in ("dev_jwt_secret", "change_me_in_production"):
                raise ValueError(
                    "JWT_SECRET must be set to a secure value in production"
                )
            if self.encryption_key in ("dev_encryption_key", "change_me_in_production"):
                raise ValueError(
                    "ENCRYPTION_KEY must be set to a secure value in production"
                )
            if self.cors_origins == "*":
                raise ValueError("CORS_ORIGINS must not be * in production")


# Global settings instance
settings = Settings()


def get_config_path() -> Path:
    """Get the path to the config directory.

    Resolution order:
      1. CONFIG_DIR env var (explicit override)
      2. <backend_root>/config  — works in Docker (/app/config via volume mount)
      3. <project_root>/config  — works in local dev (backend/../config)
    """
    env_override = os.environ.get("CONFIG_DIR")
    if env_override:
        p = Path(env_override)
        if p.exists():
            return p

    # backend root: parent of 'app/' package → /app in Docker, or <project>/backend locally
    backend_root = Path(__file__).resolve().parent.parent
    candidates = [
        backend_root / "config",  # Docker: /app/config
        backend_root.parent / "config",  # Local dev: <project>/config
    ]
    for config_dir in candidates:
        if config_dir.exists():
            return config_dir

    searched = ", ".join(str(c) for c in candidates)
    raise FileNotFoundError(f"Config directory not found (searched: {searched})")


def load_yaml_config(filename: str) -> Dict[str, Any]:
    """Load a YAML configuration file"""
    config_path = get_config_path() / filename

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_rss_sources() -> List[Dict[str, Any]]:
    """Load RSS sources from config"""
    config = load_yaml_config("rss-sources.yaml")

    # Flatten the structure - combine all source categories
    sources: List[Dict[str, Any]] = []
    for _, category_sources in config.items():
        if isinstance(category_sources, list):
            sources.extend(category_sources)  # type: ignore[arg-type]

    return sources


def load_tags_config() -> Dict[str, Any]:
    """Load tags configuration"""
    return load_yaml_config("tags.yaml")


def load_llm_config() -> Dict[str, Any]:
    """Load LLM configuration with runtime provider auto-detection.

    Reads provider_preference from the YAML config, checks which API keys
    are actually set in the environment, and resolves 'primary' and 'fallback'
    provider configs at runtime.
    """
    config = load_yaml_config("llm-config.yaml")

    # Map provider names to their Settings API-key attribute names
    provider_key_map: Dict[str, str] = {
        "google": "google_api_key",
        "gemini": "google_api_key",
        "anthropic": "anthropic_api_key",
        "openai": "openai_api_key",
        "cohere": "cohere_api_key",
    }

    # Determine preference order
    preference: List[str] = config.get(
        "provider_preference", ["google", "anthropic", "openai"]
    )

    # Find providers that have a valid API key
    available: List[str] = []
    for provider in preference:
        attr = provider_key_map.get(provider)
        if attr and getattr(settings, attr, ""):
            available.append(provider)

    if not available:
        logger.warning(
            "No LLM API keys found in environment. "
            "Set GOOGLE_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY."
        )

    # Resolve primary and fallback from available providers
    primary_name = available[0] if len(available) > 0 else preference[0]
    fallback_name = (
        available[1]
        if len(available) > 1
        else (preference[1] if len(preference) > 1 else None)
    )

    # Normalise: 'gemini' -> 'google' for config lookup
    def _normalise(name: str) -> str:
        return "google" if name in ("gemini", "google") else name

    def _build_provider_config(name: str) -> Dict[str, Any]:
        """Build a provider config dict from per-provider YAML sections."""
        norm = _normalise(name)
        section = config.get(norm, {})
        # Pick a single model: prefer 'model', else cheapest from 'models'
        model = section.get("model")
        if not model:
            models = section.get("models", {})
            model = models.get("cheap") or next(iter(models.values()), "unknown")
        return {
            "provider": norm,
            "model": model,
            "max_tokens": section.get("max_tokens", 2048),
            "temperature": section.get("temperature", 0.2),
            "rate_limits": section.get("rate_limits", {}),
            "retry_policy": section.get("retry_policy", {}),
            "api_key": getattr(settings, provider_key_map.get(name, ""), ""),
        }

    config["primary"] = _build_provider_config(primary_name)
    if fallback_name:
        config["fallback"] = _build_provider_config(fallback_name)
    else:
        config["fallback"] = None

    logger.info(
        "LLM providers resolved: primary=%s (%s), fallback=%s",
        primary_name,
        config["primary"]["model"],
        fallback_name or "none",
    )

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

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()
