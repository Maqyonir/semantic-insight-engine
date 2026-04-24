from pydantic import BaseModel
from datetime import datetime


class ChunkRead(BaseModel):
    """
    Pydantic schema for representing a document chunk in API responses.

    This schema provides a simplified view of a DocumentChunk, focusing on
    the text content and excluding the raw vector data for efficiency.

    Attributes:
        id (int): The unique identifier of the chunk.
        content (str): The text fragment stored in this chunk.
    """

    id: int
    content: str

    class Config:
        from_attributes = (
            True  # Lets Pydantic read data from SQLAlchemy models.
        )


class DocumentRead(BaseModel):
    """
    Pydantic schema for representing a document and its associated chunks.

    This schema is used to return comprehensive document information, 
    including a list of all its processed text segments.

    Attributes:
        id (int): The unique identifier of the document.
        filename (str): The name of the original uploaded file.
        created_at (datetime): The timestamp when the document was created.
        chunks (list[ChunkRead]): A list of related text chunks.
    """
    
    id: int
    filename: str
    created_at: datetime
    chunks: list[ChunkRead] = []

    class Config:
        from_attributes = True
