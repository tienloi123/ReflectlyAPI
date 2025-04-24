import logging
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from app.constant import GOOGLE_SCOPES, AppStatus
from app.core import settings, error_exception_handler
from app.schemas import FeedbackCreate
from app.utils import convert_datetime_to_str

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        self.sheet_service = self._get_service('sheets', 'v4')

    @staticmethod
    def _get_service(api, version):
        creds = Credentials.from_service_account_info(
            {
                "type": "service_account",
                "project_id": settings.GOOGLE_PROJECT_ID,
                "private_key_id": settings.GOOGLE_PRIVATE_KEY_ID,
                "private_key": settings.GOOGLE_PRIVATE_KEY.replace('\\n', '\n'),
                "client_email": settings.GOOGLE_CLIENT_EMAIL,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": settings.GOOGLE_CLIENT_X509_CERT_URL,
                "universe_domain": "googleapis.com"
            },
            scopes=GOOGLE_SCOPES
        )
        return build(api, version, credentials=creds, cache_discovery=False)

    def insert_data_to_sheet(self, values: list[list[str]]):
        sheet_metadata = self.sheet_service.spreadsheets().get(spreadsheetId=settings.GOOGLE_SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', [])

        if sheets:
            sheet_name = sheets[0]['properties']['title']
            range_ = f"{sheet_name}!A1"
        else:
            msg = f"Không tìm thấy sheet trong bảng tính."
            logger.error(msg, exc_info=ValueError(AppStatus.ERROR_400_INVALID_DATA))
            raise error_exception_handler(app_status=AppStatus.ERROR_400_INVALID_DATA, description=msg)

        body = {
            'values': values
        }

        request = self.sheet_service.spreadsheets().values().append(
            spreadsheetId=settings.GOOGLE_SPREADSHEET_ID, range=range_,
            valueInputOption="USER_ENTERED", body=body, insertDataOption="INSERT_ROWS")
        request.execute()

    async def create_feedback(self, feedback_data: FeedbackCreate):
        values = {
            **feedback_data.dict(),
            "created_at": convert_datetime_to_str(datetime.now()),
        }
        self.insert_data_to_sheet(values=[list(values.values())])
