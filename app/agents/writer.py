class WriterAgent:
    def run(self, plan: str, context: dict) -> str:
        audience = context.get("audience", "general")
        return f"Draft for {audience} audience based on {plan}"
