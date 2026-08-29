import pandas as pd


# ============================================================
# LOAD MACHINE LEARNING DATASET
# ============================================================

input_file = "datasets/processed/ml_features.csv"

df = pd.read_csv(input_file)


# ============================================================
# SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop(columns=["Category"])
y = df["Category"]


# ============================================================
# FEATURE USAGE ANALYSIS
# ============================================================

feature_usage = X.sum().sort_values(ascending=False)


print("\nTotal resumes:", len(df))
print("Total skill features:", len(X.columns))
print("Total career categories:", y.nunique())


# ============================================================
# MOST COMMON SKILLS
# ============================================================

print("\nMost frequently detected skills:")

print(
    feature_usage.head(30)
)


# ============================================================
# RARE SKILLS
# ============================================================

print("\nLeast frequently detected skills:")

print(
    feature_usage.sort_values().head(20)
)


# ============================================================
# UNUSED FEATURES
# ============================================================

unused_features = feature_usage[
    feature_usage == 0
]


print("\nUnused skill features:")

if len(unused_features) == 0:
    print("None")
else:
    print(unused_features)


# ============================================================
# SKILLS PER RESUME
# ============================================================

skills_per_resume = X.sum(axis=1)


print("\nSkills detected per resume:")

print(
    skills_per_resume.describe()
)


# ============================================================
# SKILLS PER CAREER
# ============================================================

career_skill_counts = (
    df.groupby("Category")[X.columns]
    .sum()
)

career_skill_counts["Total_Skill_Matches"] = (
    career_skill_counts.sum(axis=1)
)


print("\nTotal skill matches by career:")

print(
    career_skill_counts["Total_Skill_Matches"]
    .sort_values(ascending=False)
)


# ============================================================
# SAVE AUDIT RESULTS
# ============================================================

feature_usage.to_csv(
    "datasets/processed/skill_usage.csv",
    header=["resume_count"]
)

print("\nAudit results saved.")