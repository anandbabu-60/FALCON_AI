from fastapi import APIRouter

from app.api import auth, projects, users
from app.api.resources import routers as resource_routers

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
for resource_router in resource_routers:
    api_router.include_router(resource_router)
