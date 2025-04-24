import json
import logging
import re
from datetime import datetime, date
from enum import Enum
from typing import Dict, Any, List
from urllib.parse import unquote

import unicodedata
from rapidfuzz import fuzz, process

from app.constant import AppStatus
from app.core import error_exception_handler

logger = logging.getLogger(__name__)


def convert_datetime_to_str(datetime_value: datetime) -> str:
    return datetime_value.strftime("%H:%M:%S %d/%m/%Y")
