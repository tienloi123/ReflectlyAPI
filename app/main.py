import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.constant import ProjectBuildTypes, SwaggerPaths, BasePath
from app.core import settings, validation_exception_handler
from app.routers import main_router


main_app = FastAPI(title=settings.PROJECT_NAME,
                   description=settings.PROJECT_DESCRIPTION,
                   debug=settings.DEBUG,
                   version=settings.VERSION,
                   docs_url=None if settings.PROJECT_BUILD_TYPE == ProjectBuildTypes.PRODUCTION else
                   SwaggerPaths.DOCS,
                   redoc_url=None if settings.PROJECT_BUILD_TYPE == ProjectBuildTypes.PRODUCTION else
                   SwaggerPaths.RE_DOC)

# Routers
main_app.include_router(main_router, prefix=BasePath)

# Middlewares
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Setup loggers
LOGGING_CONFIG = Path(__file__).parent / 'core/logging.conf'
logging.config.fileConfig(LOGGING_CONFIG, disable_existing_loggers=False)

# Get root logger
logger = logging.getLogger(__name__)

# Exception handlers
main_app.add_exception_handler(RequestValidationError, validation_exception_handler)

if __name__ == "__main__":
    uvicorn.run("main:main_app", host="0.0.0.0", reload=True)
