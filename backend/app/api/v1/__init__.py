"""
API v1 Router Aggregation
"""

from fastapi import APIRouter
from app.api.v1 import events, analytics, config, search

router = APIRouter()

# Include all v1 routers
router.include_router(events.router)
router.include_router(analytics.router)
router.include_router(config.router)
router.include_router(search.router)
