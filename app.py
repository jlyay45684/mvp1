import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).parent
WORKFLOW_PATH = BASE_DIR / "workflow.json"


def planner(context):
    context["plan"] = f"Plan for: {context['input']}"
    context.setdefault("execution_order", []).append("planner")
    return context


def writer(context):
    context["draft"] = f"Draft based on {context['plan']}"
    context.setdefault("execution_order", []).append("writer")
    return context


def validator(context):
    context["is_valid"] = bool(context.get("draft"))
    context.setdefault("execution_order", []).append("validator")
    return context


AGENTS = {
    "planner": planner,
    "writer": writer,
    "validator": validator,
}


def load_workflow():
    with WORKFLOW_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_workflow(user_input):
    workflow = load_workflow()
    context = {"input": user_input}

    for step in workflow["steps"]:
        agent_name = step["agent"]
        if agent_name not in AGENTS:
            raise ValueError(f"Unknown agent: {agent_name}")
        context = AGENTS[agent_name](context)

    return {
        "workflow_loaded": True,
        "execution_order": context["execution_order"],
        "context": context,
    }


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/run-workflow":
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(content_length) if content_length else b"{}"

        try:
            body = json.loads(payload)
            user_input = body.get("input", "test")
            result = run_workflow(user_input)

            data = json.dumps(result).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:  # surface execution issues
            data = json.dumps({"error": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)


def main():
    server = HTTPServer(("127.0.0.1", 8000), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
