import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# Load the final ML dataset

dataset_path = "datasets/processed/ml_dataset.csv"

df = pd.read_csv(dataset_path)

print("Dataset shape:")
print(df.shape)

print("\n")


# Separate features and target

X = df.drop(columns=["Category"])
y = df["Category"]

print("Feature count:")
print(X.shape[1])

print("\nCareer categories:")
print(y.nunique())


# Encode career categories

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)


# Split the dataset

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# Train Logistic Regression

logistic_model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)

logistic_model.fit(X_train, y_train)

logistic_predictions = logistic_model.predict(X_test)

logistic_accuracy = accuracy_score(
    y_test,
    logistic_predictions
)

print("\n" + "=" * 70)
print("LOGISTIC REGRESSION")
print("=" * 70)

print(f"Accuracy: {logistic_accuracy:.4f}")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        logistic_predictions,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# Train Random Forest

random_forest_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

random_forest_model.fit(X_train, y_train)

random_forest_predictions = random_forest_model.predict(X_test)

random_forest_accuracy = accuracy_score(
    y_test,
    random_forest_predictions
)

print("\n" + "=" * 70)
print("RANDOM FOREST")
print("=" * 70)

print(f"Accuracy: {random_forest_accuracy:.4f}")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        random_forest_predictions,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# Compare models

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(f"Logistic Regression Accuracy: {logistic_accuracy:.4f}")
print(f"Random Forest Accuracy:       {random_forest_accuracy:.4f}")


# Select the best model

if random_forest_accuracy > logistic_accuracy:

    best_model = random_forest_model
    best_model_name = "Random Forest"

else:

    best_model = logistic_model
    best_model_name = "Logistic Regression"


print(f"\nSelected model: {best_model_name}")


# Create model directory

model_folder = "models"

os.makedirs(model_folder, exist_ok=True)


# Save the trained model

model_path = os.path.join(
    model_folder,
    "career_prediction_model.pkl"
)

joblib.dump(best_model, model_path)


# Save the label encoder

encoder_path = os.path.join(
    model_folder,
    "career_label_encoder.pkl"
)

joblib.dump(label_encoder, encoder_path)


# Save feature names

feature_path = os.path.join(
    model_folder,
    "skill_features.pkl"
)

joblib.dump(
    list(X.columns),
    feature_path
)


print("\nModel saved to:")
print(model_path)

print("\nLabel encoder saved to:")
print(encoder_path)

print("\nFeature list saved to:")
print(feature_path)


# Display confusion matrix

print("\nConfusion matrix:")

print(
    confusion_matrix(
        y_test,
        random_forest_predictions
        if best_model_name == "Random Forest"
        else logistic_predictions
    )
)