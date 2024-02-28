import pytest

from pipes.users.schemas import TeamDocument, UserDocument


@pytest.fixture
def setup_teams():
    # Teams
    team1 = TeamDocument(
        name="team1",
        description="This is team one",
    )
    team1.insert()

    team2 = TeamDocument(
        name="team2",
        description="This is team two",
    )
    team2.insert()

    # Users
    user1 = UserDocument(
        email="user1@example.com",
    )
    user1.insert()

    user2 = UserDocument(
        email="user2@example.com",
    )
    user2.insert()

    # Add users to team
    team1.members.extend([user1, user2])
    team1.save()


def test_get_team_by_name(test_client):
    response = test_client.get("/api/teams/?name=team1")
    assert response.status_code == 200
