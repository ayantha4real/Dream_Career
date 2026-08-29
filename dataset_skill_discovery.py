import re
from collections import Counter

import pandas as pd


# ============================================================
# LOAD CLEANED RESUME DATASET
# ============================================================

input_file = "datasets/processed/cleaned_resumes.csv"

df = pd.read_csv(input_file)


# ============================================================
# COMBINE RESUME TEXT
# ============================================================

texts = (
    df["Resume_str"]
    .fillna("")
    .astype(str)
    .tolist()
)

combined_text = " ".join(texts)


# ============================================================
# NORMALIZE TEXT FOR TERM DISCOVERY
# ============================================================

combined_text = combined_text.lower()


# ============================================================
# EXTRACT WORDS AND PHRASES
# ============================================================

words = re.findall(
    r"\b[a-zA-Z][a-zA-Z0-9+#./-]*\b",
    combined_text
)

word_counts = Counter(words)


# ============================================================
# DISPLAY MOST FREQUENT TERMS
# ============================================================

print("\nTop 200 terms in the resume dataset:")

for term, count in word_counts.most_common(200):
    print(f"{term:<30} {count}")


# ============================================================
# EXTRACT COMMON TWO-WORD PHRASES
# ============================================================

tokens = re.findall(
    r"\b[a-zA-Z][a-zA-Z0-9+#./-]*\b",
    combined_text
)

bigrams = zip(tokens, tokens[1:])

bigram_counts = Counter(
    f"{first} {second}"
    for first, second in bigrams
)


print("\nTop 200 two-word phrases:")

for phrase, count in bigram_counts.most_common(200):
    print(f"{phrase:<40} {count}")