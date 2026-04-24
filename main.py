from typing import Any


from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.ml_engine import MLEngine
from app.database import engine, get_db
from app import models, schemas
import fitz

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
    Processes and stores a document by splitting it into semantic chunks.

    This endpoint supports both .txt and .pdf files. It extracts the text,
    divides it into chunks of 500 characters, generates vector embeddings
    for each chunk using the ML engine, and persists everything in the database.

    Args:
        file (UploadFile): The document to be processed (PDF or UTF-8 text).
        db (Session): Database session dependency.

    Returns:
        dict[str, Any]: A summary containing the assigned document ID,
        the total number of generated chunks, and the filename.

    Raises:
        HTTPException: 400 error if the file is empty, has an invalid
        encoding, or if text extraction fails.
    """

    content = await file.read()

    try:
        if file.filename.endswith(  # pyright: ignore[reportOptionalMemberAccess]
            ".pdf"
        ):
            doc = fitz.open(stream=content, filetype="pdf")
            text = "\n".join(
                [
                    page.get_text() for page in doc
                ]  # pyright: ignore[reportCallIssue, reportArgumentType]
            )
        else:
            text = content.decode(encoding="utf-8")
        if not text.strip():
            raise HTTPException(
                status_code=400, detail="Could not get the text."
            )
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Text (.txt) only.")

    # Create and save the document.
    db_document = models.Document(filename=file.filename)
    db.add(instance=db_document)
    db.commit()
    db.refresh(instance=db_document)

    # Divide the document into chunks.
    chunks = ml.get_chunks(text, chunk_size=1000, overlap=150)

    # Process the chunks.
    for chunk_text in chunks:
        vector = ml.create_embedding(text=chunk_text)

        # Save it to the chunk table.
        # The vector is handled as a JSON string.
        db_chunk = models.DocumentChunk(
            document_id=db_document.id,
            content=chunk_text,
            embedding=vector,
        )
        db.add(instance=db_chunk)

    # Save all the chunks.
    db.commit()

    return {
        "message": "The document's been processed.",
        "document_id": db_document.id,
        "chunks_count": len(chunks),
        "filename": file.filename,
    }


@app.get(path="/documents", response_model=list[schemas.DocumentRead])
async def get_documents(
    db: Session = Depends(dependency=get_db),
) -> list[models.Document]:
    """
    Retrieves a list of all uploaded documents from the database.

    This endpoint fetches document metadata (such as IDs and filenames)
    without their individual text chunks or embeddings.

    Args:
        db (Session): The database session dependency.

    Returns:
        list[models.Document]: A list of document records formatted
        according to the DocumentRead schema.
    """

    docs = db.query(models.Document).all()
    return docs


@app.get(path="/search")
async def search(
    query: str, db: Session = Depends(dependency=get_db)
) -> list[dict[str, Any]]:
    """
    Performs a semantic search to find relevant document chunks.

    This endpoint converts the input query into a vector embedding using the ML engine
    and calculates the cosine distance against stored chunks in the database.
    It returns the top 10 most similar segments.

    Args:
        query (str): The search phrase or question.
        db (Session): The database session dependency.

    Returns:
        list[dict[str, Any]]: A list of results, each containing the chunk's content,
        source document information, and a similarity score (1 - cosine_distance).
    """

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
            "document_filename": r.DocumentChunk.document.filename,
            "similarity": round(number=1 - r.distance, ndigits=4),
        }
        for r in results
    ]


models.Base.metadata.create_all(bind=engine)
