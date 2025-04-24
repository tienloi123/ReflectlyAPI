from enum import Enum


class ProjectBuildTypes(str, Enum):
    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"


class SwaggerPaths(str, Enum):
    RE_DOC = "/api/redoc"
    DOCS = "/api/docs"


BasePath: str = "/api"
