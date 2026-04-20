from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, UTC


Base = declarative_base()  # pyright: ignore[reportAny]


class Document(Base):  # pyright: ignore[reportAny]
    __tablename__ = "documents"  # pyright: ignore[reportUnannotatedClassAttribute]

    id = Column(type=Integer, primary_key=True, index=True)  # pyright: ignore[reportUnknownVariableType, reportUnannotatedClassAttribute]
    filename = Column(type=String)  # pyright: ignore[reportUnknownVariableType, reportUnannotatedClassAttribute]
    created_at = Column(type=DateTime, default=datetime.now(tz=UTC))  # pyright: ignore[reportUnknownVariableType, reportUnannotatedClassAttribute]

    # One-to-many: Document - DocuemntChunk
    chunks = relationship(argument="DocumentChunk", back_populates="document")  # pyright: ignore[reportUnannotatedClassAttribute]


class DocumentChunk(Base):  # pyright: ignore[reportAny]
    __tabname__ = "document_chunks"  # pyright: ignore[reportUnannotatedClassAttribute]

    id = Column(type=Integer, primary_key=True, index=True)  # pyright: ignore[reportUnknownVariableType, reportUnannotatedClassAttribute]
    document_id = Column(type=Integer, foreign_keys=ForeignKey(column="documents.id"))  # pyright: ignore[reportUnknownVariableType, reportUnannotatedClassAttribute]
    content = Column(type=Text)  # pyright: ignore[reportUnknownVariableType, reportUnannotatedClassAttribute]

    embedding = Column(type=Text)  # pyright: ignore[reportUnknownVariableType, reportUnannotatedClassAttribute]

    document = relationship(argument="Document", back_populates="chunks")  # pyright: ignore[reportUnannotatedClassAttribute]
