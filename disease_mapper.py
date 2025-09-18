# pip install rapidfuzz
from rapidfuzz import process, fuzz
import pandas as pd

STOPWORDS = {"disease", "disorder", "syndrome", "of", "the", "and"}

def normalize(s: str) -> str:
    s = s.lower()
    # keep alnum + space
    s = ''.join(ch if ch.isalnum() or ch.isspace() else ' ' for ch in s)
    tokens = [t for t in s.split() if t and t not in STOPWORDS]
    return ' '.join(tokens)

class DiseaseNormalizer:
    def __init__(self, db_names: list[str], threshold: int = 90):
        self.raw_names = db_names
        self.norm_to_raw = {}
        for name in db_names:
            n = normalize(name)
            # prefer first seen; could collect list for collision handling
            self.norm_to_raw.setdefault(n, name)
        self.norm_keys = list(self.norm_to_raw.keys())
        self.threshold = threshold

    def map(self, user_input: str):
        ui_norm = normalize(user_input)
        # 1) exact normalized match
        if ui_norm in self.norm_to_raw:
            raw = self.norm_to_raw[ui_norm]
            return {"canonical_name": raw, "method": "exact", "score": 1.0}
        # 2) fuzzy match over normalized keys
        match = process.extractOne(
            ui_norm, self.norm_keys, scorer=fuzz.WRatio  # or fuzz.token_set_ratio
        )
        if match:
            key, score, _ = match
            if score >= self.threshold:
                return {"canonical_name": self.norm_to_raw[key], "method": "fuzzy", "score": score/100.0}
        # 3) no confident match
        return {"canonical_name": None, "method": "none", "score": 0.0} 

db_diseases = list(pd.read_csv('final_problems_with_description.csv')['description']) 

mapper = DiseaseNormalizer(db_diseases, threshold=90) 