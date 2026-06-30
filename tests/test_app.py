import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new@student.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@student.com for Chess Club"}
    assert "new@student.com" in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    existing_email = original_activities["Chess Club"]["participants"][0]
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_invalid_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "test@student.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant(client):
    email = original_activities["Chess Club"]["participants"][0]
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_delete_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "missing@student.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
