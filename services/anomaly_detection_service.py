from collections import defaultdict
from services.db_service.mysql_db_service import MySQLDbService
from scipy.stats import wasserstein_distance
import numpy as np
from typing import Optional
from math import radians, sin, cos, sqrt, atan2

MIN_ROUTE_SAMPLES = 50

class AnomalyDetectionService:
    
    def __init__(self, db_service: Optional[MySQLDbService] = None, use_stratified_baseline: bool = False):
        self.db = db_service if db_service is not None else MySQLDbService()
        self.use_stratified_baseline = use_stratified_baseline
        self.route_scores = defaultdict(list)
        self.route_meta = {}

    def construct_route_scores(self):
        rows = self.db.get_anomaly_detection_data()

        for row in rows:
            route = row['bidirectional_route']
            score = row['sentiment_score']
            self.route_scores[route].append(score)
            if route not in self.route_meta:
                haul = self.classify_haul(
                    row['origin_iata'],
                    row['destination_iata']
                )
                self.route_meta[route] = {
                    "haul": haul
                }

    def haversine_km(self, coord1, coord2):
        R = 6371  # Earth radius (km)

        lat1, lon1 = map(radians, coord1)
        lat2, lon2 = map(radians, coord2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def classify_haul(self, origin, destination, db, threshold_km=3000):
        o = db.get_airport_coord(origin)
        d = db.get_airport_coord(destination)

        if not o or not d:
            return "unknown"

        dist = self.haversine_km((o["latitude"], o["longitude"]),(d["latitude"], d["longitude"]))

        return "long" if dist >= threshold_km else "short"


    def calculate_distances_between_routes(self):
        results = []

        for route, scores in self.route_scores.items():
            if len(scores) < MIN_ROUTE_SAMPLES:
                continue

            other_scores = []

            for r, s in self.route_scores.items():
                if r == route:
                    continue

                if self.use_stratified_baseline:
                    if self.route_meta[r]["haul"] != self.route_meta[route]["haul"]:
                        continue

                other_scores.extend(s)

            if len(other_scores) < MIN_ROUTE_SAMPLES:
                continue

            distance = wasserstein_distance(scores, other_scores)

            results.append({
                "route": route,
                "haul": self.route_meta[route]["haul"],
                "distance": distance,
                "route_samples": len(scores),
                "baseline_samples": len(other_scores)
            })

        distances = np.array([r["distance"] for r in results])

        for r in results:
            r["percentile"] = (distances < r["distance"]).mean() * 100

        return results
