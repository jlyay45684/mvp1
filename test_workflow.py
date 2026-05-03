import json
import subprocess
import time
import urllib.request


server = subprocess.Popen(["python", "app.py"])
try:
    time.sleep(0.5)
    req = urllib.request.Request(
        "http://127.0.0.1:8000/run-workflow",
        data=json.dumps({"input": "Write release notes"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        payload = json.loads(response.read().decode("utf-8"))

    assert payload["workflow_loaded"] is True
    assert payload["execution_order"] == ["planner", "writer", "validator"]
    assert payload["context"]["plan"] == "Plan for: Write release notes"
    assert payload["context"]["draft"] == "Draft based on Plan for: Write release notes"
    assert payload["context"]["is_valid"] is True
    print("E2E workflow validation passed")
finally:
    server.terminate()
    server.wait(timeout=5)
