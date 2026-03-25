import re
from typing import Set

def _normalize_text(s: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""
    if not isinstance(s, str):
        return ""
    
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)
    
    def white_space_fix(text):
        return ' '.join(text.split())
    
    def remove_punc(text):
        exclude = set('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
        return ''.join(ch for ch in text if ch not in exclude)
    
    return white_space_fix(remove_articles(remove_punc(s.lower())))

def compute_exact_match(prediction: str, ground_truth: str) -> float:
    """Returns 1.0 if normalized strings match exactly, else 0.0"""
    return 1.0 if _normalize_text(prediction) == _normalize_text(ground_truth) else 0.0

def compute_f1(prediction: str, ground_truth: str) -> float:
    """Computes F1 score between tokenized prediction and ground truth."""
    pred_tokens = _normalize_text(prediction).split()
    truth_tokens = _normalize_text(ground_truth).split()
    
    if len(pred_tokens) == 0 or len(truth_tokens) == 0:
        return int(pred_tokens == truth_tokens)
        
    common_tokens = set(pred_tokens).intersection(set(truth_tokens))
    if len(common_tokens) == 0:
        return 0.0
        
    prec = len(common_tokens) / len(pred_tokens)
    rec = len(common_tokens) / len(truth_tokens)
    
    return 2 * (prec * rec) / (prec + rec)

def compute_overlap(prediction: str, ground_truth: str) -> float:
    """Computes basic word overlap fraction."""
    pred_tokens = set(_normalize_text(prediction).split())
    truth_tokens = set(_normalize_text(ground_truth).split())
    
    if len(truth_tokens) == 0:
        return 0.0
        
    return len(pred_tokens.intersection(truth_tokens)) / len(truth_tokens)
