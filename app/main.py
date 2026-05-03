from fastapi import FastAPI

app = FastAPI()


@app.post('/run-workflow')
async def run_workflow() -> dict[str, str]:
    return {'status': 'ok'}
