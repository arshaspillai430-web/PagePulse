import pytest

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# Happy path test
def test_valid_url(client):

    response = client.post(
        "/audit",
        json={
            "url": "https://example.com"
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["status_code"] == 200
    assert "title" in data


# Failure case 1: Invalid URL
def test_invalid_url(client):

    response = client.post(
        "/audit",
        json={
            "url": "hello"
        }
    )

    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data


# Failure case 2: Website not reachable
def test_unreachable_url(client):

    response = client.post(
        "/audit",
        json={
            "url": "https://thisdoesnotexist123456789.com"
        }
    )

    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data