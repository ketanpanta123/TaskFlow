import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from main import app
from database import get_db
from db_models import Base

load_dotenv()

TEST_DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/"
    f"taskflow_test"
)

test_engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture
def client():
    Base.metadata.create_all(test_engine)

    def override_get_db():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def user_a(client):
    response = client.post(
        "/users/register",
        json={
            "username": "usera",
            "email": "usera@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201

    login = client.post(
        "/auth/login",
        data={
            "username": "usera@example.com",
            "password": "password123"
        }
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {
        "token": token,
        "headers": {
            "Authorization": f"Bearer {token}"
        }
    }


@pytest.fixture
def user_b(client):
    response = client.post(
        "/users/register",
        json={
            "username": "userb",
            "email": "userb@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201

    login = client.post(
        "/auth/login",
        data={
            "username": "userb@example.com",
            "password": "password123"
        }
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {
        "token": token,
        "headers": {
            "Authorization": f"Bearer {token}"
        }
    }


@pytest.fixture
def project_a(client, user_a):
    response = client.post(
        "/projects/",
        headers=user_a["headers"],
        json={
            "name": "Project A"
        }
    )

    assert response.status_code == 201

    return response.json()