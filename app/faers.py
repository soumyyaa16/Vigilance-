import requests
from datetime import datetime
import threading

OPENFDA_BASE = "https://api.fda.gov/drug/event.json"

# Cache so live signals only fetch once per server session
_live_cache = None
_cache_lock = threading.Lock()


def fetch_faers_data(drug_name, limit=500):
    params = {
        "search": f'patient.drug.medicinalproduct:"{drug_name}"',
        "limit": limit
    }
    try:
        response = requests.get(OPENFDA_BASE, params=params, timeout=15)
        data = response.json()
        if "results" not in data:
            return []
        reports = []
        for result in data["results"]:
            report = {
                "report_id": result.get("safetyreportid", ""),
                "serious": result.get("serious", 0),
                "reactions": [],
                "patient_age": None,
                "patient_sex": None,
                "quarter": _get_quarter(result.get("receivedate", "")),
                "receive_date": result.get("receivedate", ""),
                "reporter_country": result.get("primarysourcecountry", "Unknown"),
                "raw": result
            }
            patient = result.get("patient", {})
            report["patient_age"] = patient.get("patientonsetage", None)
            sex_map = {"1": "Male", "2": "Female", "0": "Unknown"}
            report["patient_sex"] = sex_map.get(
                str(patient.get("patientsex", "0")), "Unknown"
            )
            for r in patient.get("reaction", []):
                name = r.get("reactionmeddrapt", "")
                if name:
                    report["reactions"].append(name.upper())
            reports.append(report)
        return reports
    except Exception as e:
        print(f"FDA API error: {e}")
        return []


def fetch_evidence(drug_name, reaction, limit=10):
    params = {
        "search": (
            f'patient.drug.medicinalproduct:"{drug_name}" AND '
            f'patient.reaction.reactionmeddrapt:"{reaction}"'
        ),
        "limit": limit
    }
    try:
        response = requests.get(OPENFDA_BASE, params=params, timeout=15)
        data = response.json()
        if "results" not in data:
            return []
        evidence = []
        for result in data["results"]:
            patient = result.get("patient", {})
            sex_map = {"1": "Male", "2": "Female", "0": "Unknown"}
            evidence.append({
                "report_id": result.get("safetyreportid", "N/A"),
                "date": _format_date(result.get("receivedate", "")),
                "age": patient.get("patientonsetage", "Unknown"),
                "sex": sex_map.get(str(patient.get("patientsex", "0")), "Unknown"),
                "serious": "Yes" if str(result.get("serious", 0)) == "1" else "No",
                "country": result.get("primarysourcecountry", "Unknown"),
                "reactions": [
                    r.get("reactionmeddrapt", "").upper()
                    for r in patient.get("reaction", [])
                ][:3]
            })
        return evidence
    except Exception as e:
        print(f"Evidence fetch error: {e}")
        return []


def fetch_live_signals():
    """
    Returns cached live signals if available.
    First call fetches from FDA (slow), all subsequent calls instant.
    Also runs a background prefetch on app start.
    """
    global _live_cache
    with _cache_lock:
        if _live_cache is not None:
            return _live_cache
        result = _fetch_live_signals_fresh()
        _live_cache = result
        return result


def _fetch_live_signals_fresh():
    from app.signals import detect_signals
    drugs = [
        {"name": "ATORVASTATIN", "age_group": "65+"},
        {"name": "SEMAGLUTIDE",  "age_group": "all"},
        {"name": "METFORMIN",    "age_group": "45-64"},
    ]
    live = []
    for d in drugs:
        try:
            # Only 50 reports for the live feed — fast enough
            reports = fetch_faers_data(d["name"], limit=50)
            signals = detect_signals(reports, d["age_group"])
            if signals["signals"]:
                top = signals["signals"][0]
                live.append({
                    "drug": d["name"].title(),
                    "reaction": top["reaction"],
                    "prr": top["prr"],
                    "signal_strength": top["signal_strength"],
                    "flagged": top["flagged"],
                    "total_reports": signals["total_reports"],
                    "anomaly_detected": signals["anomaly_detected"],
                    "age_group": d["age_group"]
                })
        except Exception as e:
            print(f"Live signal error for {d['name']}: {e}")
            continue
    return live


def prefetch_in_background():
    """
    Call this once when the app starts.
    Warms the cache in a background thread so the first
    user to hit /api/live-signals doesn't wait.
    """
    def _run():
        print("Prefetching live signals in background...")
        fetch_live_signals()
        print("Live signals cached.")
    t = threading.Thread(target=_run, daemon=True)
    t.start()


def _get_quarter(date_str):
    try:
        dt = datetime.strptime(date_str[:8], "%Y%m%d")
        quarter = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{quarter}"
    except:
        return "Unknown"


def _format_date(date_str):
    try:
        dt = datetime.strptime(date_str[:8], "%Y%m%d")
        return dt.strftime("%Y-%m-%d")
    except:
        return "Unknown"