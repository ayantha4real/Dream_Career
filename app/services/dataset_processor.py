import pandas as pd


def load_resume_dataset(file_path):
    df = pd.read_csv(file_path)

    return df


def inspect_dataset(df):
    print("Dataset shape:", df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:", df.duplicated().sum())

    return df


def inspect_resume_lengths(df):
    df = df.copy()

    df["resume_length"] = df["Resume_str"].str.len()

    print("\nShortest resumes:")
    print(
        df[["ID", "Category", "resume_length"]]
        .sort_values("resume_length")
        .head(20)
        .to_string(index=False)
    )

    print("\nLongest resumes:")
    print(
        df[["ID", "Category", "resume_length"]]
        .sort_values("resume_length", ascending=False)
        .head(20)
        .to_string(index=False)
    )


def inspect_category_lengths(df):
    df = df.copy()

    df["resume_length"] = df["Resume_str"].str.len()

    category_stats = (
        df.groupby("Category")["resume_length"]
        .agg(["count", "mean", "median", "min", "max"])
        .sort_values("mean", ascending=False)
    )

    print("\nResume length by category:")
    print(category_stats.to_string())


def inspect_html(df):
    print("\nHTML statistics:")

    html_length = df["Resume_html"].str.len()

    print(html_length.describe())

    print("\nSample HTML:")
    print(df["Resume_html"].iloc[0][:1000])


def inspect_extreme_resumes(df):
    df = df.copy()

    df["resume_length"] = df["Resume_str"].str.len()

    shortest = df.sort_values("resume_length").iloc[0]

    longest = df.sort_values(
        "resume_length",
        ascending=False
    ).iloc[0]

    print("\nShortest resume:")
    print("ID:", shortest["ID"])
    print("Category:", shortest["Category"])
    print("Length:", shortest["resume_length"])
    print("Text:")
    print(shortest["Resume_str"])

    print("\n" + "=" * 70)

    print("\nLongest resume:")
    print("ID:", longest["ID"])
    print("Category:", longest["Category"])
    print("Length:", longest["resume_length"])
    print("First 3000 characters:")
    print(longest["Resume_str"][:3000])


def clean_resume_dataset(df):
    cleaned = df.copy()

    original_count = len(cleaned)

    cleaned["Resume_str"] = cleaned["Resume_str"].fillna("")
    cleaned["Category"] = cleaned["Category"].fillna("")

    cleaned["Resume_str"] = cleaned["Resume_str"].astype(str)
    cleaned["Category"] = cleaned["Category"].astype(str)

    cleaned = cleaned[
        cleaned["Resume_str"].str.strip() != ""
    ]

    cleaned = cleaned[
        cleaned["Category"].str.strip() != ""
    ]

    cleaned = cleaned.drop_duplicates(
        subset=["Resume_str", "Category"]
    )

    cleaned = cleaned.reset_index(drop=True)

    removed_count = original_count - len(cleaned)

    print("\nCleaning summary:")
    print("Original records:", original_count)
    print("Cleaned records:", len(cleaned))
    print("Removed records:", removed_count)

    return cleaned