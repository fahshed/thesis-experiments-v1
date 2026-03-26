import time
from typing import Dict, Any, List
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
    def __init__(self, llm, chunk_size=500, top_k=2, model_name='all-MiniLM-L6-v2'):
        super().__init__(llm)
        self.chunk_size = chunk_size
        self.top_k = top_k
        self.model_name = model_name
        
        if SentenceTransformer is None:
            raise ImportError("Please install sentence-transformers: pip install sentence-transformers")
            
        print(f"Loading embedding model '{model_name}'...")
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
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _retrieve_chunks(self, chunks: List[str], question: str) -> List[str]:
        # Encode question and chunks into semantic vectors
        q_emb = self.embedding_model.encode([question])[0]
        c_embs = self.embedding_model.encode(chunks)
        
        # Calculate semantic cosine similarity
        scored_chunks = []
        for i, c_emb in enumerate(c_embs):
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
        print(f"  -> [{self.strategy_name}] Q: {question[:80]}...")
        start_time = time.time()
        
        # Retrieval step (Semantic)
        chunks = self._chunk_text(cv_text)
        top_chunk_data = self._retrieve_chunks(chunks, question)
        
        # Separate text and indices
        best_chunks = [c_text for c_text, c_idx in top_chunk_data]
        best_indices = [c_idx for c_text, c_idx in top_chunk_data]
        
        relevant_context = "\n...\n".join(best_chunks)
        
        prompt = self._build_prompt(relevant_context, question)
        
        try:
            llm_output = self.llm.generate(prompt)
            raw_response = llm_output.get("text", "")
            input_tokens = llm_output.get("input_tokens", 0)
            output_tokens = llm_output.get("output_tokens", 0)
            estimated_cost = llm_output.get("estimated_cost", 0.0)
        except Exception as e:
            print(f"  -> [ERROR] LLM Generation failed: {e}")
            raw_response = f"ERROR: {str(e)}"
            input_tokens = 0
            output_tokens = 0
            estimated_cost = 0.0
            
        latency = time.time() - start_time
        
        return {
            "raw_response": raw_response,
            "latency": latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": estimated_cost,
            "context_used": f"Top {self.top_k} semantically matched chunks",
            # E3 specific data:
            "retrieved_chunk_ids": best_indices,
            "retrieved_text": relevant_context,
            "num_chunks_used": len(best_chunks)
        }
