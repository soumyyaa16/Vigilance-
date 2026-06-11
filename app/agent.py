import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
def explain_signal(drug_name, signals_data):
    """
    Gemini reads the PRR + ML results and writes
    a clinical interpretation. AI is used ONLY for
    explanation — not for finding signals. That's done
    by real math in signals.py.
    """

    if not signals_data or not signals_data.get("signals"):
        return "No significant signals detected for this drug."

    top_signals = signals_data["signals"][:5]
    total_reports = signals_data["total_reports"]
    age_group = signals_data["age_group"]
    anomaly_detected = signals_data.get("anomaly_detected", False)
    anomaly_quarters = signals_data.get("anomaly_quarters", [])

    signal_text = ""
    for s in top_signals:
        flag = "FLAGGED" if s["flagged"] else "MONITORED"
        signal_text += f"""
- Reaction: {s['reaction']}
  Reports: {s['count']} out of {total_reports}
  Serious cases: {s['serious_count']}
  PRR Score: {s['prr']} ({s['signal_strength']} signal) [{flag}]
"""

    anomaly_text = ""
    if anomaly_detected:
        anomaly_text = f"""
ML Anomaly Detection: POSITIVE
Unusual reporting spikes detected in quarters: {', '.join(anomaly_quarters)}
"""
    else:
        anomaly_text = "ML Anomaly Detection: No unusual temporal spikes detected."

    prompt = f"""
You are a pharmacovigilance analyst reviewing FDA FAERS adverse event data.

Drug: {drug_name}
Age Group Analyzed: {age_group}
Total Reports Analyzed: {total_reports}

Top Adverse Event Signals (by Proportional Reporting Ratio):
{signal_text}

{anomaly_text}

Write a concise clinical signal assessment. Include:
1. One-sentence summary of the most critical finding
2. Which reactions are most concerning and why the PRR score matters
3. What the ML anomaly finding means (if detected)
4. Recommended action: Monitor / Investigate / Escalate

Keep it under 200 words. Be direct and clinical. Never invent data.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Clinical interpretation unavailable: {e}"