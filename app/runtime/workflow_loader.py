import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WorkflowDefinition:
    name: str
    tools: list[str]
    prompt: str


class WorkflowLoader:
    def load(self, workflow_path: str) -> WorkflowDefinition:
        path = Path(workflow_path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")

        data = json.loads(path.read_text())
        required_fields = {"name", "tools", "prompt"}
        missing = required_fields.difference(data.keys())
        if missing:
            raise ValueError(f"Workflow missing required fields: {sorted(missing)}")

        if not isinstance(data["tools"], list):
            raise ValueError("Workflow field 'tools' must be a list")

        return WorkflowDefinition(
            name=data["name"],
            tools=data["tools"],
            prompt=data["prompt"],
        )
