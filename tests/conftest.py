import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.main import app
from app.models.models import Base

engine = create_engine("sqlite://", connect_args={"check_same_thread": False})

_connection = engine.connect()


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSession = sessionmaker(bind=_connection)


@pytest.fixture(autouse=True)
def _reset_tables():
    Base.metadata.create_all(_connection)
    yield
    Base.metadata.drop_all(_connection)


@pytest.fixture()
def client():
    def _override():
        session = TestSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def _register_and_login(client, username="testuser", email="test@example.com", password="securepass123"):
    client.post("/auth/register", json={"username": username, "email": email, "password": password})
    resp = client.post("/auth/login", data={"username": username, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers(client):
    return _register_and_login(client)


@pytest.fixture()
def bookmark(client, auth_headers):
    resp = client.post(
        "/bookmarks",
        json={"url": "https://example.com", "title": "Example", "tag_names": ["dev", "python"]},
        headers=auth_headers,
    )
    return resp.json()
