from typing import Dict, List
import numpy as np
from .settings import TOPK, load_label_map, load_thresholds
from tkfs_common.enums import DEPT_PAIRS

# load HF model/tokenizer elsewhere; keep this file framework-agnostic
LABELS = load_label_map()
THRESH = load_thresholds()

def postprocess_scores(scores: Dict[str, float], topk: int = TOPK) -> List[str]:
    """
    scores: {"label_name": prob, ...} for all 12 labels (sigmoid outputs)
    Constraints:
      - For each department, at most one of {neg,pos} can appear.
      - Select only labels >= threshold.
      - Cap total selections to topk by score (default 3).
    """
    # per-department resolution
    selected = []
    for dept, (neg, pos) in DEPT_PAIRS.items():
        s_neg, s_pos = scores[neg], scores[pos]
        pass_neg = s_neg >= THRESH[neg]
        pass_pos = s_pos >= THRESH[pos]
        if pass_neg and pass_pos:
            # pick higher; if tie, prefer negative or define deterministic tiebreak
            chosen = neg if s_neg >= s_pos else pos
            selected.append((chosen, scores[chosen]))
        elif pass_neg:
            selected.append((neg, s_neg))
        elif pass_pos:
            selected.append((pos, s_pos))
        # else: none selected for this dept

    # global top-k
    selected.sort(key=lambda x: x[1], reverse=True)
    return [lbl for lbl, _ in selected[:topk]]