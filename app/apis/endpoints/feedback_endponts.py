import logging

from fastapi import APIRouter, Form,UploadFile, File

from app.constant import UrgencyLevelEnum
from app.core.exceptions import make_response_object
from app.schemas.feedback_schemas import ConsultationCreate, WarrantyCreate, ComplaintCreate
from app.services import FeedbackService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/consultation")
async def create_consultation(feedback_data: ConsultationCreate):
    feedback_service = FeedbackService()
    await feedback_service.create_consultation(feedback_data=feedback_data)
    return make_response_object(data="Gửi phản hồi tư vấn dịch vụ thành công")

@router.post("/warranty")
async def create_warranty(full_name: str = Form(...),
    phone_number: str = Form(None),
    email: str = Form(None),
    conversation_code: str = Form(...),
    product_type: str = Form(...),
    start_date: str = Form(...),
    issue_description: str = Form(...),
    files: list[UploadFile] = File(None)):
    feedback_data = WarrantyCreate(
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        conversation_code=conversation_code,
        product_type=product_type,
        start_date=start_date,
        issue_description=issue_description,
    )
    feedback_service = FeedbackService()
    await feedback_service.create_warranty(feedback_data=feedback_data,files=files)
    return make_response_object(data="Gửi phản hồi bảo hành thành công")

@router.post("/complaint")
async def create_complaint(full_name: str = Form(...),
    phone_number: str = Form(None),
    email: str = Form(None),
    conversation_code: str = Form(...),
    complaint_issue: str = Form(...),
    urgency_level: UrgencyLevelEnum = Form(...),
    files: list[UploadFile] = File(None)):
    feedback_data = ComplaintCreate(
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        conversation_code=conversation_code,
        complaint_issue=complaint_issue,
        urgency_level=urgency_level,
    )
    feedback_service = FeedbackService()
    await feedback_service.create_complaint(feedback_data=feedback_data,files=files)
    return make_response_object(data="Gửi phản hồi khiếu nại thành công")