from pydantic import BaseModel
from datetime import datetime


class ChunkRead(BaseModel):
    id: int
    content: str

    class Config:
        from_attributes = (
            True  # Lets Pydantic read data from SQLAlchemy models.
        )


class DocumentRead(BaseModel):
    id: int
    filename: str
    created_at: datetime
    chunks: list[ChunkRead] = []

    class Config:
        from_attributes = True
