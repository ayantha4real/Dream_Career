import pandas as pd

from app.services.skill_extractor import extract_skills, load_skill_vocabulary


# ============================================================
# LOAD CLEANED DATASET
# ============================================================

input_file = "datasets/processed/cleaned_resumes.csv"
output_file = "datasets/processed/ml_features.csv"

df = pd.read_csv(input_file)


# ============================================================
# LOAD SKILL VOCABULARY
# ============================================================

skills = load_skill_vocabulary()

print("Total skills in vocabulary:", len(skills))


# ============================================================
# CREATE SKILL FEATURE MATRIX
# ============================================================

feature_rows = []

for index, row in df.iterrows():

    resume_text = row["Resume_str"]

    extracted_skills = extract_skills(resume_text)

    skill_set = set(extracted_skills)

    features = {
        skill: int(skill in skill_set)
        for skill in skills
    }

    features["Category"] = row["Category"]

    feature_rows.append(features)


# ============================================================
# CREATE MACHINE LEARNING DATASET
# ============================================================

ml_df = pd.DataFrame(feature_rows)


# ============================================================
# SAVE MACHINE LEARNING DATASET
# ============================================================

ml_df.to_csv(
    output_file,
    index=False
)


# ============================================================
# DISPLAY DATASET INFORMATION
# ============================================================

print("\nML dataset created successfully.")

print("\nShape:")
print(ml_df.shape)

print("\nColumns:")
print(list(ml_df.columns))

print("\nCareer categories:")
print(ml_df["Category"].value_counts())

print("\nSample:")
print(ml_df.head())