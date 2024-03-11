from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from dateutil import parser
from pydantic import EmailStr
from shortuuid import ShortUUID

from pipes.common.mapping import DNS_ORG_MAPPING


def generate_shortuuid() -> str:
    """Generate short identifier for public exposure"""
    _shortuuid = ShortUUID()
    return _shortuuid.random(length=8)


def parse_datetime(value: Any) -> datetime:
    """Parse datetime from given value"""
    if isinstance(value, datetime):
        return value
    else:
        value = str(value)

    value = parser.parse(value)

    # remove tzinfo
    native_value = value.astimezone(timezone.utc).replace(tzinfo=None)

    return native_value


def parse_organization(email: EmailStr) -> str | None:
    """Parse organization based on email domain"""
    domain = email.lower().split("@")[1]
    if domain in DNS_ORG_MAPPING:
        return DNS_ORG_MAPPING[domain]
    return None
