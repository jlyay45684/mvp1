from pydantic import BaseModel, Field


class RunWorkflowRequest(BaseModel):
    workflow_path: str = Field(..., description="Path to workflow JSON file")
    input: dict = Field(default_factory=dict, description="Input payload for workflow")


class RunWorkflowResponse(BaseModel):
    workflow_name: str
    status: str
    plan: str
    draft: str
    validation: str
    tool_results: dict
    logs: list[str]
