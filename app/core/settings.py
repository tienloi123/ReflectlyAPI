import os

from pydantic import BaseSettings

from app.constant import ProjectBuildTypes


class Settings(BaseSettings):
    PROJECT_NAME: str = "ReflectlyAPI"
    PROJECT_DESCRIPTION: str = """Powered by Tensor 🚀"""
    VERSION: str = "0.1-SNAPSHOT"
    ALLOW_ORIGINS: list
    DEBUG: bool = False
    PROJECT_BUILD_TYPE: str = ProjectBuildTypes.DEVELOPMENT
    # Google API
    GOOGLE_CLIENT_ID: str = "your-google-client-id"
    GOOGLE_PROJECT_ID: str = "your-google-project-id"
    GOOGLE_CLIENT_X509_CERT_URL: str = "your-google-client-x509-cert-url"
    GOOGLE_CLIENT_EMAIL: str = "your-google-client-email"
    GOOGLE_PRIVATE_KEY_ID: str = "your-google-private-key-id"
    GOOGLE_PRIVATE_KEY: str = "your-google-private-key"
    GOOGLE_SPREADSHEET_ID: str = "your-google-spreadsheet-id"
    GOOGLE_API_KEY: str = "your-google-api-key"
    GOOGLE_DRIVE_FOLDER_ID: str = "your-google-drive-folder-id"

env_file = os.getenv('ENV_FILE', '.env.dev')
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')
