from collections import defaultdict
from services.db_service.mysql_db_service import MySQLDbService
from scipy.stats import wasserstein_distance
import numpy as np
from typing import Optional

MIN_ROUTE_SAMPLES = 20

class AnomalyDetectionService:
    
    def __init__(self, db_service: Optional[MySQLDbService] = None):
        self.db = db_service if db_service is not None else MySQLDbService()
        self.route_scores = defaultdict(list)

    def construct_route_scores(self):
        rows = self.db.get_anomaly_detection_data()

        for row in rows:
            route = row['bidirectional_route']
            score = row['sentiment_score']
            self.route_scores[route].append(score)

    def calculate_distances_between_routes(self):
        results = []

        for route, scores in self.route_scores.items():
            if len(scores) < MIN_ROUTE_SAMPLES:
                continue

            # baseline = all other routes
            other_scores = []
            for r, s in self.route_scores.items():
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

            return results