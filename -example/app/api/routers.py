from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.infrastructure.persistence.database import get_db
from app.domain.schemas import (
    PromptCreate, PromptUpdate, PromptResponse, PromptListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    TagCreate, TagResponse,
    ModelCreate, ModelUpdate, ModelResponse,
    AttachmentResponse,
    TemplateCreate, TemplateUpdate, TemplateResponse,
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowExecutionResponse, ExecuteWorkflowRequest, InstantiateRequest,
    ImportData
)
from app.application.services import (
    PromptService, CategoryService, TagService, ModelService, AttachmentService,
    TemplateService, WorkflowService
)
from app.infrastructure.exporters.import_export_service import ImportExportService
import json

router = APIRouter()

prompt_service = PromptService()
category_service = CategoryService()
tag_service = TagService()
model_service = ModelService()
attachment_service = AttachmentService()
template_service = TemplateService()
workflow_service = WorkflowService()
import_export_service = ImportExportService()


@router.get("/prompts", response_model=List[PromptListResponse])
def list_prompts(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    skip = (page - 1) * page_size
    prompts = prompt_service.list_prompts(db, skip, page_size)
    return prompts


@router.get("/prompts/search", response_model=List[PromptListResponse])
def search_prompts(
    q: str = None,
    type: str = None,
    category_id: str = None,
    tag_ids: str = None,
    model_id: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    prompts = prompt_service.search_prompts(
        db, q, type, category_id, tag_ids, model_id, page, page_size
    )
    return prompts


@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
def get_prompt(prompt_id: str, db: Session = Depends(get_db)):
    prompt = prompt_service.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.post("/prompts", response_model=PromptResponse)
def create_prompt(data: PromptCreate, db: Session = Depends(get_db)):
    return prompt_service.create_prompt(db, data)


@router.put("/prompts/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id: str, data: PromptUpdate, db: Session = Depends(get_db)):
    prompt = prompt_service.update_prompt(db, prompt_id, data)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: str, db: Session = Depends(get_db)):
    if not prompt_service.delete_prompt(db, prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"message": "Deleted successfully"}


@router.post("/prompts/{prompt_id}/tags/{tag_id}")
def add_tag_to_prompt(prompt_id: str, tag_id: str, db: Session = Depends(get_db)):
    if not prompt_service.add_tag(db, prompt_id, tag_id):
        raise HTTPException(status_code=404, detail="Prompt or Tag not found")
    return {"message": "Tag added successfully"}


@router.delete("/prompts/{prompt_id}/tags/{tag_id}")
def remove_tag_from_prompt(prompt_id: str, tag_id: str, db: Session = Depends(get_db)):
    if not prompt_service.remove_tag(db, prompt_id, tag_id):
        raise HTTPException(status_code=404, detail="Tag association not found")
    return {"message": "Tag removed successfully"}


@router.post("/prompts/{prompt_id}/attachments", response_model=AttachmentResponse)
def upload_attachment(prompt_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    prompt = prompt_service.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return attachment_service.upload_attachment(db, prompt_id, file)


@router.delete("/prompts/{prompt_id}/attachments/{attachment_id}")
def delete_attachment(prompt_id: str, attachment_id: str, db: Session = Depends(get_db)):
    if not attachment_service.delete_attachment(db, attachment_id):
        raise HTTPException(status_code=404, detail="Attachment not found")
    return {"message": "Attachment deleted successfully"}


@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(type: str = None, db: Session = Depends(get_db)):
    return category_service.list_categories(db, type)


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: str, db: Session = Depends(get_db)):
    category = category_service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/categories", response_model=CategoryResponse)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return category_service.create_category(db, data)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: str, data: CategoryUpdate, db: Session = Depends(get_db)):
    category = category_service.update_category(db, category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/categories/{category_id}")
def delete_category(category_id: str, db: Session = Depends(get_db)):
    if not category_service.delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Deleted successfully"}


@router.get("/tags", response_model=List[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    return tag_service.list_tags(db)


@router.post("/tags", response_model=TagResponse)
def create_tag(data: TagCreate, db: Session = Depends(get_db)):
    try:
        return tag_service.create_tag(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/tags/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: str, data: TagCreate, db: Session = Depends(get_db)):
    try:
        tag = tag_service.update_tag(db, tag_id, data)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return tag
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: str, db: Session = Depends(get_db)):
    if not tag_service.delete_tag(db, tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"message": "Deleted successfully"}


@router.get("/models", response_model=List[ModelResponse])
def list_models(type: str = None, db: Session = Depends(get_db)):
    return model_service.list_models(db, type)


@router.get("/models/{model_id}", response_model=ModelResponse)
def get_model(model_id: str, db: Session = Depends(get_db)):
    model = model_service.get_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/models", response_model=ModelResponse)
def create_model(data: ModelCreate, db: Session = Depends(get_db)):
    return model_service.create_model(db, data)


@router.put("/models/{model_id}", response_model=ModelResponse)
def update_model(model_id: str, data: ModelUpdate, db: Session = Depends(get_db)):
    model = model_service.update_model(db, model_id, data)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.delete("/models/{model_id}")
def delete_model(model_id: str, db: Session = Depends(get_db)):
    if not model_service.delete_model(db, model_id):
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Deleted successfully"}


@router.get("/search", response_model=List[PromptListResponse])
def search(
    q: str = None,
    type: str = None,
    category_id: str = None,
    tag_ids: str = None,
    model_id: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    prompts = prompt_service.search_prompts(
        db, q, type, category_id, tag_ids, model_id, page, page_size
    )
    return prompts


# Template routes
@router.get("/templates", response_model=List[TemplateResponse])
def list_templates(type: str = None, db: Session = Depends(get_db)):
    return template_service.list_templates(db, type)


@router.get("/templates/{template_id}", response_model=TemplateResponse)
def get_template(template_id: str, db: Session = Depends(get_db)):
    template = template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/templates", response_model=TemplateResponse)
def create_template(data: TemplateCreate, db: Session = Depends(get_db)):
    return template_service.create_template(db, data)


@router.put("/templates/{template_id}", response_model=TemplateResponse)
def update_template(template_id: str, data: TemplateUpdate, db: Session = Depends(get_db)):
    template = template_service.update_template(db, template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/templates/{template_id}")
def delete_template(template_id: str, db: Session = Depends(get_db)):
    if not template_service.delete_template(db, template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Deleted successfully"}


@router.post("/templates/{template_id}/instantiate")
def instantiate_template(template_id: str, data: InstantiateRequest, db: Session = Depends(get_db)):
    try:
        result = template_service.instantiate(db, template_id, data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/templates/{template_id}/validate")
def validate_template(template_id: str, db: Session = Depends(get_db)):
    try:
        result = template_service.validate(db, template_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Workflow routes
@router.get("/workflows", response_model=List[WorkflowResponse])
def list_workflows(status: str = None, db: Session = Depends(get_db)):
    return workflow_service.list_workflows(db, status)


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    workflow = workflow_service.get_workflow(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.post("/workflows", response_model=WorkflowResponse)
def create_workflow(data: WorkflowCreate, db: Session = Depends(get_db)):
    return workflow_service.create_workflow(db, data)


@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: str, data: WorkflowUpdate, db: Session = Depends(get_db)):
    workflow = workflow_service.update_workflow(db, workflow_id, data)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.delete("/workflows/{workflow_id}")
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    if not workflow_service.delete_workflow(db, workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Deleted successfully"}


@router.post("/workflows/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
def execute_workflow(workflow_id: str, data: ExecuteWorkflowRequest = None, db: Session = Depends(get_db)):
    try:
        inputs = data.inputs if data else None
        return workflow_service.execute(db, workflow_id, inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
def get_workflow_executions(workflow_id: str, limit: int = 20, db: Session = Depends(get_db)):
    return workflow_service.get_executions(db, workflow_id, limit)


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
def get_execution(execution_id: str, db: Session = Depends(get_db)):
    execution = workflow_service.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.post("/executions/{execution_id}/cancel")
def cancel_execution(execution_id: str, db: Session = Depends(get_db)):
    if not workflow_service.cancel_execution(db, execution_id):
        raise HTTPException(status_code=400, detail="Cannot cancel execution")
    return {"message": "Execution cancelled"}


# Import/Export routes
@router.get("/export")
def export_prompts(
    format: str = "json",
    prompt_ids: str = None,
    category_id: str = None,
    tag_ids: str = None,
    include_templates: bool = False,
    db: Session = Depends(get_db)
):
    prompt_id_list = prompt_ids.split(",") if prompt_ids else None
    tag_id_list = tag_ids.split(",") if tag_ids else None
    
    if format == "json":
        data = import_export_service.export_json(db, prompt_id_list, category_id, tag_id_list, include_templates)
        return PlainTextResponse(content=data, media_type="application/json", 
                                 headers={"Content-Disposition": "attachment; filename=prompts.json"})
    elif format == "csv":
        data = import_export_service.export_csv(db, prompt_id_list, category_id, tag_id_list)
        return PlainTextResponse(content=data, media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=prompts.csv"})
    elif format == "markdown":
        data = import_export_service.export_markdown(db, prompt_id_list, category_id, tag_id_list)
        return PlainTextResponse(content=data, media_type="text/markdown",
                                 headers={"Content-Disposition": "attachment; filename=prompts.md"})
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use json, csv, or markdown.")


@router.post("/import")
def import_prompts(data: ImportData, db: Session = Depends(get_db)):
    data_dict = data.model_dump()
    stats = import_export_service.import_json(db, data_dict)
    return {"message": "Import successful", "stats": stats}