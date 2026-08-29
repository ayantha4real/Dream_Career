import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer


# ============================================================
# LOAD CLEANED RESUME DATASET
# ============================================================

input_file = "datasets/processed/cleaned_resumes.csv"

df = pd.read_csv(input_file)

df["Resume_str"] = (
    df["Resume_str"]
    .fillna("")
    .astype(str)
)


# ============================================================
# CREATE TF-IDF REPRESENTATION
# ============================================================

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=3,
    max_df=0.90,
    sublinear_tf=True
)

tfidf_matrix = vectorizer.fit_transform(
    df["Resume_str"]
)

terms = vectorizer.get_feature_names_out()


# ============================================================
# DISCOVER DISTINCTIVE TERMS BY CAREER
# ============================================================

for category in sorted(df["Category"].unique()):

    category_indices = (
        df["Category"] == category
    ).values

    category_matrix = (
        tfidf_matrix[category_indices]
    )

    mean_scores = (
        category_matrix.mean(axis=0)
        .A1
    )

    top_indices = mean_scores.argsort()[-30:][::-1]

    print("\n" + "=" * 70)
    print(f"CAREER: {category}")
    print("=" * 70)

    for index in top_indices:

        term = terms[index]
        score = mean_scores[index]

        print(
            f"{term:<35} {score:.4f}"
        )