from app.services.dataset_processor import (
    load_resume_dataset,
    inspect_dataset,
    inspect_resume_lengths,
    inspect_category_lengths,
    inspect_html,
    inspect_extreme_resumes
)


file_path = "datasets/Resume.csv"

df = load_resume_dataset(file_path)

inspect_dataset(df)

print("\nCareer category distribution:")
print(df["Category"].value_counts())

print("\nResume text statistics:")
print(df["Resume_str"].str.len().describe())

inspect_resume_lengths(df)

inspect_category_lengths(df)

inspect_html(df)

inspect_extreme_resumes(df)