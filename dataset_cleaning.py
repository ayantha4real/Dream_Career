from app.services.dataset_processor import (
    load_resume_dataset,
    clean_resume_dataset
)


# ============================================================
# DATASET FILE PATHS
# ============================================================

input_file = "datasets/Resume.csv"
output_file = "datasets/processed/cleaned_resumes.csv"


# ============================================================
# LOAD AND CLEAN DATASET
# ============================================================

df = load_resume_dataset(input_file)

cleaned_df = clean_resume_dataset(df)


# ============================================================
# SAVE CLEANED DATASET
# ============================================================

cleaned_df.to_csv(
    output_file,
    index=False
)

print("\nCleaned dataset saved to:")
print(output_file)


# ============================================================
# VALIDATE CLEANED DATASET
# ============================================================

print("\nCleaned dataset shape:")
print(cleaned_df.shape)

print("\nMissing values:")
print(cleaned_df.isnull().sum())

print("\nDuplicate resume/category pairs:")
print(
    cleaned_df.duplicated(
        subset=["Resume_str", "Category"]
    ).sum()
)

print("\nCareer category distribution:")
print(cleaned_df["Category"].value_counts())