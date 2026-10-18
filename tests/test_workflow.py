from app import load_workflow, run_planner, run_validator, run_workflow, run_writer
from app import RunWorkflowRequest


def test_workflow_configuration_has_expected_order() -> None:
    workflow = load_workflow()

    assert [agent["name"] for agent in workflow["agents"]] == [
        "planner",
        "writer",
        "validator",
    ]


def test_agent_pipeline_builds_valid_context() -> None:
    context = {"task": "validate AQG"}

    assert run_planner(context) == {"plan": "Plan for task: validate AQG"}
    assert run_writer(context) == {"draft": "Draft based on Plan for task: validate AQG"}
    assert run_validator(context) == {"status": "valid"}
    assert context["validation"] == "valid"


def test_run_workflow_returns_all_steps() -> None:
    response = run_workflow(RunWorkflowRequest(task="ship MVP"))

    assert response.workflow_loaded is True
    assert response.execution_order == ["planner", "writer", "validator"]
    assert [step.agent for step in response.steps] == response.execution_order
    assert response.context["validation"] == "valid"
