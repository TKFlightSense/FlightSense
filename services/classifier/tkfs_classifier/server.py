from fastapi import FastAPI
from tkfs_common.schemas import ReviewIn, MultiLabelOut
from .pipeline import postprocess_scores

app = FastAPI(title="tkfs-classifier")

@app.post("/classify", response_model=MultiLabelOut)
def classify(review: ReviewIn):
    # 1) run model -> raw label probabilities (dict of 12)
    raw_scores = run_model(review)  # {"label": float}
    chosen = postprocess_scores(raw_scores)
    return MultiLabelOut(review_id=review.id, labels=chosen, scores=raw_scores)

@app.post("/classify_batch")
def classify_batch(payload: dict):
    # payload: {"reviews": [ReviewIn,...]}
    items = []
    for r in payload["reviews"]:
        raw = run_model(ReviewIn(**r))
        items.append(MultiLabelOut(review_id=r.get("id"), labels=postprocess_scores(raw), scores=raw).model_dump())
    return {"items": items}