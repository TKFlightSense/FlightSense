from fastapi import FastAPI
from tkfs_common.schemas import ReviewIn, MultiLabelOut
from .pipeline import run_model, postprocess_scores  # <-- keep this import

app = FastAPI(title="tkfs-classifier")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/classify", response_model=MultiLabelOut)
def classify(review: ReviewIn) -> MultiLabelOut:
    raw_scores = run_model(review)
    chosen = postprocess_scores(raw_scores)
    return MultiLabelOut(review_id=review.id, labels=chosen, scores=raw_scores)


@app.post("/classify_batch")
def classify_batch(payload: dict) -> dict:
    items = []
    for r in payload.get("reviews", []):
        raw = run_model(ReviewIn(**r))
        items.append(
            MultiLabelOut(
                review_id=r.get("id"),
                labels=postprocess_scores(raw),
                scores=raw,
            ).model_dump()
        )
    return {"items": items}
