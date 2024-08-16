from fastapi import APIRouter
from src.views.auth import auth_routes
from src.views.user import user_routes
from src.views.chat import chat_route
from src.views.faq import faqs_router
from src.views.resource import resources_router

routes = APIRouter()

routes.include_router(auth_routes)
routes.include_router(user_routes)
routes.include_router(chat_route)
routes.include_router(faqs_router)
routes.include_router(resources_router)
