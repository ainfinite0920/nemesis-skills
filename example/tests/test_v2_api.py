import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.persistence.database import Base, get_db
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_v2.db"

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
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


class TestTemplateAPI:
    def test_create_template(self, client):
        response = client.post("/api/templates", json={
            "title": "风景图模板",
            "content": "生成一张{{style}}风格的{{subject}}图片",
            "type": "image",
            "variables": [
                {"name": "style", "type": "select", "options": ["写实", "卡通", "油画"], "default": "写实"},
                {"name": "subject", "type": "text", "required": True}
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "风景图模板"
        assert len(data["variables"]) == 2

    def test_instantiate_template(self, client):
        create_resp = client.post("/api/templates", json={
            "title": "测试模板",
            "content": "生成{{style}}风格的{{subject}}",
            "type": "image",
            "variables": [
                {"name": "style", "type": "text", "default": "写实"},
                {"name": "subject", "type": "text", "required": True}
            ]
        })
        template_id = create_resp.json()["id"]

        response = client.post(f"/api/templates/{template_id}/instantiate", json={
            "variables": {"subject": "日落"},
            "save_as_prompt": False
        })
        assert response.status_code == 200
        data = response.json()
        assert "写实风格的日落" in data["content"]

    def test_validate_template(self, client):
        create_resp = client.post("/api/templates", json={
            "title": "验证模板",
            "content": "生成{{style}}图片",
            "type": "image",
            "variables": [{"name": "style", "type": "text"}]
        })
        template_id = create_resp.json()["id"]

        response = client.post(f"/api/templates/{template_id}/validate")
        assert response.status_code == 200
        assert response.json()["valid"] == True


class TestWorkflowAPI:
    def test_create_workflow(self, client):
        response = client.post("/api/workflows", json={
            "name": "测试工作流",
            "type": "image",
            "description": "测试工作流描述",
            "steps": [
                {"id": "step_1", "name": "第一步", "type": "prompt", "prompt_id": None, "order": 1}
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试工作流"

    def test_list_workflows(self, client):
        client.post("/api/workflows", json={
            "name": "工作流1",
            "type": "image",
            "steps": []
        })
        response = client.get("/api/workflows")
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestImportExportAPI:
    def test_export_json(self, client):
        client.post("/api/prompts", json={
            "title": "测试提示词",
            "content": "测试内容",
            "type": "image"
        })
        
        response = client.get("/api/export?format=json")
        assert response.status_code == 200
        
        data = json.loads(response.text)
        assert "prompts" in data
        assert "version" in data

    def test_export_csv(self, client):
        client.post("/api/prompts", json={
            "title": "CSV测试",
            "content": "内容",
            "type": "image"
        })
        
        response = client.get("/api/export?format=csv")
        assert response.status_code == 200
        assert "title,content" in response.text

    def test_export_markdown(self, client):
        client.post("/api/prompts", json={
            "title": "MD测试",
            "content": "内容",
            "type": "image"
        })
        
        response = client.get("/api/export?format=markdown")
        assert response.status_code == 200
        assert "# 提示词" in response.text

    def test_import_json(self, client):
        import_data = {
            "version": "2.0",
            "prompts": [
                {
                    "title": "导入测试",
                    "content": "导入内容",
                    "type": "image"
                }
            ],
            "tags": [{"name": "测试标签", "color": "#FF0000"}],
            "categories": [{"name": "测试分类", "type": "image"}]
        }
        
        response = client.post("/api/import", json=import_data)
        assert response.status_code == 200
        stats = response.json()["stats"]
        assert stats["prompts"] == 1
        assert stats["tags"] == 1
        assert stats["categories"] == 1