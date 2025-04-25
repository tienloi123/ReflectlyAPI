from enum import Enum

GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']

FEEDBACK_FIELD_LABELS = {
    "conversation_code": "Mã cuộc hội thoại",
    "issue": "Vấn đề"
}

class FeedbackStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class ServiceEnum(str, Enum):
    CHATBOT = "Chatbot"
    RETAIL = "Retail"
    OCR = "OCR"
    CHIBOSO = "Chiboso"

class UrgencyLevelEnum(str, Enum):
    HIGH = "Cao"
    MEDIUM = "Trung Bình"
    LOW = "Thấp"