import unittest
from src.llm.base import BaseLLM
from src.strategies.strategy_1_full_cv import Strategy1FullCV
from src.strategies.strategy_2_retrieve_section import Strategy2RetrieveSection


class MockLLM(BaseLLM):
    def __init__(self):
        self._model_name = "mock-model"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(self, prompt: str, **kwargs) -> dict:
        return {
            "text": '{"predicted_answer": "3.9", "rationale": "It says GPA is 3.9", "confidence_score": 0.9}',
            "latency": 0.1,
            "input_tokens": 100,
            "output_tokens": 20,
            "estimated_cost": 0.0,
        }


class TestStrategies(unittest.TestCase):
    def setUp(self):
        self.llm = MockLLM()
        self.cv_text = "John Doe. Education: BSc in Computer Science, GPA: 3.9 out of 4.0. Skills: Python, Java, C++."
        self.question = "What is the GPA of the candidate?"

    def test_strategy_1(self):
        strategy = Strategy1FullCV(self.llm)
        result = strategy.run(self.cv_text, self.question)

        self.assertEqual(result["predicted_answer"], "3.9")
        self.assertEqual(result["confidence_score"], 0.9)
        self.assertEqual(result["context_used"], "Full CV")

    def test_strategy_2(self):
        strategy = Strategy2RetrieveSection(self.llm, chunk_size=10, top_k=1)
        result = strategy.run(self.cv_text, self.question)

        self.assertEqual(result["predicted_answer"], "3.9")
        self.assertEqual(result["confidence_score"], 0.9)
        self.assertEqual(result["context_used"], "Top 1 chunks")
        self.assertEqual(result["num_chunks_used"], 1)


if __name__ == "__main__":
    unittest.main()
