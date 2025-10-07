from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Document to be stored in the vector database."""

    text: str
    title: str | None = None
    metadata: dict[str, Any] | None = Field(default_factory=dict)


class DocumentInput(BaseModel):
    """Input for adding documents to the vector database."""

    documents: list[Document]
    embedding_model: str = "text-embedding-ada-002"


class DocumentUploadResponse(BaseModel):
    """Response from adding documents to the vector database."""

    document_ids: list[str]


class SearchQuery(BaseModel):
    """Query for searching the vector database."""

    query_text: str
    embedding_model: str = "text-embedding-ada-002"
    limit: int = Field(default=10, gt=0, le=100)
    filter_metadata: dict[str, Any] | None = None


class SearchResult(BaseModel):
    """Search result from the vector database."""

    id: str
    score: float
    document: dict[str, Any]
    metadata: dict[str, Any]


class DeleteDocumentsRequest(BaseModel):
    """Request for deleting documents from the vector database."""

    document_ids: list[str]
