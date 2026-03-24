from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.models import (
    Prompt, Category, Tag, Model, Attachment, PromptTag,
    Template, Workflow, WorkflowExecution, WorkflowStatus
)
from app.domain.schemas import (
    PromptCreate, PromptUpdate, PromptResponse,
    CategoryCreate, CategoryUpdate,
    TagCreate,
    ModelCreate, ModelUpdate,
    TemplateCreate, TemplateUpdate,
    WorkflowCreate, WorkflowUpdate,
    InstantiateRequest
)
from app.infrastructure.persistence.repositories import (
    PromptRepositoryImpl, CategoryRepositoryImpl, TagRepositoryImpl,
    ModelRepositoryImpl, AttachmentRepositoryImpl,
    TemplateRepositoryImpl, WorkflowRepositoryImpl, WorkflowExecutionRepositoryImpl
)
from app.domain.services.template_service import TemplateService as TemplateDomainService
from app.domain.services.workflow_engine import WorkflowEngine
from app.config import settings
import os
import uuid
import shutil


class PromptService:
    def __init__(self):
        self.repo = PromptRepositoryImpl()
        self.tag_repo = TagRepositoryImpl()

    def get_prompt(self, db: Session, prompt_id: str) -> Optional[Prompt]:
        return self.repo.get_by_id(db, prompt_id)

    def list_prompts(self, db: Session, skip: int = 0, limit: int = 20) -> List[Prompt]:
        return self.repo.get_all(db, skip, limit)

    def search_prompts(self, db: Session, q: str = None, type: str = None,
                       category_id: str = None, tag_ids: str = None,
                       model_id: str = None, page: int = 1, page_size: int = 20) -> List[Prompt]:
        tag_id_list = tag_ids.split(",") if tag_ids else None
        skip = (page - 1) * page_size
        return self.repo.search(db, q, type, category_id, tag_id_list, model_id, skip, page_size)

    def create_prompt(self, db: Session, data: PromptCreate) -> Prompt:
        prompt = Prompt(
            title=data.title,
            content=data.content,
            type=data.type,
            description=data.description,
            category_id=data.category_id,
            model_id=data.model_id
        )
        prompt = self.repo.create(db, prompt)
        
        if data.tag_ids:
            for tag_id in data.tag_ids:
                tag = self.tag_repo.get_by_id(db, tag_id)
                if tag:
                    prompt_tag = PromptTag(prompt_id=prompt.id, tag_id=tag_id)
                    db.add(prompt_tag)
            db.commit()
        
        return prompt

    def update_prompt(self, db: Session, prompt_id: str, data: PromptUpdate) -> Optional[Prompt]:
        prompt = self.repo.get_by_id(db, prompt_id)
        if not prompt:
            return None
        
        if data.title is not None:
            prompt.title = data.title
        if data.content is not None:
            prompt.content = data.content
        if data.description is not None:
            prompt.description = data.description
        if data.category_id is not None:
            prompt.category_id = data.category_id
        if data.model_id is not None:
            prompt.model_id = data.model_id
        
        return self.repo.update(db, prompt)

    def delete_prompt(self, db: Session, prompt_id: str) -> bool:
        return self.repo.delete(db, prompt_id)

    def add_tag(self, db: Session, prompt_id: str, tag_id: str) -> bool:
        prompt = self.repo.get_by_id(db, prompt_id)
        tag = self.tag_repo.get_by_id(db, tag_id)
        if not prompt or not tag:
            return False
        
        prompt_tag = PromptTag(prompt_id=prompt_id, tag_id=tag_id)
        db.add(prompt_tag)
        db.commit()
        return True

    def remove_tag(self, db: Session, prompt_id: str, tag_id: str) -> bool:
        prompt_tag = db.query(PromptTag).filter(
            PromptTag.prompt_id == prompt_id,
            PromptTag.tag_id == tag_id
        ).first()
        if prompt_tag:
            db.delete(prompt_tag)
            db.commit()
            return True
        return False


class CategoryService:
    def __init__(self):
        self.repo = CategoryRepositoryImpl()

    def get_category(self, db: Session, category_id: str) -> Optional[Category]:
        return self.repo.get_by_id(db, category_id)

    def list_categories(self, db: Session, type: str = None) -> List[Category]:
        return self.repo.get_all(db, type)

    def create_category(self, db: Session, data: CategoryCreate) -> Category:
        category = Category(
            name=data.name,
            type=data.type,
            description=data.description,
            parent_id=data.parent_id
        )
        return self.repo.create(db, category)

    def update_category(self, db: Session, category_id: str, data: CategoryUpdate) -> Optional[Category]:
        category = self.repo.get_by_id(db, category_id)
        if not category:
            return None
        
        if data.name is not None:
            category.name = data.name
        if data.description is not None:
            category.description = data.description
        
        return self.repo.update(db, category)

    def delete_category(self, db: Session, category_id: str) -> bool:
        return self.repo.delete(db, category_id)


class TagService:
    def __init__(self):
        self.repo = TagRepositoryImpl()

    def get_tag(self, db: Session, tag_id: str) -> Optional[Tag]:
        return self.repo.get_by_id(db, tag_id)

    def list_tags(self, db: Session) -> List[Tag]:
        return self.repo.get_all(db)

    def create_tag(self, db: Session, data: TagCreate) -> Tag:
        existing = self.repo.get_by_name(db, data.name)
        if existing:
            raise ValueError(f"Tag '{data.name}' already exists")
        
        tag = Tag(name=data.name, color=data.color)
        return self.repo.create(db, tag)

    def update_tag(self, db: Session, tag_id: str, data: TagCreate) -> Optional[Tag]:
        tag = self.repo.get_by_id(db, tag_id)
        if not tag:
            return None
        
        if data.name is not None:
            existing = self.repo.get_by_name(db, data.name)
            if existing and existing.id != tag_id:
                raise ValueError(f"Tag '{data.name}' already exists")
            tag.name = data.name
        if data.color is not None:
            tag.color = data.color
        
        return self.repo.update(db, tag)

    def delete_tag(self, db: Session, tag_id: str) -> bool:
        return self.repo.delete(db, tag_id)


class ModelService:
    def __init__(self):
        self.repo = ModelRepositoryImpl()

    def get_model(self, db: Session, model_id: str) -> Optional[Model]:
        return self.repo.get_by_id(db, model_id)

    def list_models(self, db: Session, type: str = None) -> List[Model]:
        return self.repo.get_all(db, type)

    def create_model(self, db: Session, data: ModelCreate) -> Model:
        model = Model(
            name=data.name,
            type=data.type,
            provider=data.provider,
            description=data.description,
            parameters=data.parameters
        )
        return self.repo.create(db, model)

    def update_model(self, db: Session, model_id: str, data: ModelUpdate) -> Optional[Model]:
        model = self.repo.get_by_id(db, model_id)
        if not model:
            return None
        
        if data.name is not None:
            model.name = data.name
        if data.provider is not None:
            model.provider = data.provider
        if data.description is not None:
            model.description = data.description
        if data.parameters is not None:
            model.parameters = data.parameters
        
        return self.repo.update(db, model)

    def delete_model(self, db: Session, model_id: str) -> bool:
        return self.repo.delete(db, model_id)


class AttachmentService:
    def __init__(self):
        self.repo = AttachmentRepositoryImpl()

    def get_attachment(self, db: Session, attachment_id: str) -> Optional[Attachment]:
        return self.repo.get_by_id(db, attachment_id)

    def get_prompt_attachments(self, db: Session, prompt_id: str) -> List[Attachment]:
        return self.repo.get_by_prompt(db, prompt_id)

    def upload_attachment(self, db: Session, prompt_id: str, file) -> Attachment:
        file_ext = file.filename.split(".")[-1].lower()
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(settings.upload_dir, file_name)
        
        os.makedirs(settings.upload_dir, exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if file_ext in ["jpg", "jpeg", "png", "gif", "webp"]:
            file_type = "image"
        elif file_ext in ["mp4", "webm", "mov"]:
            file_type = "video"
        else:
            file_type = "image"
        
        attachment = Attachment(
            prompt_id=prompt_id,
            file_path=file_path,
            file_name=file.filename,
            file_type=file_type,
            mime_type=file.content_type,
            file_size=0
        )
        
        attachment.file_size = os.path.getsize(file_path)
        
        return self.repo.create(db, attachment)

    def delete_attachment(self, db: Session, attachment_id: str) -> bool:
        attachment = self.repo.get_by_id(db, attachment_id)
        if attachment:
            if os.path.exists(attachment.file_path):
                os.remove(attachment.file_path)
            return self.repo.delete(db, attachment_id)
        return False


class TemplateService:
    def __init__(self):
        self.repo = TemplateRepositoryImpl()
        self.prompt_repo = PromptRepositoryImpl()
        self.domain_service = TemplateDomainService()

    def get_template(self, db: Session, template_id: str) -> Optional[Template]:
        return self.repo.get_by_id(db, template_id)

    def list_templates(self, db: Session, type: str = None) -> List[Template]:
        return self.repo.get_all(db, type)

    def create_template(self, db: Session, data: TemplateCreate) -> Template:
        template = Template(
            title=data.title,
            content=data.content,
            type=data.type,
            description=data.description,
            category_id=data.category_id,
            variables=[v.dict() for v in data.variables]
        )
        return self.repo.create(db, template)

    def update_template(self, db: Session, template_id: str, data: TemplateUpdate) -> Optional[Template]:
        template = self.repo.get_by_id(db, template_id)
        if not template:
            return None
        
        if data.title is not None:
            template.title = data.title
        if data.content is not None:
            template.content = data.content
        if data.description is not None:
            template.description = data.description
        if data.category_id is not None:
            template.category_id = data.category_id
        if data.variables is not None:
            template.variables = [v.dict() for v in data.variables]
        
        return self.repo.update(db, template)

    def delete_template(self, db: Session, template_id: str) -> bool:
        return self.repo.delete(db, template_id)

    def instantiate(self, db: Session, template_id: str, data: InstantiateRequest) -> dict:
        template = self.repo.get_by_id(db, template_id)
        if not template:
            raise ValueError("Template not found")
        
        from app.domain.schemas import VariableDefinition
        variables = [VariableDefinition(**v) for v in template.variables]
        content = self.domain_service.instantiate(template.content, variables, data.variables)
        
        prompt_id = None
        if data.save_as_prompt:
            prompt = Prompt(
                title=data.prompt_title or template.title,
                content=content,
                type=template.type,
                description=template.description,
                category_id=template.category_id
            )
            prompt = self.prompt_repo.create(db, prompt)
            prompt_id = prompt.id
        
        return {"content": content, "prompt_id": prompt_id}

    def validate(self, db: Session, template_id: str) -> dict:
        template = self.repo.get_by_id(db, template_id)
        if not template:
            raise ValueError("Template not found")
        
        from app.domain.schemas import VariableDefinition
        variables = [VariableDefinition(**v) for v in template.variables]
        return self.domain_service.validate_variables(template.content, variables)


class WorkflowService:
    def __init__(self):
        self.repo = WorkflowRepositoryImpl()
        self.execution_repo = WorkflowExecutionRepositoryImpl()
        self.engine = WorkflowEngine()

    def get_workflow(self, db: Session, workflow_id: str) -> Optional[Workflow]:
        return self.repo.get_by_id(db, workflow_id)

    def list_workflows(self, db: Session, status: str = None) -> List[Workflow]:
        return self.repo.get_all(db, status)

    def create_workflow(self, db: Session, data: WorkflowCreate) -> Workflow:
        workflow = Workflow(
            name=data.name,
            type=data.type,
            description=data.description,
            steps=[s.dict() for s in data.steps]
        )
        return self.repo.create(db, workflow)

    def update_workflow(self, db: Session, workflow_id: str, data: WorkflowUpdate) -> Optional[Workflow]:
        workflow = self.repo.get_by_id(db, workflow_id)
        if not workflow:
            return None
        
        if data.name is not None:
            workflow.name = data.name
        if data.description is not None:
            workflow.description = data.description
        if data.steps is not None:
            workflow.steps = [s.dict() for s in data.steps]
        if data.status is not None:
            workflow.status = data.status
        
        return self.repo.update(db, workflow)

    def delete_workflow(self, db: Session, workflow_id: str) -> bool:
        return self.repo.delete(db, workflow_id)

    def execute(self, db: Session, workflow_id: str, inputs: dict = None) -> WorkflowExecution:
        workflow = self.repo.get_by_id(db, workflow_id)
        if not workflow:
            raise ValueError("Workflow not found")
        
        if workflow.status != WorkflowStatus.ACTIVE:
            raise ValueError("Workflow is not active")
        
        return self.engine.execute(db, workflow, inputs)

    def get_executions(self, db: Session, workflow_id: str, limit: int = 20) -> List[WorkflowExecution]:
        return self.execution_repo.get_by_workflow(db, workflow_id, limit)

    def get_execution(self, db: Session, execution_id: str) -> Optional[WorkflowExecution]:
        return self.execution_repo.get_by_id(db, execution_id)

    def cancel_execution(self, db: Session, execution_id: str) -> bool:
        execution = self.execution_repo.get_by_id(db, execution_id)
        if not execution:
            return False
        
        from app.domain.entities.models import ExecutionStatus
        if execution.status == ExecutionStatus.RUNNING:
            execution.status = ExecutionStatus.CANCELLED
            self.execution_repo.update(db, execution)
            return True
        return False