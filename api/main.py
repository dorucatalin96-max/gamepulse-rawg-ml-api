import os
from typing import Optional

import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field

# -----------------------------
# Config
# -----------------------------
MODEL_PATH = os.environ.get("MODEL_PATH", "ml/models/model.joblib")

app = FastAPI(
    title="GamePulse API",
    version="0.1.0",
    description="FastAPI service for RAWG-based ML predictions and analytics.",
)

_model = None


def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at '{MODEL_PATH}'. "
                f"Run: python ml/train.py"
            )
        _model = joblib.load(MODEL_PATH)
    return _model


# -----------------------------
# Schemas
# -----------------------------
class PredictRequest(BaseModel):
    rating: Optional[float] = Field(default=None, description="RAWG rating (0-5)")
    rating_top: Optional[int] = Field(default=None, description="Top rating value (usually 5)")
    metacritic: Optional[int] = Field(default=None, description="Metacritic score")
    added: Optional[int] = Field(default=None, description="RAWG 'added' count")
    playtime: Optional[int] = Field(default=None, description="Average playtime in hours")

    reviews_text_count: Optional[int] = Field(default=None)
    suggestions_count: Optional[int] = Field(default=None)

    reddit_count: Optional[int] = Field(default=None)
    twitch_count: Optional[int] = Field(default=None)
    youtube_count: Optional[int] = Field(default=None)

    has_website: Optional[bool] = Field(default=None)
    release_year: Optional[int] = Field(default=None)
    release_month: Optional[int] = Field(default=None)


class PredictResponse(BaseModel):
    prediction_ratings_count: float
    prediction_ratings_count_note: str


# -----------------------------
# Endpoints
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    model = load_model()

    # Keep SAME feature order as training
    features = [
        payload.rating,
        payload.rating_top,
        payload.metacritic,
        payload.added,
        payload.playtime,
        payload.reviews_text_count,
        payload.suggestions_count,
        payload.reddit_count,
        payload.twitch_count,
        payload.youtube_count,
        float(payload.has_website) if payload.has_website is not None else None,
        payload.release_year,
        payload.release_month,
    ]

    X = np.array([features], dtype="float64")

    # Our model was trained on log1p(ratings_count)
    y_log = float(model.predict(X)[0])
    y = float(np.expm1(y_log))

    return PredictResponse(
        prediction_ratings_count=y,
        prediction_ratings_count_note="Predicted ratings_count (inverse of log1p transform).",
    )
