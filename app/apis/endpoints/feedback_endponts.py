import logging

from fastapi import APIRouter

from app.core.exceptions import make_response_object
from app.schemas import FeedbackCreate
from app.services import FeedbackService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("")
async def create_feedback(feedback_data: FeedbackCreate):
    feedback_service = FeedbackService()
    await feedback_service.create_feedback(feedback_data=feedback_data)
    return make_response_object(data="Gửi phản hồi góp ý thành công")