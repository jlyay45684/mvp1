from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
WORKFLOW_PATH = Path(__file__).with_name("workflow.json")


class WorkflowRequest(BaseModel):
    topic: str
    audience: str = "general"


def load_workflow() -> dict[str, Any]:
    if not WORKFLOW_PATH.exists():
        raise HTTPException(status_code=500, detail="workflow.json not found")
    try:
        with WORKFLOW_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Invalid workflow JSON: {exc}") from exc


def planner(context: dict[str, Any]) -> dict[str, Any]:
    context["plan"] = f"Plan for {context['topic']} (audience: {context['audience']})"
    return context


def writer(context: dict[str, Any]) -> dict[str, Any]:
    context["draft"] = f"Draft based on: {context['plan']}"
    return context


def validator(context: dict[str, Any]) -> dict[str, Any]:
    context["validation"] = {
        "ok": bool(context.get("draft")),
        "checks": ["plan_present", "draft_present"],
    }
    return context


@app.post("/run-workflow")
def run_workflow(req: WorkflowRequest) -> dict[str, Any]:
    workflow = load_workflow()
    steps = workflow.get("steps", [])
    context: dict[str, Any] = {"topic": req.topic, "audience": req.audience}
    execution_order: list[str] = []

    agent_map = {
        "planner": planner,
        "writer": writer,
        "validator": validator,
    }

    for step in steps:
        name = step.get("agent")
        fn = agent_map.get(name)
        if fn is None:
            raise HTTPException(status_code=500, detail=f"Unknown agent: {name}")
        context = fn(context)
        execution_order.append(name)

    return {
        "workflow_loaded": True,
        "execution_order": execution_order,
        "context": context,
    }
