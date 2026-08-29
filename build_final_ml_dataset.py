import pandas as pd

INPUT_FILE = "datasets/processed/refined_resumes.csv"
OUTPUT_FILE = "datasets/processed/ml_dataset.csv"


# Load refined dataset
df = pd.read_csv(INPUT_FILE)

df["Extracted_Skills"] = df["Extracted_Skills"].fillna("")


# Build skill vocabulary
skill_vocabulary = sorted(
    {
        skill.strip()
        for skills in df["Extracted_Skills"]
        for skill in skills.split(",")
        if skill.strip()
    }
)

print(f"Total skills in vocabulary: {len(skill_vocabulary)}")


# Create binary skill features
for skill in skill_vocabulary:
    df[skill] = df["Extracted_Skills"].apply(
        lambda skills: int(
            skill in [item.strip() for item in skills.split(",")]
        )
    )


# Keep career category as the target variable
feature_columns = skill_vocabulary + ["Category"]

ml_df = df[feature_columns]


# Save final ML dataset
ml_df.to_csv(OUTPUT_FILE, index=False)


print("\nML dataset created successfully.")

print("\nShape:")
print(ml_df.shape)

print("\nFeature count:")
print(len(skill_vocabulary))

print("\nCareer categories:")
print(ml_df["Category"].value_counts())

print("\nSample:")
print(ml_df.head())