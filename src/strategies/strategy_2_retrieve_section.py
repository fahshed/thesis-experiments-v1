import time
from typing import Dict, Any, List
from src.strategies.base import BaseStrategy

class Strategy2RetrieveSection(BaseStrategy):
    """
    Strategy 2: Retrieve Section, then LLM
    Uses a basic chunking and keyword overlap approach to find
    the most relevant section before prompting the LLM.
    """
    def __init__(self, llm, chunk_size=500, top_k=2):
        super().__init__(llm)
        self.chunk_size = chunk_size
        self.top_k = top_k

    @property
    def strategy_name(self) -> str:
        return "S2_Retrieve_Section"

    def _chunk_text(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size):
            chunks.append(" ".join(words[i:i + self.chunk_size]))
        return chunks

    def _retrieve_chunks(self, chunks: List[str], question: str) -> List[str]:
        # Extremely simple keyword overlap scoring
        q_words = set(question.lower().split())
        scored_chunks = []
        for chunk in chunks:
            c_words = set(chunk.lower().split())
            score = len(q_words.intersection(c_words))
            scored_chunks.append((score, chunk))
            
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [c for score, c in scored_chunks[:self.top_k]]
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
        start_time = time.time()
        
        # Retrieval step
        chunks = self._chunk_text(cv_text)
        best_chunks = self._retrieve_chunks(chunks, question)
        relevant_context = "\n...\n".join(best_chunks)
        
        prompt = self._build_prompt(relevant_context, question)
        
        try:
            llm_output = self.llm.generate(prompt)
            raw_response = llm_output.get("text", "")
            input_tokens = llm_output.get("input_tokens", 0)
            output_tokens = llm_output.get("output_tokens", 0)
            estimated_cost = llm_output.get("estimated_cost", 0.0)
        except Exception as e:
            print(f"=== -> [ERROR] LLM Generation failed: {e}")
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
            "context_used": f"Top {self.top_k} chunks",
            # E3 specific data:
            "retrieved_chunk_ids": [chunks.index(c) for c in best_chunks],
            "retrieved_text": relevant_context,
            "num_chunks_used": len(best_chunks)
        }
