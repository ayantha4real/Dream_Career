import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# Load the refined resume dataset

dataset_path = "datasets/processed/refined_resumes.csv"

df = pd.read_csv(dataset_path)

print("Dataset shape:")
print(df.shape)

print("\nColumns:")
print(list(df.columns))


# Prepare resume text and career labels

X_text = df["Resume_str"].fillna("")
y = df["Category"]

print("\nTotal resumes:", len(X_text))
print("Career categories:", y.nunique())


# Encode career categories

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)


# Split the dataset

X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print("\nTraining samples:", len(X_train_text))
print("Testing samples:", len(X_test_text))


# Create TF-IDF features

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True
)

X_train = vectorizer.fit_transform(X_train_text)
X_test = vectorizer.transform(X_test_text)

print("\nTF-IDF feature count:", X_train.shape[1])
print("Training matrix shape:", X_train.shape)
print("Testing matrix shape:", X_test.shape)


# Train Logistic Regression

model = LogisticRegression(
    max_iter=3000,
    class_weight="balanced"
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)


# Evaluate the model

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\n" + "=" * 70)
print("TF-IDF + LOGISTIC REGRESSION")
print("=" * 70)

print(f"Accuracy: {accuracy:.4f}")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# Create model directory

model_folder = "models"

os.makedirs(model_folder, exist_ok=True)


# Save the model

model_path = os.path.join(
    model_folder,
    "tfidf_career_model.pkl"
)

joblib.dump(
    model,
    model_path
)


# Save the TF-IDF vectorizer

vectorizer_path = os.path.join(
    model_folder,
    "tfidf_vectorizer.pkl"
)

joblib.dump(
    vectorizer,
    vectorizer_path
)


# Save the label encoder

encoder_path = os.path.join(
    model_folder,
    "tfidf_label_encoder.pkl"
)

joblib.dump(
    label_encoder,
    encoder_path
)


print("\nModel saved to:")
print(model_path)

print("\nTF-IDF vectorizer saved to:")
print(vectorizer_path)

print("\nLabel encoder saved to:")
print(encoder_path)


# Display confusion matrix

print("\nConfusion matrix:")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)