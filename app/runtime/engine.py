from app.agents.planner import PlannerAgent
from app.agents.validator import ValidatorAgent
from app.agents.writer import WriterAgent
from app.runtime.logging_config import get_logger
from app.runtime.workflow_loader import WorkflowDefinition
from app.tools.registry import ToolRegistry


class RuntimeEngine:
    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.writer = WriterAgent()
        self.validator = ValidatorAgent()
        self.tools = ToolRegistry()
        self.logger = get_logger(__name__)

    def run(self, workflow: WorkflowDefinition, context: dict) -> dict:
        logs: list[str] = []

        self.logger.info("Planner agent started")
        plan = self.planner.run(workflow.prompt, context)
        logs.append("planner_completed")

        tool_results: dict[str, dict] = {}
        for tool_name in workflow.tools:
            self.logger.info("Running tool", extra={"tool": tool_name})
            tool_results[tool_name] = self.tools.run(tool_name, context)
            logs.append(f"tool_completed:{tool_name}")

        self.logger.info("Writer agent started")
        draft = self.writer.run(plan, context)
        logs.append("writer_completed")

        self.logger.info("Validator agent started")
        validation = self.validator.run(draft)
        logs.append("validator_completed")

        status = "success" if validation == "Validation passed" else "failed"
        return {
            "workflow_name": workflow.name,
            "status": status,
            "plan": plan,
            "draft": draft,
            "validation": validation,
            "tool_results": tool_results,
            "logs": logs,
        }
