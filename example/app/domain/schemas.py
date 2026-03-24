from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime
from app.domain.entities.models import PromptType, AttachmentType, WorkflowStatus, ExecutionStatus


class TagBase(BaseModel):
    name: str
    color: str = "#3B82F6"


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    type: PromptType
    description: Optional[str] = None
    parent_id: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ModelBase(BaseModel):
    name: str
    type: PromptType
    provider: str
    description: Optional[str] = None
    parameters: Optional[dict] = None


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict] = None


class ModelResponse(ModelBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AttachmentResponse(BaseModel):
    id: str
    prompt_id: str
    file_name: str
    file_type: AttachmentType
    mime_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True


class PromptBase(BaseModel):
    title: str
    content: str
    type: PromptType
    description: Optional[str] = None
    category_id: Optional[str] = None
    model_id: Optional[str] = None


class PromptCreate(PromptBase):
    tag_ids: Optional[List[str]] = None


class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    model_id: Optional[str] = None


class PromptResponse(PromptBase):
    id: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True


class PromptListResponse(BaseModel):
    id: str
    title: str
    type: PromptType
    description: Optional[str] = None
    created_at: datetime
    category: Optional[CategoryResponse] = None
    model: Optional[ModelResponse] = None
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


class SearchParams(BaseModel):
    q: Optional[str] = None
    type: Optional[PromptType] = None
    category_id: Optional[str] = None
    tag_ids: Optional[str] = None
    model_id: Optional[str] = None
    page: int = 1
    page_size: int = 20


class VariableDefinition(BaseModel):
    name: str
    type: str = "text"
    label: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None
    options: Optional[List[str]] = None
    description: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class TemplateBase(BaseModel):
    title: str
    content: str
    type: PromptType
    description: Optional[str] = None
    category_id: Optional[str] = None
    variables: List[VariableDefinition] = []


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    variables: Optional[List[VariableDefinition]] = None


class TemplateResponse(TemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InstantiateRequest(BaseModel):
    variables: Dict[str, Any]
    save_as_prompt: bool = False
    prompt_title: Optional[str] = None


class InstantiateResponse(BaseModel):
    content: str
    prompt_id: Optional[str] = None


class WorkflowStep(BaseModel):
    id: str
    name: str
    type: str
    template_id: Optional[str] = None
    prompt_id: Optional[str] = None
    inputs: Dict[str, Any] = {}
    outputs: List[str] = []
    order: int
    condition: Optional[str] = None
    on_failure: str = "stop"


class WorkflowBase(BaseModel):
    name: str
    type: PromptType
    description: Optional[str] = None
    steps: List[WorkflowStep] = []


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[WorkflowStep]] = None
    status: Optional[WorkflowStatus] = None


class WorkflowResponse(WorkflowBase):
    id: str
    status: WorkflowStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StepExecution(BaseModel):
    step_id: str
    status: ExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WorkflowExecutionBase(BaseModel):
    workflow_id: str
    inputs: Optional[Dict[str, Any]] = None


class WorkflowExecutionCreate(WorkflowExecutionBase):
    pass


class WorkflowExecutionResponse(WorkflowExecutionBase):
    id: str
    status: ExecutionStatus
    outputs: Optional[Dict[str, Any]] = None
    step_executions: List[StepExecution] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExecuteWorkflowRequest(BaseModel):
    inputs: Optional[Dict[str, Any]] = None


class ExportRequest(BaseModel):
    format: str = "json"
    prompt_ids: Optional[List[str]] = None
    category_id: Optional[str] = None
    tag_ids: Optional[List[str]] = None
    include_templates: bool = False


class ImportData(BaseModel):
    version: str = "2.0"
    prompts: Optional[List[Dict[str, Any]]] = None
    templates: Optional[List[Dict[str, Any]]] = None
    categories: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[Dict[str, Any]]] = None
    models: Optional[List[Dict[str, Any]]] = None