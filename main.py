from fastapi import FastAPI, UploadFile, File
from app.ml_engine import MLEngine
from app.database import engine, Base
from app import models

app = FastAPI()
ml = MLEngine()


@app.get(path="/status")
async def get_status() -> dict[str, str]:
    """
    Checks the operational status of the engine.

    Returns:
        dict[str, str]: A dictionary containing the servcie availability message.
    """
    return {"status": "The semantic insight engine is ready to work."}


@app.post(path="/upload")
async def upload_document(
    file: UploadFile = File(default=...),
) -> dict[str, str | list[float] | int | None]:
    """
    Uploads a text document to generate its vector embedding.

    This endpoint reads the uploaded file, decodes it as UTF-8,
    and processes the text through the ML engine to create a semantic vector.

    Args:
        file (UploadFile): The text file to be processed.

    Returns:
        dict[str, Any]: A summary containing the filename, a preview of the
        embedding (first 5 elements), and the total vector dimension.
    """
    content = await file.read()
    text = content.decode(encoding="utf-8")

    vector = ml.create_embedding(text)

    return {
        "filename": file.filename,
        "vector_preview": vector[:5],
        "vector_size": len(vector),
    }


models.Base.metadata.create_all(bind=engine)
