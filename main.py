from fastapi import FastAPI

app = FastAPI()


@app.get(path="/status")
async def get_status() -> dict[str, str]:
    return {"status": "The semantic insight engine is ready to work."}
