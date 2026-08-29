import pandas as pd

orig = pd.read_csv('datasets/Resume.csv')
print('Original Resume.csv:')
print(f'  Rows: {len(orig)}')
print(f'  Categories: {orig["Category"].nunique()}')
print(f'  Duplicates: {orig["Resume_str"].duplicated().sum()}')
print()
print('Category distribution:')
print(orig['Category'].value_counts())

print()
print('=' * 50)

# Check processed files
cleaned = pd.read_csv('datasets/processed/cleaned_resumes.csv')
print(f'cleaned_resumes.csv: {len(cleaned)} rows')

refined = pd.read_csv('datasets/processed/refined_resumes.csv')
print(f'refined_resumes.csv: {len(refined)} rows')

synthetic = pd.read_csv('datasets/processed/synthetic_resumes.csv')
print(f'synthetic_resumes.csv: {len(synthetic)} rows')

ml = pd.read_csv('datasets/processed/ml_training_final.csv')
print(f'ml_training_final.csv: {len(ml)} rows')
print(f'Categories: {ml["Category"].nunique()}')
print(ml['Category'].value_counts())