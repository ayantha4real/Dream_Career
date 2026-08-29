"""
Build the final DreamCareer training dataset.

Combines:
  1. Original Kaggle resume corpus (Resume.csv), cleaned + deduped
  2. Sri Lankan synthetic resumes (synthetic_resumes.csv)

with GLOBAL exact and near-duplicate removal across the merge,
producing one canonical file used for all future training:

    datasets/processed/ml_training_final.csv
"""

import hashlib
import os
import re

import pandas as pd


ORIGINAL_FILE = "datasets/Resume.csv"
SYNTHETIC_FILE = "datasets/processed/synthetic_resumes.csv"
OUTPUT_FILE = "datasets/processed/ml_training_final.csv"


def normalize_text(text):
    """Aggressive normalization used ONLY for duplicate detection."""

    lowered = str(text).lower()

    words = re.findall(r"[a-z0-9]+", lowered)

    return " ".join(words)


def signature(text):
    """
    Near-duplicate signature: first 60 normalized words.
    Resumes sharing their opening are almost certainly copies.
    """

    return " ".join(normalize_text(text).split()[:60])


def main():
    original = pd.read_csv(ORIGINAL_FILE)

    synthetic = pd.read_csv(SYNTHETIC_FILE)

    # --- clean originals ---
    original = original.dropna(subset=["Resume_str", "Category"])

    original["Resume_str"] = original["Resume_str"].astype(str).str.strip()

    original = original[original["Resume_str"].str.len() > 120]

    before_orig = len(original)

    # --- clean synthetics ---
    synthetic = synthetic.dropna(subset=["Resume_str", "Category"])

    synthetic["Resume_str"] = synthetic["Resume_str"].astype(str).str.strip()

    print(f"Original rows loaded : {before_orig}")
    print(f"Synthetic rows loaded: {len(synthetic)}")

    combined = pd.concat(
        [
            original[["ID", "Resume_str", "Category"]],
            synthetic[["ID", "Resume_str", "Category"]],
        ],
        ignore_index=True,
    )

    # --- global exact dedupe ---
    combined["_norm"] = combined["Resume_str"].map(normalize_text)

    combined["_hash"] = combined["_norm"].map(
        lambda text: hashlib.md5(text.encode()).hexdigest()
    )

    before_exact = len(combined)
    combined = combined.drop_duplicates(subset=["_hash"])
    exact_removed = before_exact - len(combined)

    # --- global near dedupe ---
    combined["_sig"] = combined["_norm"].map(signature)

    before_near = len(combined)
    combined = combined.sort_values("ID").drop_duplicates(subset=["_sig"])
    near_removed = before_near - len(combined)

    combined = combined.drop(columns=["_norm", "_hash", "_sig"])

    combined = combined.sample(frac=1.0, random_state=42).reset_index(drop=True)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    combined.to_csv(OUTPUT_FILE, index=False)

    print()
    print(f"Exact duplicates removed : {exact_removed}")
    print(f"Near duplicates removed  : {near_removed}")
    print(f"FINAL dataset            : {len(combined)} rows -> {OUTPUT_FILE}")
    print()
    print("Per-class distribution:")
    print(combined["Category"].value_counts().to_string())


if __name__ == "__main__":
    main()
