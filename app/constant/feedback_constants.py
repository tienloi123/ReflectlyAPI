from enum import Enum

GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

FEEDBACK_FIELD_LABELS = {
    "conversation_code": "Mã cuộc hội thoại",
    "issue": "Vấn đề"
}

class FeedbackStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"