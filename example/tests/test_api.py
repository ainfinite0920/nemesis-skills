import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.persistence.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


class TestPromptAPI:
    def test_create_prompt(self, client):
        response = client.post("/api/prompts", json={
            "title": "Test Prompt",
            "content": "A beautiful sunset over mountains",
            "type": "image"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Prompt"
        assert data["type"] == "image"

    def test_list_prompts(self, client):
        client.post("/api/prompts", json={
            "title": "Prompt 1",
            "content": "Content 1",
            "type": "image"
        })
        response = client.get("/api/prompts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_search_prompts(self, client):
        client.post("/api/prompts", json={
            "title": "Sunset",
            "content": "Beautiful sunset",
            "type": "image"
        })
        response = client.get("/api/prompts/search?q=sunset")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


class TestCategoryAPI:
    def test_create_category(self, client):
        response = client.post("/api/categories", json={
            "name": "Nature",
            "type": "image"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nature"

    def test_list_categories(self, client):
        client.post("/api/categories", json={
            "name": "Test",
            "type": "video"
        })
        response = client.get("/api/categories")
        assert response.status_code == 200


class TestTagAPI:
    def test_create_tag(self, client):
        response = client.post("/api/tags", json={
            "name": "landscape",
            "color": "#FF0000"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "landscape"

    def test_list_tags(self, client):
        response = client.get("/api/tags")
        assert response.status_code == 200


class TestModelAPI:
    def test_create_model(self, client):
        response = client.post("/api/models", json={
            "name": "DALL-E 3",
            "type": "image",
            "provider": "OpenAI"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "DALL-E 3"

    def test_list_models(self, client):
        response = client.get("/api/models")
        assert response.status_code == 200