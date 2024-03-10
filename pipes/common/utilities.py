from __future__ import annotations

from datetime import datetime
from typing import Any

from dateutil import parser
from shortuuid import ShortUUID


def generate_shortuuid() -> str:
    """Generate short identifier for public exposure"""
    _shortuuid = ShortUUID()
    return _shortuuid.random(length=8)


def parse_datatime(value: Any) -> datetime:
    """Parse datetime from given value"""
    if isinstance(value, datetime):
        return value
    else:
        value = str(value)

    value = parser.parse(value)
    return value
