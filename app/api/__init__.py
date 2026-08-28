from fastapi import APIRouter

from app.api import ai, artifacts, auth, documents, knowledge_graph, projects, users
from app.api.resources import routers as resource_routers

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(ai.router)
api_router.include_router(knowledge_graph.router)
api_router.include_router(documents.router)
api_router.include_router(artifacts.router)
for resource_router in resource_routers:
    api_router.include_router(resource_router)
