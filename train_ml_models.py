import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from imblearn.over_sampling import SMOTE

from xgboost import XGBClassifier


DATASET = "datasets/processed/ml_training_final.csv"
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)


print("=" * 70)
print("LOADING DATASET")
print("=" * 70)

df = pd.read_csv(DATASET)

print("Dataset shape:", df.shape)
print("Career categories:", df["Category"].nunique())
print("Missing values:", df[["Resume_str", "Category"]].isnull().sum().sum())
print("Duplicate resumes:", df["Resume_str"].duplicated().sum())


df = df.dropna(subset=["Resume_str", "Category"])

X = df["Resume_str"].astype(str)
y = df["Category"].astype(str)


print("\nCategory distribution:")
print(y.value_counts().sort_index())


print("\n" + "=" * 70)
print("LABEL ENCODING")
print("=" * 70)

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

print("Number of classes:", len(label_encoder.classes_))


print("\n" + "=" * 70)
print("TRAIN / TEST SPLIT")
print("=" * 70)

X_train_text, X_test_text, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print("Training samples:", len(X_train_text))
print("Testing samples:", len(X_test_text))


print("\n" + "=" * 70)
print("TF-IDF")
print("=" * 70)

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

print("TF-IDF feature count:", X_train.shape[1])
print("Training matrix:", X_train.shape)
print("Testing matrix:", X_test.shape)


# Apply SMOTE to balance training data (only on training set to avoid data leakage)
print("\n" + "=" * 70)
print("APPLYING SMOTE (Training data only)")
print("=" * 70)

smote = SMOTE(random_state=42, k_neighbors=3)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

print(f"Original training samples: {X_train.shape[0]}")
print(f"Resampled training samples: {X_train_resampled.shape[0]}")
print("Class distribution after SMOTE:")
print(pd.Series(y_train_resampled).value_counts().sort_index())

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        C=2.0
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    ),

    "XGBoost": XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="mlogloss",
        n_jobs=-1
    )
}


results = []
trained_models = {}


for name, model in models.items():

    print("\n" + "=" * 70)
    print(name.upper())
    print("=" * 70)

    model.fit(X_train_resampled, y_train_resampled)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )
    recall = recall_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )
    f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    print("Accuracy: ", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall:   ", round(recall, 4))
    print("F1-score: ", round(f1, 4))

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1
    })

    trained_models[name] = model


results_df = pd.DataFrame(results)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df
    .sort_values("F1", ascending=False)
    .to_string(index=False)
)


best_model_name = (
    results_df
    .sort_values("F1", ascending=False)
    .iloc[0]["Model"]
)

best_model = trained_models[best_model_name]

print("\nSelected model:", best_model_name)


joblib.dump(
    best_model,
    os.path.join(MODEL_DIR, "career_model.pkl")
)

joblib.dump(
    vectorizer,
    os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
)

joblib.dump(
    label_encoder,
    os.path.join(MODEL_DIR, "career_label_encoder.pkl")
)

results_df.to_csv(
    os.path.join(MODEL_DIR, "model_comparison.csv"),
    index=False
)

print("\nSaved:")
print("models/career_model.pkl")
print("models/tfidf_vectorizer.pkl")
print("models/career_label_encoder.pkl")
print("models/model_comparison.csv")

print("\nTraining completed successfully.")