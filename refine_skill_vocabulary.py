import re
import pandas as pd
from collections import Counter

INPUT_FILE = "datasets/processed/cleaned_resumes.csv"
OUTPUT_FILE = "datasets/processed/refined_resumes.csv"

# Career-specific skills and technical terms
SKILLS = [
    "Python",
    "Java",
    "C++",
    "C#",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "TensorFlow",
    "Keras",
    "Machine Learning",
    "Deep Learning",
    "Power BI",
    "Tableau",
    "Excel",
    "Git",
    "GitHub",
    "Docker",
    "AWS",
    "Azure",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Node.js",
    "Flask",
    "Django",
    "Bootstrap",
    "REST API",
    "Linux",
    "MongoDB",
    "Communication",
    "Leadership",
    "Problem Solving",
    "Teamwork",
    "Project Management",
    "Strategic Planning",
    "Time Management",
    "Conflict Resolution",
    "Decision Making",
    "Customer Service",
    "Customer Satisfaction",
    "Human Resources",
    "Recruitment",
    "Payroll",
    "Marketing",
    "Sales",
    "Public Relations",
    "Social Media",
    "Business Development",
    "Business Administration",
    "Accounting",
    "Accounts Payable",
    "Financial Statements",
    "Financial Reporting",
    "Finance",
    "Banking",
    "Database",
    "Data Analysis",
    "Data Entry",
    "Statistical Analysis",
    "Operations Management",
    "Inventory Management",
    "Quality Assurance",
    "Construction",
    "Engineering",
    "Aviation",
    "Healthcare",
    "Agriculture",
    "Automotive",
    "Food Safety",
    "Culinary",
    "Hospitality",
    "Graphic Design",
    "Digital Media",
    "Education",
    "Training and Development",
    "Adaptability",
    "Critical Thinking"
]

# Remove features that are too generic or not useful for prediction
EXCLUDED_TERMS = {
    "state",
    "city",
    "company",
    "name",
    "management",
    "experience",
    "work",
    "staff",
    "office",
    "service",
    "customer",
    "business",
    "development",
    "project",
    "training",
    "skills",
    "professional",
    "information",
    "system",
    "systems",
    "support",
    "team",
    "data",
    "process",
    "reports",
    "school",
    "university",
    "college"
}


def contains_skill(text, skill):
    pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
    return bool(re.search(pattern, text, re.IGNORECASE))


def extract_skills(text):
    found = []

    for skill in SKILLS:
        if skill.lower() in EXCLUDED_TERMS:
            continue

        if contains_skill(text, skill):
            found.append(skill)

    return sorted(set(found))


# Load cleaned dataset
df = pd.read_csv(INPUT_FILE)

df["Resume_str"] = df["Resume_str"].fillna("").astype(str)

# Extract refined skills
df["Extracted_Skills"] = df["Resume_str"].apply(extract_skills)

# Count detected skills
skill_counts = Counter()

for skills in df["Extracted_Skills"]:
    skill_counts.update(skills)

print("\nRefined skill vocabulary:")
print(f"Total candidate skills: {len(SKILLS)}")
print(f"Detected skills: {len(skill_counts)}")

print("\nMost frequently detected skills:")

for skill, count in skill_counts.most_common(30):
    print(f"{skill:<30} {count}")

print("\nLeast frequently detected skills:")

for skill, count in sorted(skill_counts.items(), key=lambda x: x[1])[:20]:
    print(f"{skill:<30} {count}")

# Create a readable skill column
df["Extracted_Skills"] = df["Extracted_Skills"].apply(
    lambda skills: ", ".join(skills)
)

df.to_csv(OUTPUT_FILE, index=False)

print("\nRefined dataset saved to:")
print(OUTPUT_FILE)

print("\nDataset shape:")
print(df.shape)