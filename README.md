# mvp1

Minimal AI workflow orchestration runtime MVP.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoint

`POST /run-workflow`

Example request body:

```json
{
  "workflow_path": "workflows/sample_workflow.json",
  "input": {
    "objective": "Write launch copy",
    "audience": "technical buyers"
  }
}
```
