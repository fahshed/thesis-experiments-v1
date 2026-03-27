import time
from typing import Dict, Any, List, Optional
import numpy as np
from src.strategies.base import BaseStrategy

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class Strategy3RAG(BaseStrategy):
    """
    Strategy 3: RAG System (Semantic Search)
    Uses a small, fast local embedding model to semantically retrieve
    the most relevant chunks of the CV before prompting the LLM.
    """
    def __init__(self, llm, chunk_size=500, top_k=1, model_name='all-MiniLM-L6-v2'):
        super().__init__(llm)
        self.chunk_size = chunk_size
        self.top_k = top_k
        self.model_name = model_name
        self._cv_cache: Dict[str, Dict[str, Any]] = {}
        
        if SentenceTransformer is None:
            raise ImportError("Please install sentence-transformers: pip install sentence-transformers")
            
        print(f"=== Loading embedding model '{model_name}'...")
        self.embedding_model = SentenceTransformer(model_name)

    @property
    def strategy_name(self) -> str:
        return "S3_RAG"

    def _chunk_text(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size):
            chunks.append(" ".join(words[i:i + self.chunk_size]))
        return chunks

    def _cosine_similarity(self, a, b):
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return np.dot(a, b) / denom

    def _build_retrieval_query(self, question: str, question_category: Optional[str] = None) -> str:
        if question_category:
            return f"Category: {question_category}\nQuestion: {question}"
        return question

    def _prepare_cv_cache(self, cv_id: str, cv_text: str) -> Dict[str, Any]:
        cached = self._cv_cache.get(cv_id)
        if cached is not None:
            return cached

        prep_start_time = time.time()

        chunking_start_time = time.time()
        chunks = self._chunk_text(cv_text)
        chunking_latency = time.time() - chunking_start_time

        embedding_start_time = time.time()
        chunk_embeddings = np.asarray(self.embedding_model.encode(chunks)) if chunks else np.asarray([])
        chunk_embedding_latency = time.time() - embedding_start_time
        prep_total_latency = time.time() - prep_start_time

        cached = {
            "chunks": chunks,
            "chunk_embeddings": chunk_embeddings,
            "num_chunks": len(chunks),
            "retrieval_context_type": f"Top {self.top_k} semantically matched chunks",
        }
        self._cv_cache[cv_id] = cached

        print(
            f"=== -> [{self.strategy_name}] Prepared cache for CV ID: {cv_id} | "
            f"num_chunks={len(chunks)} | "
            f"chunking_latency={chunking_latency:.6f}s | "
            f"chunk_embedding_latency={chunk_embedding_latency:.6f}s | "
            f"prep_total_latency={prep_total_latency:.6f}s"
        )
        return cached

    def _retrieve_chunks(self, cache_entry: Dict[str, Any], retrieval_query: str) -> List[str]:
        chunks = cache_entry["chunks"]
        chunk_embeddings = cache_entry["chunk_embeddings"]
        if not chunks:
            return []

        # Encode the retrieval query into a semantic vector.
        q_emb = np.asarray(self.embedding_model.encode([retrieval_query])[0])

        # Calculate semantic cosine similarity against cached chunk embeddings.
        scored_chunks = []
        for i, c_emb in enumerate(chunk_embeddings):
            score = self._cosine_similarity(q_emb, c_emb)
            scored_chunks.append((score, chunks[i], i))
            
        # Sort by highest semantic score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Select the top_k chunks
        top_chunks = [(c_text, c_idx) for score, c_text, c_idx in scored_chunks[:self.top_k]]
        return top_chunks

    def _build_prompt(self, relevant_text: str, question: str) -> str:
        return f"""You are an expert HR assistant. Your task is to extract information based on a relevant section retrieved from a CV.
        
RELEVANT CV SECTION:
{relevant_text}

QUESTION:
{question}

Please answer the question accurately using ONLY the information from the relevant section above. If the answer is not in the text, say 'Not found'.
Respond ONLY in valid JSON format with the following keys:
- "predicted_answer": A concise and factual answer to the question.
- "rationale": A brief explanation of why this answer is correct based on the section.
- "confidence_score": A float between 0.0 and 1.0 representing your confidence.

JSON Response:
"""

    def run(self, cv_text: str, question: str, **kwargs) -> Dict[str, Any]:
        print(f"=== -> [{self.strategy_name}] Q: {question[:80]}...")
        cv_id = kwargs.get("cv_id")
        question_category = kwargs.get("question_category")
        if not cv_id:
            raise ValueError("S3_RAG requires cv_id to prepare and reuse per-CV retrieval cache.")
        cache_entry = self._prepare_cv_cache(cv_id, cv_text)

        lookup_start_time = time.time()
        retrieval_query = self._build_retrieval_query(question, question_category)
        top_chunk_data = self._retrieve_chunks(cache_entry, retrieval_query)
        
        # Separate text and indices
        best_chunks = [c_text for c_text, c_idx in top_chunk_data]
        best_indices = [c_idx for c_text, c_idx in top_chunk_data]
        
        relevant_context = "\n...\n".join(best_chunks)
        
        prompt = self._build_prompt(relevant_context, question)
        lookup_latency = time.time() - lookup_start_time
        
        try:
            llm_generation_start_time = time.time()
            llm_output = self.llm.generate(prompt)
            llm_generation_latency = time.time() - llm_generation_start_time
            raw_response = llm_output.get("text", "")
            input_tokens = llm_output.get("input_tokens", 0)
            output_tokens = llm_output.get("output_tokens", 0)
            estimated_cost = llm_output.get("estimated_cost", 0.0)
        except Exception as e:
            llm_generation_latency = time.time() - llm_generation_start_time
            print(f"=== -> [ERROR] LLM Generation failed: {e}")
            raw_response = f"ERROR: {str(e)}"
            input_tokens = 0
            output_tokens = 0
            estimated_cost = 0.0
            
        latency = lookup_latency + llm_generation_latency
        
        return {
            "raw_response": raw_response,
            "latency": latency,
            "lookup_latency": lookup_latency,
            "llm_generation_latency": llm_generation_latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": estimated_cost,
            "context_used": cache_entry["retrieval_context_type"],
            # E3 specific data:
            "retrieved_chunk_ids": best_indices,
            "retrieved_text": relevant_context,
            "num_chunks_used": len(best_chunks)
        }
