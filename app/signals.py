import os
import numpy as np
from collections import Counter
from sklearn.ensemble import IsolationForest

def calculate_prr(drug_reaction_count, drug_total, all_reaction_count, all_total):
    """
    Proportional Reporting Ratio — the real epidemiological formula
    used by FDA, EMA, and WHO for signal detection.
    
    PRR = (drug_reaction / drug_total) / (all_reaction / all_total)
    PRR > 2 + at least 3 cases = signal worth investigating
    """
    if drug_total == 0 or all_total == 0:
        return 0
    a = drug_reaction_count / drug_total
    b = all_reaction_count / all_total
    if b == 0:
        return 0
    return round(a / b, 2)


def detect_anomaly(time_series_counts):
    """
    Isolation Forest ML model.
    Takes a list of quarterly report counts and flags
    which quarters are statistically abnormal.
    
    Example input: [12, 15, 11, 14, 89, 92, 13, 11]
    The 89 and 92 would get flagged as anomalies.
    """
    if len(time_series_counts) < 4:
        return [], False
    
    data = np.array(time_series_counts).reshape(-1, 1)
    
    model = IsolationForest(
        contamination=0.15,
        random_state=42
    )
    model.fit(data)
    predictions = model.predict(data)
    
    anomaly_indices = [i for i, p in enumerate(predictions) if p == -1]
    anomaly_detected = len(anomaly_indices) > 0
    
    return anomaly_indices, anomaly_detected


def detect_signals(reports, age_group="all"):
    """
    Main signal detection function.
    Combines PRR calculation + ML anomaly detection.
    """
    if not reports:
        return {
            "total_reports": 0,
            "age_group": age_group,
            "signals": [],
            "anomaly_detected": False,
            "anomaly_quarters": []
        }

    # filter by age group
    filtered = []
    for r in reports:
        if age_group == "all":
            filtered = reports
            break
        try:
            age = float(r["patient_age"]) if r["patient_age"] else 0
            if age_group == "65+" and age >= 65:
                filtered.append(r)
            elif age_group == "18-44" and 18 <= age < 45:
                filtered.append(r)
            elif age_group == "45-64" and 45 <= age < 65:
                filtered.append(r)
        except:
            continue

    if not filtered:
        filtered = reports

    total_reports = len(filtered)

    # count all reactions across all reports
    all_reactions = []
    for r in filtered:
        all_reactions.extend(r["reactions"])

    if not all_reactions:
        return {
            "total_reports": total_reports,
            "age_group": age_group,
            "signals": [],
            "anomaly_detected": False,
            "anomaly_quarters": []
        }

    reaction_counts = Counter(all_reactions)
    total_reactions = len(all_reactions)

    # count serious reports per reaction
    serious_counts = Counter()
    for r in filtered:
        if str(r["serious"]) == "1":
            for reaction in r["reactions"]:
                serious_counts[reaction] += 1

    # build quarterly time series for anomaly detection
    quarterly = Counter()
    for r in filtered:
        quarter = r.get("quarter", "Unknown")
        quarterly[quarter] += 1

    sorted_quarters = sorted(quarterly.keys())
    time_series = [quarterly[q] for q in sorted_quarters]

    anomaly_indices, anomaly_detected = detect_anomaly(time_series)
    anomaly_quarters = [sorted_quarters[i] for i in anomaly_indices]

    # calculate PRR for each reaction
    signals = []
    for reaction, count in reaction_counts.most_common(20):
        prr = calculate_prr(
            drug_reaction_count=count,
            drug_total=total_reports,
            all_reaction_count=total_reactions,
            all_total=total_reports * 10  # baseline approximation
        )

        # signal strength based on PRR
        if prr >= 5:
            strength = "Critical"
        elif prr >= 3:
            strength = "High"
        elif prr >= 2:
            strength = "Moderate"
        else:
            strength = "Low"

        signals.append({
            "reaction": reaction,
            "count": count,
            "serious_count": serious_counts.get(reaction, 0),
            "prr": prr,
            "signal_strength": strength,
            "flagged": prr >= 2.0 and count >= 3
        })

    signals.sort(key=lambda x: x["prr"], reverse=True)

    return {
        "total_reports": total_reports,
        "age_group": age_group,
        "signals": signals[:10],
        "anomaly_detected": anomaly_detected,
        "anomaly_quarters": anomaly_quarters,
        "chart_data": {
            "quarters": sorted_quarters,
            "counts": time_series,
            "anomaly_indices": anomaly_indices
        }
    }