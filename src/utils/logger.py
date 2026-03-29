import os
import pandas as pd
from typing import List
from src.core.schemas import RunResult


class CSVLogger:
    """
    Handles logging of RunResult objects directly to the master output CSV.
    """

    def __init__(self, output_path: str):
        self.output_path = output_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)

    def log_result(self, result: RunResult) -> None:
        """
        Appends a single RunResult object to the CSV file.
        Flattens the experiment metadata dictionary into columns.
        """
        data = result.model_dump()
        metadata = data.pop("experiment_metadata", {})
        data.update(metadata)

        df = pd.DataFrame([data])

        # Keep consistent order if possible or let pandas handle it
        if not os.path.exists(self.output_path):
            df.to_csv(self.output_path, index=False)
        else:
            df.to_csv(self.output_path, mode="a", header=False, index=False)

    def log_batch(self, results: List[RunResult]) -> None:
        """
        Logs a batch of results.
        """
        for res in results:
            self.log_result(res)
