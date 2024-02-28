def test_get_projects__unauthorized(test_client):
    response = test_client.get("/api/projects")
    assert response.status_code == 401


def test_get_projects__authorized(test_client, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = test_client.get("/api/projects", headers=headers)
    assert response.status_code == 200
