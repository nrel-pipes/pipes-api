from __future__ import annotations


def test_healthcheck(client):
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
