import pandas as pd

from app.services.skill_extractor import extract_skills


# ============================================================
# LOAD CLEANED DATASET
# ============================================================

input_file = "datasets/processed/cleaned_resumes.csv"

df = pd.read_csv(input_file)


# ============================================================
# TEST SKILL EXTRACTION
# ============================================================

for index in range(10):

    text = df["Resume_str"].iloc[index]

    skills = extract_skills(text)

    print("\nResume:", index + 1)
    print("Category:", df["Category"].iloc[index])
    print("Extracted skills:", skills)