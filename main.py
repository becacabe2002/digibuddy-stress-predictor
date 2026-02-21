from contextlib import asynccontextmanager
from typing import Literal

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

MODEL_PATH = "random_forest.joblib"


class StressFeatures(BaseModel):
    age: int
    gender: Literal["male", "female"]
    region: Literal[
        "Asia",
        "Africa",
        "North America",
        "Middle East",
        "Europe",
        "South America",
    ]
    income_level: Literal["High", "Lower-Mid", "Low", "Upper-Mid"]
    education_level: Literal["High School", "Master", "Bachelor", "PhD"]
    daily_role: Literal[
        "Part-time/Shift",
        "Full-time Employee",
        "Caregiver/Home",
        "Unemployed_Looking",
        "Student",
    ]
    device_hours_per_day: float
    phone_unlocks: int
    notifications_per_day: int
    social_media_mins: int
    study_mins: int
    physical_activity_days: float   # range enforced by caller
    sleep_hours: float
    sleep_quality: float            # range enforced by caller
    device_type: Literal["Android", "Laptop", "Tablet", "iPhone"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load model once
    try:
        app.state.model = joblib.load(MODEL_PATH)
    except Exception as exc:  # noqa: BLE001
        # Let the app start but without a model; endpoints will 500 if used
        app.state.model = None
        print(f"Failed to load model from {MODEL_PATH}: {exc}")

    yield

    # Shutdown: optionally clean up resources (nothing needed for joblib model)
    app.state.model = None


app = FastAPI(
    title="DigiBuddy Stress Level Predictor",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict:
    if getattr(app.state, "model", None) is None:
        return {"status": "unhealthy", "detail": "model not loaded"}
    return {"status": "ok"}


@app.post("/predict")
async def predict_stress_level(features: StressFeatures) -> dict:
    model = getattr(app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Build a DataFrame with the same column names used during training
    data = {
        "age": [features.age],
        "gender": [features.gender],
        "region": [features.region],
        "income_level": [features.income_level],
        "education_level": [features.education_level],
        "daily_role": [features.daily_role],
        "device_hours_per_day": [features.device_hours_per_day],
        "phone_unlocks": [features.phone_unlocks],
        "notifications_per_day": [features.notifications_per_day],
        "social_media_mins": [features.social_media_mins],
        "study_mins": [features.study_mins],
        "physical_activity_days": [features.physical_activity_days],
        "sleep_hours": [features.sleep_hours],
        "sleep_quality": [features.sleep_quality],
        "device_type": [features.device_type],
    }

    df = pd.DataFrame(data)

    prediction = model.predict(df)[0]  # expected low, Medium, High

    return {"stress_level": prediction}
