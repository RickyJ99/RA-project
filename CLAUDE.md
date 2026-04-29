# Project Context — Economics RA: NLP Narrative Extraction from White House Speeches

## Research Goal

This is a Research Assistant project in economics. The objective is to extract **economic narratives** from White
House press briefing transcripts and connect them to financial uncertainty indices (FRED EPU and equity-market
uncertainty). The hypothesis is that the tone, complexity, and themes of presidential communication affect or reflect
macroeconomic uncertainty. The final product is a weekly time-series panel used in a Structural VAR (SVAR) model
estimated in MATLAB, with the Cholesky ordering: EPU → SYN → Sent.

Focus period: **Trump administration, January–August 2020** (COVID-19 shock window). Some earlier Trump data and
Biden press briefings are included for comparison but are not part of the VAR estimation.

---

## Repository Layout

```
RA-project/
├── CLAUDE.md                        ← this file
├── Readme.md                        ← human-readable overview
├── RA project.md                    ← week-by-week research log
├── Code_From Download to Dataset/   ← all Python/Jupyter pipeline code
├── Data/                            ← intermediate and final CSV datasets
├── Exploring_dataset/               ← R scripts for EDA
├── VAR/                             ← MATLAB VAR/SVAR code and output
├── Literature review/               ← reference papers and model cards
└── processed_texts/                 ← per-speech .txt files for CohMetrix upload
```

---

## Data Pipeline — Step by Step

Run scripts in numbered order. Each step reads the previous step's output CSV.

### Step 1 — Download (`1_Get_speech_dataset.ipynb`, `1a_urlextratction.py`)

- Scrapes all speeches from `whitehouse.gov` for the Trump and Biden administrations.
- Output: `Data/1_onlyrawdatadownloaded.csv` and `url_speeches.txt`.
- `1a_urlextratction.py` is an alternative that re-downloads from a pre-saved URL list.

### Step 2 — Metadata extraction (`2_extraction info.py`)

- Uses spaCy (`en_core_web_lg`), NLTK, and gensim to extract structured fields from raw text:
  speaker name, location, date, administration.
- Output: `Data/2_Data_after_infoextraolated.csv`.

### Step 3 — Text cleaning (`3_cleaning data.py`)

- Three sequential cleaning steps applied to each speech:
  1. `remove_sentence()` — strips the website boilerplate header.
  2. `split_text()` — separates the main speech body from the Q&A section on regex `".Q\s+"`.
     The Q&A text is stored in a separate `QA` column.
  3. `remove_pattern()` — removes location/time-stamp boilerplate (Brady Briefing Room stamps,
     Air Force One headers, teleconference headers, social-sharing footers).
- Uses `df.at[i, col]` for all writes (not chained indexing).
- Output: `Data/3_Data_after_cleaningdata.csv`.

### Step 4 — AI analysis (`4_AI_analysis.ipynb`)

This is the core analytical step. The single canonical file is `4_AI_analysis.ipynb`.

**What it does, in order:**

1. **LDA topic modeling** (sklearn `LatentDirichletAllocation`, `random_state=42`):
   - Applied to `trump_2020` press briefings (Jan–Aug 2020, titles containing "Press Bri").
   - 3 topics. Top 20 words per topic printed and saved as word-cloud PNGs (`topic_0.png`, etc.).
   - Preprocessing: regex strip → lowercase → tokenize → NLTK stop words + SmartStopList.txt →
     WordNetLemmatizer. **`SmartStopList.txt` is loaded once at module level** into `_SMART_STOPS`
     (not inside the function, which would re-read the file thousands of times).

2. **DistilBERT binary sentiment** (`distilbert-base-uncased-finetuned-sst-2-english`, default HF model):
   - Applied to **all speeches** in `df`.
   - Each speech is chunked into 512-token windows; chunk scores are averaged.
   - POSITIVE → +score, NEGATIVE → -score; result is a scalar in [−1, +1].
   - Column added: `sentiment_score`.

3. **heBERT 3-class sentiment** (`avichr/heBERT_sentiment_analysis`):
   - Applied to **all speeches** in `df`.
   - Same chunking logic; three separate mean scores per document.
   - Columns added: `sentiment_score_positive`, `sentiment_score_neutral`, `sentiment_score_negative`.
   - NaN (not 0) when a label never appeared in any chunk of a document.

4. **Gensim LDA thematic analysis** (applied to `trump_2020` only):
   - 10 topics, 10 passes, 2 workers, `random_state=42`.
   - Returns a DataFrame with `speech` and `theme` (topic_id, keywords) columns.

5. **FRED uncertainty indices**:
   - Downloads `USEPUINDXD` (Economic Policy Uncertainty) → column `UI`.
   - Downloads `WLEMUINDXD` (Equity Market Uncertainty) → column `EI` (also labelled `UI_WLE` in
     some outputs).
   - Joined by date string match (`%Y-%m-%d`).
   - **Requires** environment variable `FRED_API_KEY` (free at https://fred.stlouisfed.org/docs/api/api_key.html).

6. **Correlation analysis**:
   - `normalize()` returns a `pd.Series` (min-max, preserving the index) — **not a list**.
   - `trump_2020` is always `.sort_values("Date Time")` before plotting.
   - Two plots: sentiment_score vs. UI, and sentiment_score_negative vs. UI (after dropna).

- Output: `Data/4_Data_with_AI_Market_Indicies.csv`.
- Intermediate output (after heBERT step): `Analysis_1.csv`.

**Device**: defaults to `"cpu"`. Pass `device="cuda"` to any `analyze_*` function if a GPU is available.

### Step 5 — CohMetrix grammar indices (`5_grammar_pipeline.ipynb`)

CohMetrix (Memphis University) produces ~106 readability and syntactic cohesion indices. The pipeline is
semi-automated because the web interface requires a CAPTCHA. The entire step lives in one notebook with
three sections:

**Section 1 — Text preparation:**
- Filters `trump_2020` press briefings from `Data/4_Data_with_AI_Market_Indicies.csv`.
- Calls `limit_text(text, max_length=15000)` which strips non-standard characters and truncates.
- Saves one `.txt` file per speech to `processed_texts/{original_index}.txt`.

**Section 2 — Web automation:**
- Selenium + ChromeDriver opens the CohMetrix web interface at `http://141.225.61.35/CohMetrix2017/`.
- Tesseract OCR (`pytesseract`) attempts to solve the CAPTCHA; loops until solved.
- The `run_cohmetrix()` call is **commented out by default** — uncomment only when the server is reachable
  and the session can be supervised. The server at Memphis University is frequently unstable.

**Section 3 — Merge CohMetrix output:**
- Reads all `Resources/Trump_full/CohMetrixOutput (N).txt` files in numbered order.
- `import_cohmetrix_folder()` counts only files starting with `"CohMetrixOutput"` (ignores .DS_Store etc.)
  and iterates over all of them.
- Transposes each tab-separated file so each CohMetrix metric becomes a column.
- Merges with the Trump 2020 dataset by `Record Order` (sequential integer, 0-indexed).
- **The merge assumes CohMetrix output files and the filtered speech DataFrame are in the same order.**
- Output: `Data/6_TrumpwithCohmetrix.csv`.

### Step 6 — Weekly frequency adjustment (`6_frequencyadjustment.py`)

- Reads `Data/6_TrumpwithCohmetrix.csv`.
- Strips timezone with `.dt.tz_convert(None)` (**not** `tz_localize(None)`, which raises TypeError on
  tz-aware series).
- Uses `np.nanmean` to handle weeks with no speeches.
- Produces weekly averages for three series: EPU (`UI`), SYN (`SYNLE`), Sent (`sentiment_score`).
- Output: `Data/6_TrumpwithCohmetrix_freq.csv` with columns: `EPU`, `SYN`, `Sent` (date index).
- This CSV is the direct input to the MATLAB VAR model.

---

## Dataset Column Reference

### `3_Data_after_cleaningdata.csv`

| Column | Type | Description |
|--------|------|-------------|
| `Administration` | str | `"Trump"` or `"Biden"` |
| `Date Time` | datetime (UTC) | Speech timestamp, format `%Y-%m-%d %H:%M:%S%z` |
| `Title` | str | Speech title from whitehouse.gov |
| `Description` | str | Short description field |
| `Main text` | str | Cleaned speech body (no Q&A, no boilerplate) |
| `URL` | str | Source URL |
| `Location/Organization` | str | Extracted venue |
| `Speaker` | str | Extracted speaker name |
| `QA` | str / None | Q&A portion split from the speech |
| `sentiment_score` | float | DistilBERT binary score in [−1, +1] (added by step 4) |

### `4_Data_with_AI_Market_Indicies.csv`

All columns above, plus:

| Column | Type | Description |
|--------|------|-------------|
| `sentiment_score_positive` | float | heBERT mean positive score (NaN if label absent) |
| `sentiment_score_neutral` | float | heBERT mean neutral score |
| `sentiment_score_negative` | float | heBERT mean negative score |
| `UI` | float | Economic Policy Uncertainty index (USEPUINDXD, daily) |
| `UI_WLE` / `EI` | float | Equity Market Uncertainty index (WLEMUINDXD, daily) |

### `6_TrumpwithCohmetrix.csv`

All columns above (Trump 2020 press briefings only), plus `Record Order` (int, 0-based) and
~106 CohMetrix metrics including:

| Column | Description |
|--------|-------------|
| `DESPC` | Number of paragraphs |
| `DESSC` | Number of sentences |
| `DESWC` | Number of words |
| `DESPL` | Words per paragraph (mean) |
| `DESSL` | Words per sentence (mean) |
| `SYNLE` | **Syntactic complexity** — left-embeddedness (key VAR variable) |
| `RDFRE` | Flesch Reading Ease |
| `RDFKGL` | Flesch-Kincaid Grade Level |
| `WRDCNCc` | Concreteness (mean) |
| `WRDIMGc` | Imageability (mean) |

### `6_TrumpwithCohmetrix_freq.csv`

| Column | Source | Description |
|--------|--------|-------------|
| index | date | Week start date |
| `EPU` | `UI` | Weekly mean Economic Policy Uncertainty |
| `SYN` | `SYNLE` | Weekly mean syntactic complexity |
| `Sent` | `sentiment_score` | Weekly mean DistilBERT sentiment |

---

## Key Design Decisions

- **Filter**: all analyses focus on `(year==2020) & (month<9) & title.contains("Press Bri") & admin=="Trump"`.
  This isolates the COVID-19 shock period and one speech type (press briefings), controlling for format.
- **Two sentiment models**: heBERT gives 3-class probabilities (richer but noisier); DistilBERT gives a scalar
  useful as the VAR variable `Sent`. Both are stored.
- **Chunking**: BERT models have a 512-token hard limit. Long speeches are split into 512-character chunks
  (characters, not tokens — a conservative approximation), scored independently, then averaged.
- **LDA used twice**: sklearn LDA for the word-cloud exploration (step 4a), gensim LDA for per-document topic
  assignment (step 4d). They are separate runs with different hyperparameters.
- **Merge by Record Order**: CohMetrix output files are numbered 0..N-1 to match the filtered and sorted
  trump_2020 DataFrame. If the filter or sort order changes, the merge will silently produce wrong results.
- **SVAR ordering**: EPU is ordered first (exogenous uncertainty shock), SYN second (how complexity of speech
  responds), Sent last (sentiment responds to both). Cholesky decomposition in MATLAB.

---

## Environment Setup

```bash
# Python dependencies
pip install transformers torch scikit-learn gensim spacy wordcloud \
            nltk fredapi matplotlib pandas selenium pytesseract opencv-python \
            pillow beautifulsoup4 requests

python -m spacy download en_core_web_lg
python -m nltk.downloader stopwords wordnet punkt

# FRED API key (free registration)
export FRED_API_KEY="your_key_here"

# For CohMetrix automation (step 5b only)
# Install ChromeDriver matching your Chrome version
```

---

## Common Gotchas

- **`.csv` extension**: the data files use `.csv` extension. Early versions of the notebook omitted it.
  Always use `pd.read_csv("3_Data_after_cleaningdata.csv")`, not `"3_Data_after_cleaningdata"`.
- **Timezone handling**: `Date Time` is stored as UTC-aware (`+00:00`). Use `.dt.tz_convert(None)` to
  strip timezone for MATLAB export. Never use `.dt.tz_localize(None)` on already-aware series — it raises
  `TypeError`.
- **Chained indexing**: always use `df.at[i, "col"] = value`, not `df["col"][i] = value`. The latter writes
  to a temporary copy and the change is silently lost.
- **`preprocess()` performance**: `SmartStopList.txt` must be loaded once at module level (`_SMART_STOPS`),
  not inside `preprocess()`. CountVectorizer calls `preprocess()` once per document × vocabulary iteration.
- **`normalize()`**: returns a `pd.Series` preserving the original index. Always call `.sort_values("Date Time")`
  before plotting so dates and values align correctly.
- **`iloc[1:]` anti-pattern**: `pd.read_csv` already drops the CSV header row. Calling `.iloc[1:]` afterward
  silently drops the first real data row. This bug has been removed from all files.
- **CohMetrix range**: `import_cohmetrix_folder()` counts only files named `CohMetrixOutput*` so `.DS_Store`
  and other macOS metadata files do not corrupt the count.
- **`random_state=42`**: set on both sklearn LDA and gensim LdaMulticore for reproducible topic assignments.

---

## File Authoring Notes (for AI assistants)

- All files use relative paths from `Code_From Download to Dataset/` as the working directory.
  Open notebooks from that directory; run Python scripts with `cd "Code_From Download to Dataset"` first.
- **Canonical files per step:**
  - Step 3: `3_cleaning data.py`
  - Step 4: `4_AI_analysis.ipynb` — the single definitive notebook; do not create new variants.
  - Step 5: `5_grammar_pipeline.ipynb` — the single definitive notebook for all three CohMetrix steps.
  - Step 6: `6_frequencyadjustment.py`
- The CohMetrix automation section in `5_grammar_pipeline.ipynb` (Step 2) depends on the external server
  being online. The `run_cohmetrix()` call is commented out. Do not uncomment it automatically.
- When suggesting code changes, preserve existing column names exactly — downstream scripts and MATLAB
  code reference them by name.
- Never split steps 4 or 5 back into multiple files.
