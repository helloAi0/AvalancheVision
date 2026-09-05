"""Small, deployment-neutral API access controls."""

import secrets
from fastapi import Header, HTTPException
from backend.core.config import settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Require the configured API key when API_KEY is enabled in deployment."""
    if not settings.API_KEY:
        return
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(status_code=401, detail="API authentication required.")
