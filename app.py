import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class RunWorkflowRequest(BaseModel):
    task: str


class AgentResult(BaseModel):
    agent: str
    output: Dict[str, Any]


class WorkflowResponse(BaseModel):
    workflow_loaded: bool
    execution_order: list[str]
    context: Dict[str, Any]
    steps: list[AgentResult]


app = FastAPI()


WORKFLOW_FILE = Path(__file__).with_name("workflow.json")


def load_workflow() -> Dict[str, Any]:
    if not WORKFLOW_FILE.exists():
        raise FileNotFoundError(f"Missing workflow file: {WORKFLOW_FILE}")
    with WORKFLOW_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_planner(context: Dict[str, Any]) -> Dict[str, Any]:
    plan = f"Plan for task: {context['task']}"
    context["plan"] = plan
    return {"plan": plan}


def run_writer(context: Dict[str, Any]) -> Dict[str, Any]:
    draft = f"Draft based on {context['plan']}"
    context["draft"] = draft
    return {"draft": draft}


def run_validator(context: Dict[str, Any]) -> Dict[str, Any]:
    is_valid = bool(context.get("draft"))
    report = "valid" if is_valid else "invalid"
    context["validation"] = report
    return {"status": report}


AGENT_RUNNERS = {
    "planner": run_planner,
    "writer": run_writer,
    "validator": run_validator,
}


@app.post("/run-workflow", response_model=WorkflowResponse)
def run_workflow(request: RunWorkflowRequest) -> WorkflowResponse:
    try:
        workflow = load_workflow()
    except Exception as exc:  # runtime validation path
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    agents = workflow.get("agents", [])
    context: Dict[str, Any] = {"task": request.task}
    steps: list[AgentResult] = []
    execution_order: list[str] = []

    for agent in agents:
        name = agent.get("name")
        if name not in AGENT_RUNNERS:
            raise HTTPException(status_code=500, detail=f"Unknown agent: {name}")
        output = AGENT_RUNNERS[name](context)
        steps.append(AgentResult(agent=name, output=output))
        execution_order.append(name)

    return WorkflowResponse(
        workflow_loaded=True,
        execution_order=execution_order,
        context=context,
        steps=steps,
    )
