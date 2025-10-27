import json, os
from pathlib import Path

TOPK = int(os.getenv("CLASSIFIER_TOPK", "3"))

def load_label_map(path="models/artifacts/label_map.json"):
    return json.loads(Path(path).read_text())["labels"]

def load_thresholds(path="models/artifacts/thresholds.json"):
    if Path(path).exists():
        return json.loads(Path(path).read_text())
    # default 0.5 if file not present
    return {lbl: 0.5 for lbl in load_label_map()}