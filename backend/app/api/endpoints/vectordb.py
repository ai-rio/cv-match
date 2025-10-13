import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.vectordb_models import (
    DeleteDocumentsRequest,
    DocumentInput,
    DocumentUploadResponse,
    SearchQuery,
    SearchResult,
)
from app.services.llm.embedding_service import EmbeddingService, get_embedding_service
from app.services.security.middleware import validate_and_sanitize_request
from app.services.supabase.auth import SupabaseAuthService, get_auth_service
from app.services.vectordb import QdrantService, get_vector_db_service

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


@router.post("/documents", response_model=DocumentUploadResponse)
async def add_documents(
    request: DocumentInput,
    http_request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_auth_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_db: QdrantService = Depends(get_vector_db_service),
):
    """Add documents to the vector database."""
    try:
        # Validate user authentication
        user = await auth_service.get_user(credentials.credentials)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        user_id = user.get("id")
        logger.info(f"User authenticated: {user.get('email', 'Unknown user')}")

        # Validate and sanitize input
        try:
            sanitized_request_data = await validate_and_sanitize_request(
                request.dict(), credentials=credentials, request=http_request
            )

            # Update request with sanitized data
            sanitized_documents = sanitized_request_data.get("documents", request.documents)

            # Log sanitization warnings if any
            if "documents" in sanitized_request_data:
                for i, doc_result in enumerate(sanitized_request_data["documents"]):
                    if hasattr(doc_result, "warnings") and len(doc_result.warnings) > 0:
                        warnings = doc_result.warnings
                        logger.warning(
                            f"Input sanitization warnings for document {i}, "
                            f"user {user_id}: {warnings}"
                        )

        except HTTPException:
            # Re-raise HTTP exceptions from validation
            raise
        except Exception as sanitization_error:
            logger.error(f"Input sanitization error: {str(sanitization_error)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Input validation failed"
            )

        # Generate embeddings for each document
        all_embeddings = []
        for document in sanitized_documents:
            embedding_response = await embedding_service.create_embedding(
                text=document.text, model=request.embedding_model
            )
            all_embeddings.append(embedding_response.embedding)

        # Prepare documents and metadata for storage
        docs = [{"text": doc.text, "title": doc.title} for doc in sanitized_documents]
        metadata = (
            [doc.metadata for doc in sanitized_documents]
            if all(hasattr(doc, "metadata") for doc in sanitized_documents)
            else None
        )

        # Add documents to vector database
        doc_ids = await vector_db.add_documents(
            documents=docs, embeddings=all_embeddings, metadata=metadata
        )

        return DocumentUploadResponse(document_ids=doc_ids)
    except Exception as e:
        logger.error(f"Failed to add documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to add documents: {str(e)}"
        )


@router.post("/search", response_model=list[SearchResult])
async def search_documents(
    query: SearchQuery,
    http_request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_auth_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_db: QdrantService = Depends(get_vector_db_service),
):
    """Search for documents similar to the query."""
    try:
        # Validate user authentication
        user = await auth_service.get_user(credentials.credentials)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        user_id = user.get("id")
        logger.info(f"User authenticated: {user.get('email', 'Unknown user')}")

        # Validate and sanitize input
        try:
            sanitized_request_data = await validate_and_sanitize_request(
                query.dict(), credentials=credentials, request=http_request
            )

            # Update query with sanitized data
            sanitized_query_text = sanitized_request_data.get("query_text", query.query_text)

            # Log sanitization warnings if any
            if (
                hasattr(sanitized_request_data, "query_text")
                and len(sanitized_request_data["query_text"].warnings) > 0
            ):
                warnings = sanitized_request_data["query_text"].warnings
                logger.warning(f"Input sanitization warnings for user {user_id}: {warnings}")

        except HTTPException:
            # Re-raise HTTP exceptions from validation
            raise
        except Exception as sanitization_error:
            logger.error(f"Input sanitization error: {str(sanitization_error)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Input validation failed"
            )

        # Generate embedding for the query
        embedding_response = await embedding_service.create_embedding(
            text=sanitized_query_text, model=query.embedding_model
        )

        # Search vector database
        results = await vector_db.search(
            query_embedding=embedding_response.embedding,
            limit=query.limit,
            filter_params=query.filter_metadata,
        )

        return results
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Search failed: {str(e)}"
        )


@router.delete("/documents", status_code=status.HTTP_204_NO_CONTENT)
async def delete_documents(
    request: DeleteDocumentsRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_auth_service),
    vector_db: QdrantService = Depends(get_vector_db_service),
):
    """Delete documents from the vector database."""
    try:
        # Validate user authentication
        await auth_service.get_user(credentials.credentials)

        # Delete documents
        success = await vector_db.delete(request.document_ids)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete one or more documents",
            )
    except Exception as e:
        logger.error(f"Document deletion failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Document deletion failed: {str(e)}"
        )
