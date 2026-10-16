from fastapi import FastAPI

app = FastAPI(title="mvp1")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}
