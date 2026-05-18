from typing import List, Dict, Tuple

def calculate_score(timeline: List[Dict]) -> Tuple[int, int]:
    """
    Calculate home and away scores from timeline events.
    Only goal and penalty_goal events contribute to score.
    Returns (home_score, away_score).
    """
    home_score = 0
    away_score = 0
    for event in timeline:
        if event.get('event_type') in ('goal', 'penalty_goal', '골', '페널티골'):
            team = event.get('team')
            if team == 'home':
                home_score += 1
            elif team == 'away':
                away_score += 1
    return home_score, away_score