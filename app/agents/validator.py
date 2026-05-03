class ValidatorAgent:
    def run(self, draft: str) -> str:
        if len(draft) < 20:
            return "Validation failed: draft too short"
        return "Validation passed"
