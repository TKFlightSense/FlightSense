from collections import defaultdict
from services.db_service.mysql_db_service import MySQLDbService
from scipy.stats import wasserstein_distance
import numpy as np
from typing import Optional
from math import radians, sin, cos, sqrt, atan2
from models.enums.enums import LabelToDepartment
from datetime import timedelta

MIN_ROUTE_SAMPLES = 40
MIN_LABEL_SAMPLES_DRIFT = 8  
MIN_WINDOW_SAMPLES = 10


LABEL_BASELINE_MAP = {
    # In-flight
    "inflight_experience_food_beverage": "haul",
    "inflight_experience_entertainment": "haul",
    "inflight_experience_seats_comfort": "haul",
    "inflight_experience_cabin_service": "haul",
    "inflight_experience_cleanliness": "haul",

    # Baggage
    "baggage_lost": "destination",
    "baggage_damaged": "destination",

    # Ground ops
    "checkin_process": "origin",
    "boarding_process": "origin",
    "flight_delay_cancellation": "origin",

    # Global
    "booking_and_ticketing": "global",
    "customer_support": "global",
    "pricing_and_loyalty": "global",
}

DRIFT_CONFIG = {
    "window_days": 30,        # her pencere 30 gün
    "step_days": 15,          # 15 gün kayarak
    "min_windows": 3,         # en az 3 pencere
    "min_increase": 0.05,     # distance artışı eşiği
    "min_polarity_drop": -0.05,  # polarity_delta düşüş eşiği
}


class AnomalyDetectionService:
    
    def __init__(self, db_service: Optional[MySQLDbService] = None, use_stratified_baseline: bool = False):
        self.db = db_service if db_service is not None else MySQLDbService()
        self.use_stratified_baseline = use_stratified_baseline
        self.route_scores = defaultdict(list)
        self.route_meta = {}

    def generate_time_windows(self, dates, window_days, step_days):
        start = min(dates)
        end = max(dates)

        windows = []
        cur = start

        while cur + timedelta(days=window_days) <= end:
            windows.append((
                cur,
                cur + timedelta(days=window_days)
            ))
            cur += timedelta(days=step_days)

        return windows
    
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

    def classify_haul(self, origin, destination, threshold_km=3000):
        o = self.db.get_airport_coord(origin)
        d = self.db.get_airport_coord(destination)

        if not o or not d:
            return "unknown"

        dist = self.haversine_km((o["latitude"], o["longitude"]),(d["latitude"], d["longitude"]))

        return "long" if dist >= threshold_km else "short"

    def get_baseline_key(self, row, baseline_type):
        if baseline_type == "global":
            return "GLOBAL"
        if baseline_type == "haul":
            return self.route_meta[row["bidirectional_route"]]["haul"]
        if baseline_type == "origin":
            return row["origin_iata"]
        if baseline_type == "destination":
            return row["destination_iata"]
        raise ValueError(f"Unknown baseline type: {baseline_type}")

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

            route_mean = np.mean(scores)
            baseline_mean = np.mean(other_scores)
            polarity_delta = route_mean - baseline_mean

            results.append({
                "route": route,
                "haul": self.route_meta[route]["haul"],
                "distance": distance,
                "route_samples": len(scores),
                "baseline_samples": len(other_scores),
                "route_mean": route_mean,
                "baseline_mean": baseline_mean,
                "polarity_delta": polarity_delta,
            })

        distances = np.array([r["distance"] for r in results])

        for r in results:
            r["percentile"] = (distances < r["distance"]).mean() * 100
            if r["percentile"] >= 90 and r["polarity_delta"] < 0:
                r["anomaly_type"] = "BAD_ANOMALY"
            elif r["percentile"] >= 80 and r["polarity_delta"] < 0:
                 r["anomaly_type"] = "WATCHLIST"
            elif r["percentile"] >= 90 and r["polarity_delta"] > 0:
                r["anomaly_type"] = "GOOD_OUTLIER"
            else:
                r["anomaly_type"] = "NORMAL"

        return results
    
    def calculate_label_level_anomalies(self, rows, min_samples=MIN_ROUTE_SAMPLES):
        """
        Computes (route, label) level anomalies with context-aware baselines.
        """

        targets = defaultdict(list)
        meta = {}

        for row in rows:
            route = row["bidirectional_route"]
            label = row["label"]
            score = row["sentiment_score"]

            baseline_type = LABEL_BASELINE_MAP.get(label, "global")
            baseline_key = self.get_baseline_key(row, baseline_type)

            key = (route, label)
            targets[key].append(score)

            if key not in meta:
                meta[key] = {
                    "baseline_type": baseline_type,
                    "baseline_key": baseline_key,
                }

        results = []

        for (route, label), scores in targets.items():
            if len(scores) < min_samples:
                continue

            baseline_scores = []

            for (r2, l2), s2 in targets.items():
                if (r2, l2) == (route, label):
                    continue

                if meta[(r2, l2)]["baseline_type"] != meta[(route, label)]["baseline_type"]:
                    continue

                if meta[(r2, l2)]["baseline_key"] != meta[(route, label)]["baseline_key"]:
                    continue

                if l2 != label:
                    continue 

                baseline_scores.extend(s2)

            if len(baseline_scores) < min_samples:
                continue

            distance = wasserstein_distance(scores, baseline_scores)

            route_mean = np.mean(scores)
            baseline_mean = np.mean(baseline_scores)
            polarity_delta = route_mean - baseline_mean

            results.append({
                "route": route,
                "label": label,
                "baseline_type": meta[(route, label)]["baseline_type"],
                "baseline_key": meta[(route, label)]["baseline_key"],
                "distance": distance,
                "route_samples": len(scores),
                "baseline_samples": len(baseline_scores),
                "route_mean": route_mean,
                "baseline_mean": baseline_mean,
                "polarity_delta": polarity_delta,
            })

        distances = np.array([r["distance"] for r in results])

        for r in results:
            r["percentile"] = float((distances < r["distance"]).mean() * 100)

            if r["percentile"] >= 90 and r["polarity_delta"] < 0:
                r["anomaly_type"] = "BAD_ANOMALY"
            elif r["percentile"] >= 80 and r["polarity_delta"] < 0:
                 r["anomaly_type"] = "WATCHLIST"
            elif r["percentile"] >= 90 and r["polarity_delta"] > 0:
                r["anomaly_type"] = "GOOD_OUTLIER"
            else:
                r["anomaly_type"] = "NORMAL"

        return results

    def aggregate_department_anomalies(self, label_anomalies):
        """
        Aggregates (route, label) anomalies into (route, department).
        """

        dept_groups = defaultdict(list)

        for r in label_anomalies:
            dept = LabelToDepartment[r["label"]].value
            if not dept:
                continue
            key = (r["route"], dept)
            dept_groups[key].append(r)

        results = []

        for (route, dept), items in dept_groups.items():
            distances = [x["distance"] for x in items]
            polarity_deltas = [x["polarity_delta"] for x in items]

            dept_distance = float(np.mean(distances))
            dept_polarity = float(np.mean(polarity_deltas))

            types = {x["anomaly_type"] for x in items}

            if "BAD_ANOMALY" in types:
                anomaly_type = "BAD_ANOMALY"
            elif "WATCHLIST" in types:
                anomaly_type = "WATCHLIST"
            elif "GOOD_OUTLIER" in types:
                anomaly_type = "GOOD_OUTLIER"
            else:
                anomaly_type = "NORMAL"

            results.append({
                "route": route,
                "department": dept,
                "distance": dept_distance,
                "polarity_delta": dept_polarity,
                "labels": [x["label"] for x in items],
                "anomaly_type": anomaly_type,
                "num_labels": len(items),
            })

        return results
    
    def detect_temporal_drift(
        self,
        rows,
        window_days=30,
        step_days=15,
    ):
        """
        Detects temporal drift for (route, department).
        """

        dates = [row["event_time"] for row in rows if row.get("event_time")]
        if len(dates) == 0:
            return []

        windows = self.generate_time_windows(
            dates,
            window_days,
            step_days
        )

        if len(windows) < DRIFT_CONFIG["min_windows"]:
            return []

        window_results = []

        for start, end in windows:
            window_rows = [
                r for r in rows
                if start <= r["event_time"] < end
            ]

            if len(window_rows) < MIN_ROUTE_SAMPLES:
                continue

            label_anoms = self.calculate_label_level_anomalies(window_rows)
            dept_anoms = self.aggregate_department_anomalies(label_anoms)

            for d in dept_anoms:
                d_copy = d.copy()
                d_copy["window_start"] = start
                d_copy["window_end"] = end
                window_results.append(d_copy)

        trends = defaultdict(list)

        for r in window_results:
            key = (r["route"], r["department"])
            trends[key].append(r)

        drift_results = []

        for (route, dept), items in trends.items():
            if len(items) < DRIFT_CONFIG["min_windows"]:
                continue

            items.sort(key=lambda x: x["window_start"])

            distances = [x["distance"] for x in items]
            polarities = [x["polarity_delta"] for x in items]

            dist_increase = distances[-1] - distances[0]
            polarity_drop = polarities[-1] - polarities[0]

            if (
                dist_increase >= DRIFT_CONFIG["min_increase"]
                and polarity_drop <= DRIFT_CONFIG["min_polarity_drop"]
            ):
                drift_results.append({
                    "route": route,
                    "department": dept,
                    "distance_start": distances[0],
                    "distance_end": distances[-1],
                    "distance_increase": dist_increase,
                    "polarity_start": polarities[0],
                    "polarity_end": polarities[-1],
                    "polarity_drop": polarity_drop,
                    "num_windows": len(items),
                    "drift_type": "NEGATIVE_DRIFT",
                })

        return drift_results

