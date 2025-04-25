import logging
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from app.constant import GOOGLE_SCOPES, AppStatus
from app.core import settings, error_exception_handler
from app.schemas.feedback_schemas import ConsultationCreate, WarrantyCreate, ComplaintCreate
from app.utils import convert_datetime_to_str
from googleapiclient.http import MediaIoBaseUpload
import io
from fastapi import UploadFile
logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        self.drive_service = self._get_service('drive', 'v3')
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

    def insert_data_to_sheet(self, values: list[list[str]], sheet_name: str):
        try:
            sheet_metadata = self.sheet_service.spreadsheets().get(
                spreadsheetId=settings.GOOGLE_SPREADSHEET_ID).execute()
            sheets = sheet_metadata.get('sheets', [])

            sheet_names = [sheet['properties']['title'] for sheet in sheets]
            if sheet_name not in sheet_names:
                self.create_sheet(sheet_name)

            range_ = f"{sheet_name}!A1"

            body = {'values': values}

            request = self.sheet_service.spreadsheets().values().append(
                spreadsheetId=settings.GOOGLE_SPREADSHEET_ID,
                range=range_,
                valueInputOption="USER_ENTERED",
                body=body,
                insertDataOption="INSERT_ROWS"
            )
            request.execute()

        except Exception as e:
            logger.error(f"Error while inserting data to sheet: {e}", exc_info=True)
            raise error_exception_handler(app_status=AppStatus.ERROR_400_INVALID_DATA, description=str(e))

    def upload_multiple_to_drive(self, parent_folder_id: str, folder_name: str, files: list[UploadFile]):
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = self.drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')

        for file in files:
            file_data = io.BytesIO(file.file.read())
            media = MediaIoBaseUpload(file_data, mimetype='application/octet-stream')
            file_metadata = {
                'name': file.filename,
                'parents': [folder_id]
            }
            self.drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

        folder_link = f'https://drive.google.com/drive/folders/{folder_id}'
        return folder_link

    def create_parent_folder(self, parent_folder_name: str):
        parent_folder_id = self.get_or_create_folder(parent_folder_name)
        return parent_folder_id

    def get_or_create_folder(self, folder_name: str):
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
        results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])
        if not folders:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [settings.GOOGLE_DRIVE_FOLDER_ID]
            }
            folder = self.drive_service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
        else:
            folder_id = folders[0]['id']

        return folder_id

    def create_sheet(self, sheet_name: str):
        try:
            requests = [{
                "addSheet": {
                    "properties": {
                        "title": sheet_name,
                        "gridProperties": {
                            "rowCount": 1000,
                            "columnCount": 26
                        }
                    }
                }
            }]

            batch_update_request = {
                'requests': requests
            }

            self.sheet_service.spreadsheets().batchUpdate(
                spreadsheetId=settings.GOOGLE_SPREADSHEET_ID,
                body=batch_update_request
            ).execute()

            logger.info(f"Sheet '{sheet_name}' created successfully.")
        except Exception as e:
            logger.error(f"Error while creating sheet: {e}", exc_info=True)
            raise error_exception_handler(app_status=AppStatus.ERROR_400_INVALID_DATA, description=str(e))

    async def create_consultation(self, feedback_data: ConsultationCreate):
        values = {
            **feedback_data.dict(),
            "created_at": convert_datetime_to_str(datetime.now()),
        }
        self.insert_data_to_sheet(values=[list(values.values())], sheet_name="Consultation")

    async def create_warranty(self, feedback_data: WarrantyCreate, files: list[UploadFile] | None = None):
        folder_name = f"warranty_{feedback_data.conversation_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        parent_folder_id = self.create_parent_folder("Warranty")

        folder_link = None
        if files:
            folder_link = self.upload_multiple_to_drive(parent_folder_id=parent_folder_id, folder_name=folder_name, files=files)

        values = {
            **feedback_data.dict(),
            "image_urls": f'=HYPERLINK("{folder_link}"; "Đường dẫn đến thư mục ảnh")' if folder_link else "",
            "created_at": convert_datetime_to_str(datetime.now()),
        }

        self.insert_data_to_sheet(values=[list(values.values())], sheet_name="Warranty")

    async def create_complaint(self, feedback_data: ComplaintCreate, files: list[UploadFile] | None = None):
        folder_name = f"complaint_{feedback_data.conversation_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        parent_folder_id = self.create_parent_folder("Complaint")

        # Upload ảnh nếu có
        folder_link = None
        if files:
            folder_link = self.upload_multiple_to_drive(parent_folder_id=parent_folder_id, folder_name=folder_name, files=files)
        values = {
            **feedback_data.dict(),
            "image_urls": f'=HYPERLINK("{folder_link}"; "Đường dẫn đến thư mục ảnh")' if folder_link else "",
            "created_at": convert_datetime_to_str(datetime.now()),
        }
        self.insert_data_to_sheet(values=[list(values.values())], sheet_name="Complaint")
