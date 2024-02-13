from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(autouse=True)
def client():
    return TestClient(app)
