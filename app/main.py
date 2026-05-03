from fastapi import FastAPI, HTTPException

from app.runtime.engine import RuntimeEngine
from app.runtime.logging_config import get_logger
from app.runtime.workflow_loader import WorkflowLoader
from app.schemas import RunWorkflowRequest, RunWorkflowResponse

app = FastAPI(title="MVP Workflow Runtime")
logger = get_logger(__name__)
workflow_loader = WorkflowLoader()
runtime_engine = RuntimeEngine()


@app.post("/run-workflow", response_model=RunWorkflowResponse)
def run_workflow(payload: RunWorkflowRequest) -> RunWorkflowResponse:
    """Load a workflow JSON definition and execute it with the runtime engine."""
    try:
        workflow = workflow_loader.load(payload.workflow_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    logger.info("Running workflow", extra={"workflow_name": workflow.name})
    result = runtime_engine.run(workflow, payload.input)
    return RunWorkflowResponse(**result)
