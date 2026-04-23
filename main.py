from typing import Any


from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.ml_engine import MLEngine
from app.database import engine, get_db
from app import models, schemas
import json

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
    db: Session = Depends(dependency=get_db),
) -> dict[str, Any]:
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
    try:
        text = content.decode(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Text (.txt) only.")

    # Create and save the document.
    db_document = models.Document(filename=file.filename)
    db.add(instance=db_document)
    db.commit()
    db.refresh(instance=db_document)

    # Divide the document into chunks (500 characters).
    chunk_size = 500
    text_chunks = [
        text[i : i + chunk_size] for i in range(0, len(text), chunk_size)
    ]

    # Process the chunks.
    for content_piece in text_chunks:
        vector = ml.create_embedding(text=content_piece)

        # Save it to the chunk table.
        # The vector is handled as a JSON string.
        db_chunk = models.DocumentChunk(
            document_id=db_document.id,
            content=content_piece,
            embedding=vector,
        )
        db.add(instance=db_chunk)

    # Save all the chunks.
    db.commit()

    return {
        "message": "The document's been processed.",
        "document_id": db_document.id,
        "chunks_count": len(text_chunks),
        "filename": file.filename,
    }


@app.get(path="/documents", response_model=list[schemas.DocumentRead])
async def get_documents(
    db: Session = Depends(dependency=get_db),
) -> list[models.Document]:
    docs = db.query(models.Document).all()
    return docs


@app.get(path="/search")
async def search(query: str, db: Session = Depends(dependency=get_db)):
    # Translate the query into the vector.
    query_vector = ml.create_embedding(text=query)

    distance_label = models.DocumentChunk.embedding.cosine_distance(
        query_vector
    ).label("distance")

    # Run a database query using cosine similarity.
    # Find chunks in which the distance to the vector is minimal.
    results = (
        db.query(models.DocumentChunk, distance_label)
        .order_by(distance_label)
        .limit(limit=10)
        .all()
    )

    return [
        {
            "content": r.DocumentChunk.content,
            "document_id": r.DocumentChunk.document_id,
            "similarity": round(number=1 - r.distance, ndigits=4),
        }
        for r in results
    ]


models.Base.metadata.create_all(bind=engine)
