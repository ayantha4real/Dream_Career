# DreamCareer — AI-Powered Career Intelligence Platform

DreamCareer analyzes a job seeker's PDF resume and produces an actionable
career report: AI career predictions, skill-gap analysis, course
recommendations and matched live job listings from the Sri Lankan market.

## How it works

```
PDF resume upload
      │
      ▼
PyMuPDF text + table extraction          app/services/resume_parser.py
      │
      ├─► Regex skill matching (290+ skills)   app/services/skill_extractor.py
      │
      ├─► spaCy NLP analysis (NER, keywords)   app/services/nlp_analyzer.py
      │
      ├─► Rule-based career matching           app/services/career_matcher.py
      │
      ├─► TF-IDF + XGBoost classification      app/services/ml_predictor.py
      │        └─ SHAP feature attribution     app/services/shap_explainer.py
      │
      └─► Job recommendation engine            app/services/jobs/job_database.py
               (scored against scraped listings)
```

## Key features

- **AI career prediction** — XGBoost (selected against Logistic Regression
  and Random Forest baselines) over 135k TF-IDF features across 24 fields.
- **Explainable AI** — interactive SHAP attribution panel with
  positive/negative toggles on the results page.
- **Skill-gap analysis & course recommendations** for the best-match career.
- **Live job board** — Scrapy spiders refresh a SQLite registry:
  - `topjobs` — topjobs.lk (JSON-LD structured vacancy data)
  - `xpressjobs` — xpress.jobs REST API
- **Automated refresh** — one command re-crawls all sources:

  ```powershell
  venv\Scripts\python scripts\refresh_jobs.py
  ```

- **Dreamy AI assistant** — rule-based navigation agent (chat widget,
  `chatbot/engine.py`) answering platform questions.
- **Accounts** — register / login with hashed passwords (Flask-Login).

## Project layout

| Path | Purpose |
|---|---|
| `app/` | Flask application (routes, services, templates, static) |
| `chatbot/` | Assistant intent engine |
| `job_scraper/` | Scrapy project (spiders + SQLite pipeline) |
| `scripts/` | Automation utilities (`refresh_jobs.py`) |
| `datasets/` | Resume datasets, skill vocabulary, category maps |
| `models/` | Trained model artifacts (.pkl) |
| `notebooks/` | Research notebooks 01–07 (EDA → SHAP analysis) |
| `tests/` | Pytest suite |
| `archive/` | Superseded experiment scripts kept for reference |
| `database/` | `dreamcareer.db` jobs registry |

## Setup

```powershell
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# run the web app
venv\Scripts\python run.py

# refresh the job database
venv\Scripts\python scripts\refresh_jobs.py

# run tests
venv\Scripts\python -m pytest tests/ -v
```

## Model performance (held-out test split, SMOTE-balanced training)

| Model | Accuracy | F1 |
|---|---|---|
| Logistic Regression | 77.6% | 77.3% |
| Random Forest | 81.6% | 81.2% |
| **XGBoost (deployed)** | **96.84%** | **96.83%** |

The results page flags low-confidence predictions and falls back to the
deterministic skill-matching engine so users always see trustworthy output.

**Note:** XGBoost achieved 96.84% accuracy (760 test samples, 24 career classes)
after SMOTE-based retraining to address class imbalance.
