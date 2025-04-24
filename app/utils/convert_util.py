import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def convert_datetime_to_str(datetime_value: datetime) -> str:
    return datetime_value.strftime("%H:%M:%S %d/%m/%Y")
