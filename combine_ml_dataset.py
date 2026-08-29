import pandas as pd

original_file = "datasets/processed/cleaned_resumes.csv"
synthetic_file = "datasets/processed/synthetic_resumes.csv"
output_file = "datasets/processed/ml_resumes.csv"

original = pd.read_csv(original_file)
synthetic = pd.read_csv(synthetic_file)

print("Original dataset:", original.shape)
print("Synthetic dataset:", synthetic.shape)

combined = pd.concat(
    [original, synthetic],
    ignore_index=True
)

combined = combined.drop_duplicates(
    subset=["Resume_str", "Category"]
)

combined = combined.reset_index(drop=True)

combined.to_csv(
    output_file,
    index=False
)

print("\nCombined dataset created:")
print("Records:", len(combined))
print("Columns:", combined.columns.tolist())

print("\nCategory distribution:")
print(
    combined["Category"]
    .value_counts()
    .sort_index()
)

print("\nSaved to:")
print(output_file)