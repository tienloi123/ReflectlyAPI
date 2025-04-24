import logging
import re

from fastapi import UploadFile
from pydantic import BaseModel, root_validator, validator

from app.constant import AppStatus
from app.core import error_exception_handler

logger = logging.getLogger(__name__)

class FeedbackCreate(BaseModel):
    full_name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    content: str
    files: list[UploadFile] | None = None

    @root_validator(pre=True)
    def check_values(cls, values):
        phone_number = values.get('phone_number', None)
        email = values.get('email', None)

        if phone_number is None and email is None:
            msg = f"Số điện thoại hoặc email không được để trống."
            logger.error(msg, exc_info=ValueError(AppStatus.ERROR_400_INVALID_DATA))
            raise error_exception_handler(app_status=AppStatus.ERROR_400_INVALID_DATA, description=msg)

        return values

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