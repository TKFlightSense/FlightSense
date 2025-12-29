from collections import defaultdict
from services.db_service.mysql_db_service import MySQLDbService
from scipy.stats import wasserstein_distance
import numpy as np

route_scores = defaultdict(list)
db_service = MySQLDbService()

rows = db_service.get_anomaly_detection_data()

for row in rows:
    route = row['bidirectional_route']
    score = row['sentiment_score']
    route_scores[route].append(score)

MIN_ROUTE_SAMPLES = 50

results = []

for route, scores in route_scores.items():
    if len(scores) < MIN_ROUTE_SAMPLES:
        continue

    # baseline = all other routes
    other_scores = []
    for r, s in route_scores.items():
        if r != route:
            other_scores.extend(s)

    if len(other_scores) < MIN_ROUTE_SAMPLES:
        continue

    distance = wasserstein_distance(scores, other_scores)

    results.append({
        'route': route,
        'distance': distance,
        'route_samples': len(scores),
        'baseline_samples': len(other_scores)
    })

distances = np.array([r['distance'] for r in results])

for r in results:
    r['percentile'] = (distances < r['distance']).mean() * 100