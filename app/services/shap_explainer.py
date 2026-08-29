import shap
import numpy as np


_explainer_cache = {}


def _get_explainer(model):

    key = id(model)

    if key not in _explainer_cache:
        _explainer_cache[key] = shap.TreeExplainer(model)

    return _explainer_cache[key]


def explain_prediction(model, vectorizer, text, top_n=10):

    if not text or not isinstance(text, str):
        return []

    text_vector = vectorizer.transform([text])

    explainer = _get_explainer(model)

    shap_values = explainer.shap_values(text_vector)

    feature_names = vectorizer.get_feature_names_out()

    if isinstance(shap_values, list):
        values = np.array(shap_values)
        predicted_class = model.predict(text_vector)[0]
        values = values[predicted_class][0]
    else:
        values = np.array(shap_values)

        if values.ndim == 3:
            predicted_class = model.predict(text_vector)[0]
            values = values[0, :, predicted_class]
        elif values.ndim == 2:
            values = values[0]

    non_zero_indices = np.where(text_vector.toarray()[0] != 0)[0]

    contributions = []

    for index in non_zero_indices:
        value = float(values[index])

        contributions.append({
            "feature": feature_names[index],
            "impact": round(value, 4),
            "direction": "positive" if value > 0 else "negative"
        })

    max_impact = max(
        (abs(c["impact"]) for c in contributions),
        default=1
    ) or 1

    for contribution in contributions:
        contribution["weight"] = round(
            abs(contribution["impact"]) / max_impact * 100,
            1
        )

    contributions.sort(
        key=lambda x: abs(x["impact"]),
        reverse=True
    )

    return contributions[:top_n]
