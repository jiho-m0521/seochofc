from flask import Flask, request, jsonify
import json
import os
from typing import Dict, List
from .models import calculate_score

app = Flask(__name__)

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

def save_match_details(match_id: str, details: Dict) -> None:
    """Save match details to JSON file."""
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, f"{match_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)

def load_match_details(match_id: str) -> Dict:
    """Load match details from JSON file."""
    file_path = os.path.join(DATA_DIR, f"{match_id}.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def load_all_matches() -> List[str]:
    """Load all match IDs from data directory."""
    import glob
    files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    return [os.path.basename(f).replace('.json', '') for f in files]

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """Get list of all match IDs."""
    matches = load_all_matches()
    return jsonify(matches)

@app.route('/api/matches/<match_id>', methods=['GET'])
def get_match(match_id):
    """Get match details by ID."""
    details = load_match_details(match_id)
    return jsonify(details)

@app.route('/api/matches/<match_id>', methods=['POST'])
def save_match(match_id):
    """Save match details."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    details = request.get_json()
    save_match_details(match_id, details)
    return jsonify({"status": "success", "message": "Match saved"})

@app.route('/api/roster', methods=['GET'])
def get_roster():
    """Get roster data from CSV."""
    files = os.listdir('.')
    target = [f for f in files if '로스터' in f and f.endswith('.csv')]
    if target:
        import pandas as pd
        df = pd.read_csv(target[0], skiprows=7)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(subset=['이름']) if '이름' in df.columns else df
        players = df['이름'].tolist()
        return jsonify({"roster": players})
    return jsonify({"roster": []})

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Get schedule data from CSV."""
    files = os.listdir('.')
    target = [f for f in files if '일정' in f and f.endswith('.csv')]
    if target:
        import pandas as pd
        df = pd.read_csv(target[0], skiprows=3)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        matches = []
        for _, row in df.iterrows():
            opp = row['상대'].replace('vs ', '').strip() if '상대' in row else 'TBD'
            date = row.get('날짜', '')
            matches.append(f"서초중 vs {opp} ({date})")
        return jsonify(matches)
    return jsonify({"schedule": []})

if __name__ == '__main__':
    app.run(port=8050, debug=True)