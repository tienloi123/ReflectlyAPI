import logging
import re

from pydantic import BaseModel, validator

from app.constant import AppStatus, FEEDBACK_FIELD_LABELS, UrgencyLevelEnum, ServiceEnum
from app.core import error_exception_handler
from fastapi import UploadFile
logger = logging.getLogger(__name__)

class FeedbackBase(BaseModel):
    full_name: str
    phone_number: str | None = None
    email: str | None = None
    conversation_code: str

    @validator('conversation_code')
    def not_empty(cls, v, field):
        if not v or not v.strip():
            msg = f"{FEEDBACK_FIELD_LABELS[field.name]} không được để trống."
            logger.error(msg, exc_info=ValueError(AppStatus.ERROR_400_INVALID_DATA))
            raise error_exception_handler(app_status=AppStatus.ERROR_400_INVALID_DATA, description=msg)
        return v

    @validator('phone_number')
    def check_phone_number_vietnamses(cls, value):
        if value:
            regex_pattern = r'^(((\+|)84)|0)(2|3|5|7|8|9)+([0-9]{8})\b'

            if not re.match(regex_pattern, value):
                msg = f"Số điện thoại không thuộc lãnh thổ Việt Nam."
                logger.error(msg, exc_info=ValueError(AppStatus.ERROR_400_INVALID_DATA))
                raise error_exception_handler(app_status=AppStatus.ERROR_400_INVALID_DATA, description=msg)
            return value

    @validator('email')
    def check_email_valid(cls, value):
        if value:
            regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
            if not re.match(regex, value):
                msg = "Email không hợp lệ."
                logger.error(msg, exc_info=ValueError(AppStatus.ERROR_400_INVALID_DATA))
                raise error_exception_handler(app_status=AppStatus.ERROR_400_INVALID_DATA, description=msg)
        return value

    class Config:
        orm_mode = True


class ConsultationCreate(FeedbackBase):
    product_interest: ServiceEnum
    conversation_summary: str

    @validator('conversation_summary')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Tổng kết cuộc hội thoại không được để trống.")
        return v

    @validator('phone_number')
    def check_phone_number_vietnamses(cls, value):
        if value:
            regex_pattern = r'^(((\+|)84)|0)(2|3|5|7|8|9)+([0-9]{8})\b'
            if not re.match(regex_pattern, value):
                raise ValueError("Số điện thoại không thuộc lãnh thổ Việt Nam.")
        return value

    class Config:
        orm_mode = True


class WarrantyCreate(FeedbackBase):
    product_type: str
    start_date: str
    issue_description: str
    image_urls: list[UploadFile] | None = None

    @validator('issue_description')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Mô tả vấn đề hiện tại không được để trống.")
        return v

    class Config:
        orm_mode = True

class ComplaintCreate(FeedbackBase):
    complaint_issue: str
    image_urls: list[UploadFile] | None = None
    urgency_level: UrgencyLevelEnum

    @validator('complaint_issue')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Vấn đề khiếu nại không được để trống.")
        return v

    class Config:
        orm_mode = True

