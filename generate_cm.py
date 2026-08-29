import sys
import os
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, r'C:\Users\Ayant\Desktop\DREAM_CAREER')
os.chdir(r'C:\Users\Ayant\Desktop\DREAM_CAREER')

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('datasets/processed/ml_training_final.csv')
df = df.dropna(subset=['Resume_str', 'Category'])
X = df['Resume_str'].astype(str)
y = df['Category'].astype(str)

le = LabelEncoder()
y_enc = le.fit_transform(y)

# Load vectorizer
import joblib
vec = joblib.load('models/tfidf_vectorizer.pkl')

# Split same way as training
from sklearn.model_selection import train_test_split
X_train_text, X_test_text, y_train, y_test = train_test_split(
    df['Resume_str'].astype(str), 
    pd.Series(LabelEncoder().fit_transform(df['Category'])), 
    test_size=0.2, 
    random_state=42, 
    stratify=pd.Series(LabelEncoder().fit_transform(y))
)

# Load vectorizer and transform test set
vec = joblib.load('models/tfidf_vectorizer.pkl')
X_test = vec.transform(df.iloc[3037:]['Resume_str'].astype(str))
y_test = LabelEncoder().fit_transform(pd.read_csv('datasets/processed/ml_training_final.csv').iloc[3037:]['Category'])

# Load model
xgb = joblib.load('models/career_model.pkl')

# Predict
X_test_vec = joblib.load('models/tfidf_vectorizer.pkl').transform(
    pd.read_csv('datasets/processed/ml_training_final.csv').iloc[3037:]['Resume_str'].astype(str)
)
preds = joblib.load('models/career_model.pkl').predict(
    joblib.load('models/tfidf_vectorizer.pkl').transform(
        pd.read_csv('datasets/processed/ml_training_final.csv').iloc[3037:]['Resume_str'].astype(str)
    )
)

# Generate confusion matrix
from sklearn.metrics import confusion_matrix
le = LabelEncoder()
le.fit(pd.read_csv('datasets/processed/ml_training_final.csv')['Category'])

y_true = pd.read_csv('datasets/processed/ml_training_final.csv').iloc[3037:]['Category']
y_true_enc = LabelEncoder().fit(pd.read_csv('datasets/processed/ml_training_final.csv')['Category']).transform(
    pd.read_csv('datasets/processed/ml_training_final.csv').iloc[3037:]['Category']
)

preds = joblib.load('models/career_model.pkl').predict(
    joblib.load('models/tfidf_vectorizer.pkl').transform(
        pd.read_csv('datasets/processed/ml_training_final.csv').iloc[3037:]['Resume_str'].astype(str)
    )
)

cm = confusion_matrix(y_test, preds, labels=range(24))

# Plot
plt.figure(figsize=(20, 18))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=le.classes_, yticklabels=le.classes_,
            cbar_kws={'label': 'Count'})
plt.title('XGBoost Confusion Matrix (Test Set, 760 samples)', fontsize=16, pad=20)
plt.xlabel('Predicted', fontsize=12)
plt.ylabel('Actual', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()

# Save
os.makedirs('app/static/images', exist_ok=True)
plt.savefig('app/static/images/confusion_matrix.png', dpi=300, bbox_inches='tight')
print('Saved to app/static/images/confusion_matrix.png')
print('Done!')