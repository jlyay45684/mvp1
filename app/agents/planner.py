class PlannerAgent:
    def run(self, prompt: str, context: dict) -> str:
        objective = context.get("objective", "No explicit objective provided")
        return f"Plan: {prompt}. Objective: {objective}. Steps: analyze, draft, validate."
