import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.domain.entities.models import Workflow, WorkflowExecution, ExecutionStatus, Template, Prompt
from app.domain.services.template_service import TemplateService


class WorkflowEngine:
    STEP_REFERENCE_PATTERN = re.compile(r'\{\{(step_\w+)\.(\w+)\}\}')
    WORKFLOW_INPUT_PATTERN = re.compile(r'\{\{workflow\.(\w+)\}\}')

    def __init__(self):
        self.template_service = TemplateService()

    def execute(self, db: Session, workflow: Workflow, inputs: Dict[str, Any] = None) -> WorkflowExecution:
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            status=ExecutionStatus.RUNNING,
            inputs=inputs or {},
            step_executions=[],
            started_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()

        context = {"workflow": inputs or {}}
        step_executions = []
        steps = sorted(workflow.steps, key=lambda s: s.get("order", 0))

        try:
            for step in steps:
                step_execution = self._execute_step(db, step, context)
                step_executions.append(step_execution)
                
                if step_execution["status"] == ExecutionStatus.FAILED:
                    if step.get("on_failure") == "stop":
                        execution.status = ExecutionStatus.FAILED
                        execution.error = f"Step {step['id']} failed: {step_execution.get('error')}"
                        break
                else:
                    for output_name in step.get("outputs", []):
                        context[f"{step['id']}.{output_name}"] = step_execution["outputs"].get(output_name)

            if execution.status == ExecutionStatus.RUNNING:
                execution.status = ExecutionStatus.COMPLETED

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)

        execution.step_executions = step_executions
        execution.completed_at = datetime.utcnow()
        execution.outputs = {k: v for k, v in context.items() if "." not in k}
        db.commit()
        db.refresh(execution)
        
        return execution

    def _execute_step(self, db: Session, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        step_execution = {
            "step_id": step["id"],
            "status": ExecutionStatus.RUNNING,
            "started_at": datetime.utcnow().isoformat(),
            "inputs": {},
            "outputs": {},
            "error": None
        }

        try:
            step_inputs = self._resolve_inputs(step.get("inputs", {}), context)
            step_execution["inputs"] = step_inputs

            if step["type"] == "template":
                template = db.query(Template).filter(Template.id == step["template_id"]).first()
                if not template:
                    raise ValueError(f"Template {step['template_id']} not found")
                
                variables = [v.dict() if hasattr(v, 'dict') else v for v in template.variables]
                content = self.template_service.instantiate(
                    template.content, 
                    [type('VariableDefinition', (), v) for v in variables],
                    step_inputs
                )
                step_execution["outputs"] = {"content": content}

            elif step["type"] == "prompt":
                prompt = db.query(Prompt).filter(Prompt.id == step["prompt_id"]).first()
                if not prompt:
                    raise ValueError(f"Prompt {step['prompt_id']} not found")
                step_execution["outputs"] = {"content": prompt.content}

            step_execution["status"] = ExecutionStatus.COMPLETED

        except Exception as e:
            step_execution["status"] = ExecutionStatus.FAILED
            step_execution["error"] = str(e)

        step_execution["completed_at"] = datetime.utcnow().isoformat()
        return step_execution

    def _resolve_inputs(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        resolved = {}
        
        for key, value in inputs.items():
            if isinstance(value, str):
                step_match = self.STEP_REFERENCE_PATTERN.match(value)
                if step_match:
                    step_id, output_name = step_match.groups()
                    resolved[key] = context.get(f"{step_id}.{output_name}")
                    continue
                
                workflow_match = self.WORKFLOW_INPUT_PATTERN.match(value)
                if workflow_match:
                    input_name = workflow_match.group(1)
                    resolved[key] = context.get("workflow", {}).get(input_name)
                    continue
            
            resolved[key] = value
        
        return resolved

    def validate_workflow(self, workflow: Workflow, db: Session) -> Dict[str, Any]:
        errors = []
        steps = workflow.steps
        
        step_ids = [s["id"] for s in steps]
        if len(step_ids) != len(set(step_ids)):
            errors.append("Duplicate step IDs found")

        orders = [s.get("order", 0) for s in steps]
        if sorted(orders) != list(range(1, len(orders) + 1)):
            errors.append("Step orders must be consecutive starting from 1")

        for step in steps:
            if step["type"] == "template":
                template = db.query(Template).filter(Template.id == step.get("template_id")).first()
                if not template:
                    errors.append(f"Step {step['id']}: Template not found")
            elif step["type"] == "prompt":
                prompt = db.query(Prompt).filter(Prompt.id == step.get("prompt_id")).first()
                if not prompt:
                    errors.append(f"Step {step['id']}: Prompt not found")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }