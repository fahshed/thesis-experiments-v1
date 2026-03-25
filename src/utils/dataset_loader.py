import os
import pandas as pd
from typing import List
from pypdf import PdfReader
from src.core.schemas import QARecord

def mock_dataset() -> List[QARecord]:
    return [
        QARecord(
            cv_id="CV_001",
            question_id="Q_01",
            question_category="GPA",
            question_text="What is the GPA of the candidate?",
            ground_truth_answer="3.9",
        ),
        QARecord(
            cv_id="CV_001",
            question_id="Q_02",
            question_category="Skills",
            question_text="Does the candidate know Python?",
            ground_truth_answer="Yes",
        ),
    ]

def mock_cv_texts() -> dict:
    return {
        "CV_001": "John Doe. Education: BSc in Computer Science, GPA: 3.9 out of 4.0. Skills: Python, Java, C++."
    }

def load_real_dataset(limit: int = 2) -> tuple[List[QARecord], dict]:
    dataset = []
    cv_texts = {}
    base_dir = "dataset/clean_matches"
    
    if not os.path.exists(base_dir):
        print(f"Dataset directory {base_dir} not found.")
        return dataset, cv_texts
        
    applicants = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    applicants.sort()
    
    # Process only the first 'limit' applicants
    for applicant_dir in applicants[:limit]:
        applicant_path = os.path.join(base_dir, applicant_dir)
        csv_path = os.path.join(applicant_path, "qna.csv")
        pdf_path = os.path.join(applicant_path, "cv.pdf")
        
        cv_id = applicant_dir
        
        # Load PDF text
        if os.path.exists(pdf_path):
            try:
                reader = PdfReader(pdf_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                cv_texts[cv_id] = text
            except Exception as e:
                print(f"Error reading PDF {pdf_path}: {e}")
                cv_texts[cv_id] = ""
        else:
            cv_texts[cv_id] = ""
            
        # Load Q&A pairs
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                for idx, row in df.iterrows():
                    record = QARecord(
                        cv_id=cv_id,
                        question_id=f"{cv_id}_Q{idx+1}",
                        question_category=str(row.get('section', 'Unknown')),
                        question_text=str(row.get('question', '')),
                        ground_truth_answer=str(row.get('answer', ''))
                    )
                    dataset.append(record)
            except Exception as e:
                print(f"Error reading CSV {csv_path}: {e}")
                
    return dataset, cv_texts
