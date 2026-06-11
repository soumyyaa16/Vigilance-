# VigilanceAI
### Real-time pharmacovigilance signal detection over live FDA adverse event data.

**[Live Demo →](https://vigilance-ai-dmsr.onrender.com)** &nbsp; &nbsp;

---

## The Problem

Every year, drugs that passed clinical trials cause unexpected harm at population scale *after* approval. The FDA collects millions of adverse event reports in FAERS, but no individual can read 20 million records. Pharma companies pay **$500k+/year** for software that does this manually.

The signals exist. They're just buried.

---

## What VigilanceAI Does

A user types a drug name. The system:

1. **Fetches** up to 500 real adverse event reports live from the FDA OpenFDA API
2. **Calculates** Proportional Reporting Ratio (PRR) the exact statistical method used by the FDA, WHO, and European Medicines Agency
3. **Runs** Isolation Forest ML anomaly detection on quarterly reporting trends to flag temporal spikes
4. **Generates** a clinical signal assessment using Gemini 1.5 Flash
5. **Returns** a structured intelligence report with flagged signals, evidence records, and recommended regulatory action

No mocked data. No simulated responses. Every signal is grounded in real FDA records.

---

## Why This Is Different

| Typical hackathon health app | VigilanceAI |
|---|---|
| Symptom checker chatbot | Population-level signal detection |
| Hardcoded or mocked data | Live FDA FAERS API — 20M+ real reports |
| "AI" as a wrapper | AI as interpretation layer over real math |
| No statistical methodology | PRR — the EMA-endorsed standard |
| Frontend demo | Full signal detection pipeline |

---

## System Architecture

```
User Query
    ↓
Flask API → OpenFDA FAERS (live)
    ↓
MongoDB Atlas (aggregation + storage)
    ↓
PRR Calculation (epidemiological signal detection)
    ↓
Isolation Forest (ML temporal anomaly detection)
    ↓
Gemini 1.5 Flash (clinical interpretation)
    ↓
Structured Signal Report + Evidence Explorer
```

---

## Core Features

- **Live FDA ingestion** — real adverse event reports, zero mock data
- **PRR signal detection** — statistically validated, EMA-endorsed methodology
- **ML anomaly detection** — Isolation Forest flags abnormal quarterly reporting spikes
- **Gemini clinical interpretation** — translates statistical findings into actionable clinical language
- **Evidence Explorer** — drill into raw FDA report IDs, patient demographics, and reactions
- **Drug Intelligence Library** — 20-drug interactive knowledge base with pharmacovigilance profiles
- **Live Signal Feed** — pre-analyzed emerging signals loaded on every page visit

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MongoDB Atlas |
| Signal Detection | NumPy, scikit-learn (Isolation Forest) |
| AI Interpretation | Google Gemini 2.5 Flash |
| Data Source | FDA OpenFDA FAERS API |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Deployment | Render |

---

## Signal Detection Methodology

**Proportional Reporting Ratio (PRR):**
```
PRR = (drug_reaction / drug_total) ÷ (all_reaction / all_total)

PRR ≥ 2.0 + minimum 3 cases = signal flagged
PRR ≥ 5.0 = critical signal
```

**Isolation Forest** runs on quarterly adverse event frequencies to detect temporal anomalies quarters where reporting spikes beyond statistically normal bounds. This is how real post-market surveillance systems catch emerging safety issues before they become crises.

---

## Real-World Context

> In 2004, Vioxx was withdrawn after being linked to 140,000 heart attacks. The signals were present in FAERS data years earlier. Automated detection systems exist to close that gap.

VigilanceAI is a prototype of that system built on the same data, using the same statistical methods, accessible to anyone.

---

## Run Locally

```bash
git clone https://github.com/soumyyaa16/Vigilance-.git
cd Vigilance-
pip install -r requirements.txt
```

Create `.env`:
```
MONGODB_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
```

```bash
python run.py
```

Visit `http://localhost:5000`

---

## Disclaimer

VigilanceAI signals indicate statistical correlation not confirmed causation. FAERS data contains known reporting biases. This tool is intended for research and educational purposes only and should not be used for clinical decision-making.

---

*Built with real FDA data. Real statistical methodology. Real ML. No shortcuts.*
