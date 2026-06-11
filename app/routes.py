from flask import Blueprint, render_template, request, jsonify
from app.faers import fetch_faers_data, fetch_evidence, fetch_live_signals
from app.signals import detect_signals
from app.agent import explain_signal

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/api/drug-summary', methods=['POST'])
def drug_summary():
    """
    Main endpoint. Takes drug name + age group.
    Returns one clean object with everything the frontend needs.
    """
    data = request.get_json()
    drug_name = data.get('drug', '').strip().upper()
    age_group = data.get('age_group', 'all')

    if not drug_name:
        return jsonify({"error": "Drug name is required"}), 400

    # step 1 — fetch real FDA data
    reports = fetch_faers_data(drug_name, limit=500)

    if not reports:
        return jsonify({
            "error": f"No FDA adverse event reports found for '{drug_name}'. Try a generic name like ATORVASTATIN or METFORMIN."
        }), 404

    # step 2 — detect signals with PRR + ML
    signals_data = detect_signals(reports, age_group)

    # step 3 — gemini clinical interpretation
    explanation = explain_signal(drug_name, signals_data)

    # step 4 — fetch evidence for top reaction
    evidence = []
    if signals_data["signals"]:
        top_reaction = signals_data["signals"][0]["reaction"]
        evidence = fetch_evidence(drug_name, top_reaction, limit=10)

    # step 5 — build clean response object
    top_signal = signals_data["signals"][0] if signals_data["signals"] else None

    return jsonify({
        "drug": drug_name.title(),
        "total_reports": signals_data["total_reports"],
        "top_reaction": top_signal["reaction"] if top_signal else "None",
        "top_prr": top_signal["prr"] if top_signal else 0,
        "signal_strength": top_signal["signal_strength"] if top_signal else "Low",
        "anomaly_detected": signals_data["anomaly_detected"],
        "anomaly_quarters": signals_data["anomaly_quarters"],
        "flagged_count": len([s for s in signals_data["signals"] if s["flagged"]]),
        "age_group": age_group,
        "gemini_summary": explanation,
        "chart_data": signals_data.get("chart_data", {}),
        "signals": signals_data["signals"],
        "evidence": evidence
    })


@main.route('/api/live-signals', methods=['GET'])
def live_signals():
    """
    Powers the Live Signal Feed on the landing page.
    Pre-fetched on app load, returns instantly.
    """
    try:
        signals = fetch_live_signals()
        return jsonify({"signals": signals})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/api/evidence', methods=['POST'])
def evidence():
    """
    Fetches raw FDA evidence reports for a specific
    drug + reaction combination.
    Called when user clicks "View Evidence" on a signal card.
    """
    data = request.get_json()
    drug_name = data.get('drug', '').strip().upper()
    reaction = data.get('reaction', '').strip()

    if not drug_name or not reaction:
        return jsonify({"error": "Drug and reaction required"}), 400

    reports = fetch_evidence(drug_name, reaction, limit=10)
    return jsonify({"evidence": reports})