from fastapi import APIRouter

from app.apis.endpoints import feedback_routes

main_router = APIRouter()
main_router.include_router(feedback_routes, prefix="/feedbacks", tags=["feedback"])
