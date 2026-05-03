from typing import Callable


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[[dict], dict]] = {}
        self.register("echo", self._echo)

    def register(self, name: str, tool: Callable[[dict], dict]) -> None:
        self._tools[name] = tool

    def run(self, name: str, payload: dict) -> dict:
        if name not in self._tools:
            return {"error": f"Tool '{name}' not registered"}
        return self._tools[name](payload)

    @staticmethod
    def _echo(payload: dict) -> dict:
        return {"echo": payload}
