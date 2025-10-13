---
chunk: 2
total_chunks: 7
title: backend/app/services/supabase/database.py (Enhanced)
context: backend/app/services/supabase/database.py (Enhanced)
estimated_tokens: 3694
source: technical-integration-guide.md
---

<!-- Context: backend/app/services/resume_matching/document_processing_service.py > 2. Embedding Service -->

#### 2. Embedding Service

```python

<!-- Context: backend/app/services/resume_matching/embedding_service.py -->

# backend/app/services/resume_matching/embedding_service.py

from typing import List, Dict, Any
import openai
import asyncio
import hashlib
import json
from app.core.config import settings
from app.services.vectordb.qdrant_service import QdrantService

class EmbeddingService:
    """Service for generating and managing text embeddings"""

    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.qdrant_service = QdrantService()
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for given text using OpenAI API

        Args:
            text: Text to generate embedding for

        Returns:
            List of float values representing the embedding

        Raises:
            Exception: If embedding generation fails
        """
        try:
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")

    async def generate_document_embeddings(self, document: ProcessedDocument) -> Dict[str, List[float]]:
        """
        Generate embeddings for different parts of a document

        Args:
            document: ProcessedDocument instance

        Returns:
            Dictionary with embeddings for different document parts
        """
        embeddings = {}

        # Full text embedding
        embeddings['full_text'] = await self.generate_embedding(document.text_content)

        # Section embeddings
        for section_name, section_text in document.sections.items():
            if section_text and len(section_text.strip()) > 50:
                embeddings[f'section_{section_name}'] = await self.generate_embedding(section_text)

        # Summary embedding (first 200 characters)
        summary = document.text_content[:200]
        embeddings['summary'] = await self.generate_embedding(summary)

        return embeddings

    async def store_embeddings(self, document_id: str, embeddings: Dict[str, List[float]],
                             metadata: Dict[str, Any]) -> bool:
        """
        Store embeddings in vector database

        Args:
            document_id: Unique document identifier
            embeddings: Dictionary of embeddings to store
            metadata: Additional metadata for the embeddings

        Returns:
            True if storage successful, False otherwise
        """
        try:
            for embedding_type, embedding_vector in embeddings.items():
                point_id = f"{document_id}_{embedding_type}"

                await self.qdrant_service.store_vector(
                    point_id=point_id,
                    vector=embedding_vector,
                    metadata={
                        **metadata,
                        'embedding_type': embedding_type,
                        'document_id': document_id
                    }
                )
            return True
        except Exception as e:
            print(f"Error storing embeddings: {str(e)}")
            return False

    async def find_similar_documents(self, query_embedding: List[float],
                                   limit: int = 10,
                                   filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Find similar documents based on embedding similarity

        Args:
            query_embedding: Embedding to search for
            limit: Maximum number of results to return
            filters: Optional filters for search

        Returns:
            List of similar documents with similarity scores
        """
        try:
            results = await self.qdrant_service.search_similar(
                query_vector=query_embedding,
                limit=limit,
                filters=filters
            )
            return results
        except Exception as e:
            raise Exception(f"Similarity search failed: {str(e)}")

    async def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score between 0 and 1
        """
        try:
            import numpy as np

            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            raise Exception(f"Similarity calculation failed: {str(e)}")
```

<!-- Context: backend/app/services/resume_matching/embedding_service.py > 3. Similarity Service -->

#### 3. Similarity Service

```python

<!-- Context: backend/app/services/resume_matching/similarity_service.py -->

# backend/app/services/resume_matching/similarity_service.py

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np
from app.services.resume_matching.embedding_service import EmbeddingService

@dataclass
class SimilarityResult:
    overall_similarity: float
    section_similarities: Dict[str, float]
    keyword_similarity: float
    confidence_score: float

class SimilarityService:
    """Service for calculating document similarities"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.weight_config = {
            'full_text': 0.4,
            'skills': 0.3,
            'experience': 0.2,
            'education': 0.1
        }

    async def calculate_document_similarity(self, resume_embeddings: Dict[str, List[float]],
                                          job_embeddings: Dict[str, List[float]]) -> SimilarityResult:
        """
        Calculate comprehensive similarity between resume and job description

        Args:
            resume_embeddings: Resume document embeddings
            job_embeddings: Job description embeddings

        Returns:
            SimilarityResult with detailed similarity scores
        """
        section_similarities = {}
        overall_similarity = 0.0
        total_weight = 0.0

        # Calculate similarities for each section type
        for section in self.weight_config.keys():
            resume_key = f"section_{section}" if section != 'full_text' else 'full_text'
            job_key = f"section_{section}" if section != 'full_text' else 'full_text'

            if resume_key in resume_embeddings and job_key in job_embeddings:
                similarity = await self.embedding_service.calculate_similarity(
                    resume_embeddings[resume_key],
                    job_embeddings[job_key]
                )
                section_similarities[section] = similarity
                overall_similarity += similarity * self.weight_config[section]
                total_weight += self.weight_config[section]

        # Normalize overall similarity
        if total_weight > 0:
            overall_similarity /= total_weight

        # Calculate keyword similarity
        keyword_similarity = await self._calculate_keyword_similarity(
            resume_embeddings, job_embeddings
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            section_similarities, len(resume_embeddings), len(job_embeddings)
        )

        return SimilarityResult(
            overall_similarity=overall_similarity,
            section_similarities=section_similarities,
            keyword_similarity=keyword_similarity,
            confidence_score=confidence_score
        )

    async def _calculate_keyword_similarity(self, resume_embeddings: Dict[str, List[float]],
                                          job_embeddings: Dict[str, List[float]]) -> float:
        """Calculate keyword-based similarity"""
        # Extract keywords from summary embeddings as a proxy
        if 'summary' in resume_embeddings and 'summary' in job_embeddings:
            return await self.embedding_service.calculate_similarity(
                resume_embeddings['summary'],
                job_embeddings['summary']
            )
        return 0.0

    def _calculate_confidence_score(self, section_similarities: Dict[str, float],
                                  resume_sections: int, job_sections: int) -> float:
        """Calculate confidence score based on available data"""
        base_confidence = 0.5

        # Increase confidence based on number of matching sections
        section_count = len(section_similarities)
        section_confidence = min(section_count / 4.0, 0.3)  # Max 0.3 for sections

        # Adjust based on similarity distribution
        if section_similarities:
            similarities = list(section_similarities.values())
            variance = np.var(similarities)
            variance_penalty = min(variance * 0.5, 0.2)  # Max 0.2 penalty
        else:
            variance_penalty = 0.2

        confidence = base_confidence + section_confidence - variance_penalty
        return max(0.1, min(1.0, confidence))

    async def find_best_matches(self, resume_embeddings: Dict[str, List[float]],
                              job_embeddings_list: List[Dict[str, List[float]]],
                              limit: int = 5) -> List[Tuple[int, SimilarityResult]]:
        """
        Find best matching job descriptions for a resume

        Args:
            resume_embeddings: Resume document embeddings
            job_embeddings_list: List of job description embeddings
            limit: Maximum number of matches to return

        Returns:
            List of tuples (job_index, similarity_result) sorted by similarity
        """
        similarities = []

        for idx, job_embeddings in enumerate(job_embeddings_list):
            similarity = await self.calculate_document_similarity(
                resume_embeddings, job_embeddings
            )
            similarities.append((idx, similarity))

        # Sort by overall similarity (descending)
        similarities.sort(key=lambda x: x[1].overall_similarity, reverse=True)

        return similarities[:limit]
```

---

<!-- Context: backend/app/services/resume_matching/similarity_service.py > Code Adaptation Guidelines -->

## Code Adaptation Guidelines

<!-- Context: backend/app/services/resume_matching/similarity_service.py > Code Adaptation Guidelines > Integration with Existing Services -->

### Integration with Existing Services

<!-- Context: backend/app/services/resume_matching/similarity_service.py > Code Adaptation Guidelines > Integration with Existing Services > 1. Supabase Service Extension -->

#### 1. Supabase Service Extension

```python

<!-- Context: backend/app/services/supabase/database.py (Enhanced) -->

# backend/app/services/supabase/database.py (Enhanced)

from typing import TypeVar, Generic, Dict, Any, List, Optional
from pydantic import BaseModel
from supabase import Client, create_client
from app.core.config import settings

T = TypeVar('T', bound=BaseModel)

class SupabaseDatabaseService(Generic[T]):
    """Enhanced database service with resume matching capabilities"""

    def __init__(self, table_name: str, model_class: Type[T]):
        self.table_name = table_name
        self.model_class = model_class
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )

    async def create(self, data: Dict[str, Any]) -> T:
        """Create new record with user association"""
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                return self.model_class(**response.data[0])
            raise Exception("No data returned from insert operation")
        except Exception as e:
            raise Exception(f"Create operation failed: {str(e)}")

    async def get_by_user(self, user_id: str, filters: Dict[str, Any] = None) -> List[T]:
        """Get records for specific user with optional filters"""
        try:
            query = self.client.table(self.table_name).select("*").eq("user_id", user_id)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            response = query.execute()
            return [self.model_class(**item) for item in response.data]
        except Exception as e:
            raise Exception(f"Get by user operation failed: {str(e)}")

    async def update(self, id: str, data: Dict[str, Any]) -> T:
        """Update existing record"""
        try:
            response = self.client.table(self.table_name).update(data).eq("id", id).execute()
            if response.data:
                return self.model_class(**response.data[0])
            raise Exception("No data returned from update operation")
        except Exception as e:
            raise Exception(f"Update operation failed: {str(e)}")

    async def delete(self, id: str) -> bool:
        """Delete record by ID"""
        try:
            response = self.client.table(self.table_name).delete().eq("id", id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Delete operation failed: {str(e)}")

    async def search(self, query: str, search_fields: List[str], user_id: str) -> List[T]:
        """Full-text search across specified fields"""
        try:
            # Build search query
            search_conditions = []
            for field in search_fields:
                search_conditions.append(f"{field}.ilike.%{query}%")

            # Combine search conditions with OR
            search_query = " , ".join(search_conditions)

            response = self.client.table(self.table_name).select("*") \
                .eq("user_id", user_id) \
                .or_(search_query) \
                .execute()

            return [self.model_class(**item) for item in response.data]
        except Exception as e:
            raise Exception(f"Search operation failed: {str(e)}")
```
