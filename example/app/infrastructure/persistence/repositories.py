from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.domain.entities.models import (
    Prompt, Category, Tag, Model, Attachment, PromptTag,
    Template, Workflow, WorkflowExecution
)


class PromptRepositoryImpl:
    def get_by_id(self, db: Session, prompt_id: str) -> Optional[Prompt]:
        return db.query(Prompt).filter(
            Prompt.id == prompt_id,
            Prompt.deleted_at.is_(None)
        ).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 20) -> List[Prompt]:
        return db.query(Prompt).filter(
            Prompt.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()

    def get_by_ids(self, db: Session, prompt_ids: List[str]) -> List[Prompt]:
        return db.query(Prompt).filter(
            Prompt.id.in_(prompt_ids),
            Prompt.deleted_at.is_(None)
        ).all()

    def search(self, db: Session, q: str = None, type: str = None, category_id: str = None,
               tag_ids: List[str] = None, model_id: str = None,
               skip: int = 0, limit: int = 20) -> List[Prompt]:
        query = db.query(Prompt).filter(Prompt.deleted_at.is_(None))
        
        if q:
            query = query.filter(or_(
                Prompt.title.ilike(f"%{q}%"),
                Prompt.content.ilike(f"%{q}%")
            ))
        
        if type:
            query = query.filter(Prompt.type == type)
        
        if category_id:
            query = query.filter(Prompt.category_id == category_id)
        
        if model_id:
            query = query.filter(Prompt.model_id == model_id)
        
        if tag_ids:
            query = query.join(PromptTag).filter(PromptTag.tag_id.in_(tag_ids))
        
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, prompt: Prompt) -> Prompt:
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        return prompt

    def update(self, db: Session, prompt: Prompt) -> Prompt:
        db.commit()
        db.refresh(prompt)
        return prompt

    def delete(self, db: Session, prompt_id: str) -> bool:
        from datetime import datetime
        prompt = self.get_by_id(db, prompt_id)
        if prompt:
            prompt.deleted_at = datetime.utcnow()
            db.commit()
            return True
        return False


class CategoryRepositoryImpl:
    def get_by_id(self, db: Session, category_id: str) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, db: Session, name: str, type: str = None) -> Optional[Category]:
        query = db.query(Category).filter(Category.name == name)
        if type:
            query = query.filter(Category.type == type)
        return query.first()

    def get_all(self, db: Session, type: str = None) -> List[Category]:
        query = db.query(Category)
        if type:
            query = query.filter(Category.type == type)
        return query.all()

    def create(self, db: Session, category: Category) -> Category:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def update(self, db: Session, category: Category) -> Category:
        db.commit()
        db.refresh(category)
        return category

    def delete(self, db: Session, category_id: str) -> bool:
        category = self.get_by_id(db, category_id)
        if category:
            db.delete(category)
            db.commit()
            return True
        return False


class TagRepositoryImpl:
    def get_by_id(self, db: Session, tag_id: str) -> Optional[Tag]:
        return db.query(Tag).filter(Tag.id == tag_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Tag]:
        return db.query(Tag).filter(Tag.name == name).first()

    def get_all(self, db: Session) -> List[Tag]:
        return db.query(Tag).all()

    def create(self, db: Session, tag: Tag) -> Tag:
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    def update(self, db: Session, tag: Tag) -> Tag:
        db.commit()
        db.refresh(tag)
        return tag

    def delete(self, db: Session, tag_id: str) -> bool:
        tag = self.get_by_id(db, tag_id)
        if tag:
            db.delete(tag)
            db.commit()
            return True
        return False


class ModelRepositoryImpl:
    def get_by_id(self, db: Session, model_id: str) -> Optional[Model]:
        return db.query(Model).filter(Model.id == model_id).first()

    def get_by_name(self, db: Session, name: str, type: str = None) -> Optional[Model]:
        query = db.query(Model).filter(Model.name == name)
        if type:
            query = query.filter(Model.type == type)
        return query.first()

    def get_all(self, db: Session, type: str = None) -> List[Model]:
        query = db.query(Model)
        if type:
            query = query.filter(Model.type == type)
        return query.all()

    def create(self, db: Session, model: Model) -> Model:
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def update(self, db: Session, model: Model) -> Model:
        db.commit()
        db.refresh(model)
        return model

    def delete(self, db: Session, model_id: str) -> bool:
        model = self.get_by_id(db, model_id)
        if model:
            db.delete(model)
            db.commit()
            return True
        return False


class AttachmentRepositoryImpl:
    def get_by_id(self, db: Session, attachment_id: str) -> Optional[Attachment]:
        return db.query(Attachment).filter(Attachment.id == attachment_id).first()

    def get_by_prompt(self, db: Session, prompt_id: str) -> List[Attachment]:
        return db.query(Attachment).filter(Attachment.prompt_id == prompt_id).all()

    def create(self, db: Session, attachment: Attachment) -> Attachment:
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        return attachment

    def delete(self, db: Session, attachment_id: str) -> bool:
        attachment = self.get_by_id(db, attachment_id)
        if attachment:
            db.delete(attachment)
            db.commit()
            return True
        return False


class TemplateRepositoryImpl:
    def get_by_id(self, db: Session, template_id: str) -> Optional[Template]:
        return db.query(Template).filter(Template.id == template_id).first()

    def get_all(self, db: Session, type: str = None) -> List[Template]:
        query = db.query(Template)
        if type:
            query = query.filter(Template.type == type)
        return query.all()

    def create(self, db: Session, template: Template) -> Template:
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    def update(self, db: Session, template: Template) -> Template:
        db.commit()
        db.refresh(template)
        return template

    def delete(self, db: Session, template_id: str) -> bool:
        template = self.get_by_id(db, template_id)
        if template:
            db.delete(template)
            db.commit()
            return True
        return False


class WorkflowRepositoryImpl:
    def get_by_id(self, db: Session, workflow_id: str) -> Optional[Workflow]:
        return db.query(Workflow).filter(Workflow.id == workflow_id).first()

    def get_all(self, db: Session, status: str = None) -> List[Workflow]:
        query = db.query(Workflow)
        if status:
            query = query.filter(Workflow.status == status)
        return query.all()

    def create(self, db: Session, workflow: Workflow) -> Workflow:
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        return workflow

    def update(self, db: Session, workflow: Workflow) -> Workflow:
        db.commit()
        db.refresh(workflow)
        return workflow

    def delete(self, db: Session, workflow_id: str) -> bool:
        workflow = self.get_by_id(db, workflow_id)
        if workflow:
            db.delete(workflow)
            db.commit()
            return True
        return False


class WorkflowExecutionRepositoryImpl:
    def get_by_id(self, db: Session, execution_id: str) -> Optional[WorkflowExecution]:
        return db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()

    def get_by_workflow(self, db: Session, workflow_id: str, limit: int = 20) -> List[WorkflowExecution]:
        return db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).order_by(WorkflowExecution.created_at.desc()).limit(limit).all()

    def create(self, db: Session, execution: WorkflowExecution) -> WorkflowExecution:
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    def update(self, db: Session, execution: WorkflowExecution) -> WorkflowExecution:
        db.commit()
        db.refresh(execution)
        return execution