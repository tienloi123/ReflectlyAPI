import logging

from fastapi import APIRouter, Form, UploadFile, File

from app.core.exceptions import make_response_object
from app.schemas import FeedbackCreate
from app.services import FeedbackService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("")
async def create_feedback(full_name: str | None = Form(None),
                            phone_number: str | None = Form(None),
                            email: str | None = Form(None),
                            content: str= Form(...),
                            files: list[UploadFile] | None = File(None)):
    feedback_data = FeedbackCreate(full_name=full_name, phone_number=phone_number, email=email, content=content, files=files)
    feedback_service = FeedbackService()
    await feedback_service.create_feedback(feedback_data=feedback_data)
    return make_response_object(data="Gửi phản hồi góp ý thành công")