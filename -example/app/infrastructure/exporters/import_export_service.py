import json
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.domain.entities.models import Prompt, Category, Tag, Model, Template, PromptTag
from app.infrastructure.persistence.repositories import (
    PromptRepositoryImpl, CategoryRepositoryImpl, TagRepositoryImpl,
    ModelRepositoryImpl, TemplateRepositoryImpl
)


class ImportExportService:
    def __init__(self):
        self.prompt_repo = PromptRepositoryImpl()
        self.category_repo = CategoryRepositoryImpl()
        self.tag_repo = TagRepositoryImpl()
        self.model_repo = ModelRepositoryImpl()
        self.template_repo = TemplateRepositoryImpl()

    def export_json(self, db: Session, prompt_ids: List[str] = None, 
                    category_id: str = None, tag_ids: List[str] = None,
                    include_templates: bool = False) -> str:
        data = {
            "version": "2.0",
            "exported_at": datetime.utcnow().isoformat(),
            "prompts": [],
            "templates": [],
            "categories": [],
            "tags": [],
            "models": []
        }

        prompts = self._get_prompts_for_export(db, prompt_ids, category_id, tag_ids)
        
        category_ids = set()
        model_ids = set()
        tag_ids_used = set()

        for prompt in prompts:
            prompt_data = {
                "id": prompt.id,
                "title": prompt.title,
                "content": prompt.content,
                "type": prompt.type.value if prompt.type else None,
                "description": prompt.description,
                "category": None,
                "model": None,
                "tags": []
            }

            if prompt.category_id:
                category_ids.add(prompt.category_id)
                prompt_data["category"] = prompt.category.name if prompt.category else None

            if prompt.model_id:
                model_ids.add(prompt.model_id)
                prompt_data["model"] = prompt.model.name if prompt.model else None

            for tag in prompt.tags:
                tag_ids_used.add(tag.id)
                prompt_data["tags"].append(tag.name)

            data["prompts"].append(prompt_data)

        if include_templates:
            templates = self.template_repo.get_all(db)
            for template in templates:
                data["templates"].append({
                    "id": template.id,
                    "title": template.title,
                    "content": template.content,
                    "type": template.type.value if template.type else None,
                    "description": template.description,
                    "variables": template.variables
                })

        for cat_id in category_ids:
            cat = self.category_repo.get_by_id(db, cat_id)
            if cat:
                data["categories"].append({
                    "id": cat.id,
                    "name": cat.name,
                    "type": cat.type.value if cat.type else None,
                    "description": cat.description
                })

        for tag_id in tag_ids_used:
            tag = self.tag_repo.get_by_id(db, tag_id)
            if tag:
                data["tags"].append({
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color
                })

        for model_id in model_ids:
            model = self.model_repo.get_by_id(db, model_id)
            if model:
                data["models"].append({
                    "id": model.id,
                    "name": model.name,
                    "type": model.type.value if model.type else None,
                    "provider": model.provider,
                    "description": model.description,
                    "parameters": model.parameters
                })

        return json.dumps(data, ensure_ascii=False, indent=2)

    def export_csv(self, db: Session, prompt_ids: List[str] = None,
                   category_id: str = None, tag_ids: List[str] = None) -> str:
        prompts = self._get_prompts_for_export(db, prompt_ids, category_id, tag_ids)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["title", "content", "type", "category", "tags", "model", "description"])
        
        for prompt in prompts:
            writer.writerow([
                prompt.title,
                prompt.content,
                prompt.type.value if prompt.type else "",
                prompt.category.name if prompt.category else "",
                ",".join([t.name for t in prompt.tags]) if prompt.tags else "",
                prompt.model.name if prompt.model else "",
                prompt.description or ""
            ])
        
        return output.getvalue()

    def export_markdown(self, db: Session, prompt_ids: List[str] = None,
                        category_id: str = None, tag_ids: List[str] = None) -> str:
        prompts = self._get_prompts_for_export(db, prompt_ids, category_id, tag_ids)
        
        lines = []
        
        for prompt in prompts:
            lines.append(f"# 提示词：{prompt.title}\n")
            lines.append(f"- **类型**: {prompt.type.value if prompt.type else ''}")
            lines.append(f"- **分类**: {prompt.category.name if prompt.category else '无'}")
            lines.append(f"- **标签**: {', '.join([t.name for t in prompt.tags]) if prompt.tags else '无'}")
            lines.append(f"- **模型**: {prompt.model.name if prompt.model else '无'}\n")
            lines.append("## 内容\n")
            lines.append(prompt.content)
            
            if prompt.description:
                lines.append(f"\n## 描述\n{prompt.description}")
            
            lines.append("\n---\n")
        
        return "\n".join(lines)

    def import_json(self, db: Session, data: Dict[str, Any]) -> Dict[str, int]:
        stats = {"prompts": 0, "templates": 0, "categories": 0, "tags": 0, "models": 0}

        for tag_data in (data.get("tags") or []):
            existing = self.tag_repo.get_by_name(db, tag_data["name"])
            if not existing:
                tag = Tag(name=tag_data["name"], color=tag_data.get("color", "#3B82F6"))
                self.tag_repo.create(db, tag)
                stats["tags"] += 1

        for cat_data in (data.get("categories") or []):
            existing = self.category_repo.get_by_name(db, cat_data["name"], cat_data.get("type"))
            if not existing:
                from app.domain.entities.models import PromptType
                cat = Category(
                    name=cat_data["name"],
                    type=PromptType(cat_data["type"]) if cat_data.get("type") else PromptType.IMAGE,
                    description=cat_data.get("description")
                )
                self.category_repo.create(db, cat)
                stats["categories"] += 1

        for model_data in (data.get("models") or []):
            existing = self.model_repo.get_by_name(db, model_data["name"], model_data.get("type"))
            if not existing:
                from app.domain.entities.models import PromptType
                model = Model(
                    name=model_data["name"],
                    type=PromptType(model_data["type"]) if model_data.get("type") else PromptType.IMAGE,
                    provider=model_data["provider"],
                    description=model_data.get("description"),
                    parameters=model_data.get("parameters")
                )
                self.model_repo.create(db, model)
                stats["models"] += 1

        for prompt_data in (data.get("prompts") or []):
            from app.domain.entities.models import PromptType
            category_id = None
            if prompt_data.get("category"):
                cat = self.category_repo.get_by_name(db, prompt_data["category"], prompt_data.get("type"))
                if cat:
                    category_id = cat.id

            model_id = None
            if prompt_data.get("model"):
                model = self.model_repo.get_by_name(db, prompt_data["model"], prompt_data.get("type"))
                if model:
                    model_id = model.id

            prompt = Prompt(
                title=prompt_data["title"],
                content=prompt_data["content"],
                type=PromptType(prompt_data["type"]) if prompt_data.get("type") else PromptType.IMAGE,
                description=prompt_data.get("description"),
                category_id=category_id,
                model_id=model_id
            )
            prompt = self.prompt_repo.create(db, prompt)

            for tag_name in prompt_data.get("tags", []):
                tag = self.tag_repo.get_by_name(db, tag_name)
                if tag:
                    prompt_tag = PromptTag(prompt_id=prompt.id, tag_id=tag.id)
                    db.add(prompt_tag)
            db.commit()

            stats["prompts"] += 1

        for template_data in (data.get("templates") or []):
            from app.domain.entities.models import PromptType
            template = Template(
                title=template_data["title"],
                content=template_data["content"],
                type=PromptType(template_data["type"]) if template_data.get("type") else PromptType.IMAGE,
                description=template_data.get("description"),
                variables=template_data.get("variables", [])
            )
            self.template_repo.create(db, template)
            stats["templates"] += 1

        return stats

    def _get_prompts_for_export(self, db: Session, prompt_ids: List[str] = None,
                                  category_id: str = None, tag_ids: List[str] = None) -> List[Prompt]:
        if prompt_ids:
            return self.prompt_repo.get_by_ids(db, prompt_ids)
        
        query = db.query(Prompt).filter(Prompt.deleted_at.is_(None))
        
        if category_id:
            query = query.filter(Prompt.category_id == category_id)
        
        if tag_ids:
            query = query.join(PromptTag).filter(PromptTag.tag_id.in_(tag_ids))
        
        return query.all()