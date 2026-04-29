## Overview

This repository contains code and resources for a project that uses NLP and AI models to extract economic narratives
from White House speech transcripts (Trump and Biden administrations). The pipeline downloads raw speeches, cleans
them, applies sentiment and topic analysis, merges syntactic readability indices from CohMetrix, and produces weekly
time-series data ready for VAR/SVAR estimation in MATLAB or R.

---

## `Code_From Download to Dataset`

This folder contains the full data pipeline. Run the scripts in numbered order.

### Step 1 — Download speeches

- **`1_Get_speech_dataset.ipynb`**: Downloads all speeches for the Trump and Biden administrations from the White
  House website and saves them in `Data/dataset1_onlyrawdatadownloaded.csv`. Also saves `url_speeches.txt` with
  every URL visited.

- **`1_a_urlextraction.py`**: Alternative entry point. Reads `url_speeches.txt` and re-downloads speeches from a
  custom list of White House URLs.

### Step 2 — Extract metadata

- **`2_extraction info.py`**: Uses NLP (spaCy, NLTK, gensim) to extract structured metadata from each speech:
  location, date, speaker name, and administration. Output: `Data/2_Data_after_infoextraolated.csv`.

### Step 3 — Clean text

- **`3_cleaning data.py`**: Reads `2_Data_after_infoextraolated.csv` and applies three cleaning steps in sequence:
  1. Strips the website boilerplate header (`remove_sentence`)
  2. Splits the main speech body from the Q&A transcript (`split_text`) — Q&A is stored separately in the `QA` column
  3. Removes location/time-stamp patterns (Brady Briefing Room stamps, Air Force One headers, etc.) from the cleaned
     body text (`remove_pattern`)

  Output: `Data/3_Data_after_cleaningdata.csv`.

### Step 4 — AI analysis

- **`4_AI_analysis.ipynb`** — Single notebook for the full AI analysis:
  1. LDA topic modeling + word clouds (sklearn) on Trump 2020 press briefings
  2. DistilBERT binary sentiment score (`sentiment_score`, range −1 to +1) for all speeches
  3. heBERT 3-class sentiment (`sentiment_score_positive/neutral/negative`) for all speeches
  4. Gensim LDA thematic analysis on Trump 2020 press briefings
  5. Economic Policy Uncertainty (EPU) and Equity Market Uncertainty (EMU) indices merged from FRED
  6. Sentiment vs. EPU correlation and time-series plots

  **Requires** `FRED_API_KEY` environment variable (free key at https://fred.stlouisfed.org/docs/api/api_key.html).
  Output: `Data/4_Data_with_AI_Market_Indicies.csv`.

### Step 5 — CohMetrix grammar indices

- **`5_grammar_pipeline.ipynb`** — Single notebook for the full CohMetrix pipeline:
  1. **Text preparation** — filter Trump 2020 press briefings, clean with `limit_text()`, save one `.txt` per
     speech to `processed_texts/`
  2. **Web automation** — Selenium + Tesseract OCR submits texts to the CohMetrix web interface at
     Memphis University (`http://141.225.61.35/CohMetrix2017/`). The `run_cohmetrix()` call is commented out
     by default; uncomment only when the server is reachable and the session is supervised.
  3. **Merge output** — reads all `CohMetrixOutput (N).txt` files, transposes metrics, merges with the Trump
     2020 speech dataset by record order. Output: `Data/6_TrumpwithCohmetrix.csv`.

### Step 6 — Weekly frequency adjustment

- **`6_frequencyadjustment.py`**: Aggregates the daily speech-level data to weekly averages for three series:
  - `EPU` — Economic Policy Uncertainty index
  - `SYN` — Syntactic complexity (SYNLE from CohMetrix)
  - `Sent` — DistilBERT sentiment score

  Output: `Data/6_TrumpwithCohmetrix_freq.csv`. This file is the direct input to the VAR/SVAR model in MATLAB.

---

## `Data`

Intermediate and final datasets, one CSV per pipeline step:

| File | Contents |
|------|----------|
| `dataset1_onlyrawdatadownloaded.csv` | Raw speech text + URL |
| `2_Data_after_infoextraolated.csv` | + extracted metadata |
| `3_Data_after_cleaningdata.csv` | + cleaned speech body and QA column |
| `4_Data_with_AI_Market_Indicies.csv` | + sentiment scores + EPU/EMU indices |
| `6_TrumpwithCohmetrix.csv` | Trump 2020 speeches + all CohMetrix indices |
| `6_TrumpwithCohmetrix_freq.csv` | Weekly averages of EPU, SYN, Sent |

---

## `Exploring_dataset`

R scripts for exploratory data analysis: summary statistics, stationarity tests, and preliminary time-series plots.

---

## `VAR`

MATLAB code and output for the Structural VAR model. The Cholesky decomposition ordering is:
EPU → SYN → Sent (uncertainty shock → speech complexity → sentiment).

---

## `Literature review`

Scientific articles that use similar NLP-based narrative extraction methods, and model cards for the AI models used:
- `avichr/heBERT_sentiment_analysis` (3-class sentiment)
- `distilbert-base-uncased-finetuned-sst-2-english` (binary sentiment)
- `en_core_web_lg` (spaCy NER/lemmatization)
