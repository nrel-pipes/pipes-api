from __future__ import annotations


def test_ping(test_client):
    response = test_client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
