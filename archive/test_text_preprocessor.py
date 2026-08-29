import pandas as pd

from app.services.text_preprocessor import normalize_resume_text


# ============================================================
# LOAD CLEANED DATASET
# ============================================================

file_path = "datasets/processed/cleaned_resumes.csv"

df = pd.read_csv(file_path)


# ============================================================
# TEST TEXT NORMALIZATION
# ============================================================

df["normalized_text"] = df["Resume_str"].apply(
    normalize_resume_text
)


# ============================================================
# DISPLAY SAMPLE RESULTS
# ============================================================

for i in range(3):
    print("\nOriginal:")
    print(df["Resume_str"].iloc[i][:500])

    print("\nNormalized:")
    print(df["normalized_text"].iloc[i][:500])

    print("\n" + "=" * 70)