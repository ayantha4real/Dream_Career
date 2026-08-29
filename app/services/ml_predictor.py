import os
import joblib

from app.services.shap_explainer import explain_prediction


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "career_model.pkl"
)

VECTORIZER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "tfidf_vectorizer.pkl"
)

ENCODER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "career_label_encoder.pkl"
)


CONFIDENCE_THRESHOLD = 40.0

MIN_TEXT_LENGTH = 120


_artifacts = None


def _load_artifacts():
    global _artifacts

    if _artifacts is None:

        _artifacts = {
            "model": joblib.load(MODEL_PATH),
            "vectorizer": joblib.load(VECTORIZER_PATH),
            "label_encoder": joblib.load(ENCODER_PATH)
        }

    return _artifacts


def predict_career(text, top_n=5):

    empty_result = {
        "predictions": [],
        "explanations": [],
        "confidence": 0.0,
        "low_confidence": True
    }

    if not text or not isinstance(text, str):
        return empty_result

    if len(text.strip()) < MIN_TEXT_LENGTH:
        return empty_result

    artifacts = _load_artifacts()

    model = artifacts["model"]
    vectorizer = artifacts["vectorizer"]
    label_encoder = artifacts["label_encoder"]

    text_vectorized = vectorizer.transform([text])

    probabilities = model.predict_proba(text_vectorized)[0]

    top_indices = probabilities.argsort()[-top_n:][::-1]

    predictions = []

    for index in top_indices:

        career = label_encoder.inverse_transform([index])[0]

        probability = float(probabilities[index] * 100)

        predictions.append({
            "career": career,
            "probability": round(probability, 2)
        })

    confidence = float(predictions[0]["probability"]) if predictions else 0.0

    explanations = explain_prediction(
        model,
        vectorizer,
        text,
        top_n=10
    )

    return {
        "predictions": predictions,
        "explanations": explanations,
        "confidence": round(confidence, 1),
        "low_confidence": confidence < CONFIDENCE_THRESHOLD
    }
