from collections import defaultdict
from typing import Dict, List
import pandas as pd
from .analyzer import analyze_review
from packages.stats.utils import load_reviews


class StatisticsEngine:

    def __init__(self, df: pd.DataFrame):
        """
        df should contain columns:
          - review (str)
          - date (datetime)
          - flight_delay_cancellation, checkin_boarding_process, baggage_issues,
            inflight_experience, pricing_fees, online_booking  (int: -1,0,1)
        """
        self.df = df.copy()
        self.total_reviews = len(df)

        # Ensure date is datetime
        if "date" in self.df.columns:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")

        self.label_columns = [
            "flight_delay_cancellation",
            "checkin_boarding_process",
            "baggage_issues",
            "inflight_experience",
            "pricing_fees",
            "online_booking",
        ]

    def get_total_feedback(self, label: str) -> int:
        if label not in self.label_columns:
            return 0
        return int((self.df[label] != 0).sum())

    def get_label_percentage(self, label: str) -> float:
        total_label = self.get_total_feedback(label)
        if self.total_reviews == 0:
            return 0.0
        return round(total_label / self.total_reviews * 100, 2)

    def get_pos_neg_ratio(self, label: str) -> Dict[str, float]:
        if label not in self.label_columns:
            return {"positive": 0.0, "negative": 0.0}

        pos = int((self.df[label] == 1).sum())
        neg = int((self.df[label] == -1).sum())
        total = pos + neg
        if total == 0:
            return {"positive": 0.0, "negative": 0.0}

        return {
            "positive": round(pos / total * 100, 2),
            "negative": round(neg / total * 100, 2),
        }

    def get_subtopic_distribution(self, label: str) -> Dict[str, Dict[str, float]]:
        if label not in self.label_columns:
            return {}

        neg_df = self.df[self.df[label] == -1].copy()
        combined = defaultdict(int)

        for _, row in neg_df.iterrows():
            sentiments = {
                "flight_delay_cancellation": int(
                    row.get("flight_delay_cancellation", 0)
                ),
                "checkin_boarding_process": int(row.get("checkin_boarding_process", 0)),
                "baggage_issues": int(row.get("baggage_issues", 0)),
                "inflight_experience": int(row.get("inflight_experience", 0)),
                "pricing_fees": int(row.get("pricing_fees", 0)),
                "online_booking": int(row.get("online_booking", 0)),
            }

            result = analyze_review(str(row["review"]), sentiments)
            if label in result:
                for sub, data in result[label].items():
                    combined[sub] += data["count"]

        total = sum(combined.values()) if combined else 1
        return {
            sub: {
                "count": count,
                "percentage": round(count / total * 100, 2),
            }
            for sub, count in sorted(combined.items(), key=lambda x: x[1], reverse=True)
        }

    def get_history(self, label: str) -> List[Dict[str, object]]:
        if label not in self.label_columns or "date" not in self.df.columns:
            return []

        df = self.df.dropna(subset=["date"]).copy()
        if df.empty:
            return []

        df = df[df[label] != 0].copy()
        if df.empty:
            return []

        # Week periods
        df["week_start"] = (
            df["date"]
            .dt.to_period("W")
            .apply(lambda p: p.start_time.date().isoformat())
        )

        grouped = df.groupby(["week_start", label]).size().unstack(fill_value=0)

        history = []
        for week_start, row in grouped.iterrows():
            positive = int(row.get(1, 0))
            negative = int(row.get(-1, 0))
            history.append(
                {
                    "week": week_start,
                    "positive": positive,
                    "negative": negative,
                }
            )

        history.sort(key=lambda x: x["week"])
        return history

    def generate_label_statistics(self, label: str) -> Dict[str, object]:
        return {
            "label": label,
            "total_feedback": self.get_total_feedback(label),
            "label_percentage": self.get_label_percentage(label),
            "pos_neg_ratio": self.get_pos_neg_ratio(label),
            "subtopic_distribution": self.get_subtopic_distribution(label),
            "history": self.get_history(label),
        }


# Test statistics
if __name__ == "__main__":
    file_path = "data/raw/labeled_data.csv"  # <-- update name here
    df = load_reviews(file_path)

    label_cols = [
        "flight_delay_cancellation",
        "checkin_boarding_process",
        "baggage_issues",
        "inflight_experience",
        "pricing_fees",
        "online_booking",
    ]

    engine = StatisticsEngine(df)

    for label in label_cols:
        stats = engine.generate_label_statistics(label)

        print(f"\n=== STATISTICS FOR {label} ===")
        print(f"Total feedback count: {stats['total_feedback']}")
        print(f"Label percentage: {stats['label_percentage']}%")
        print(f"Pos/Neg ratio: {stats['pos_neg_ratio']}")

        print("\nSubtopic distribution:")
        for sub, info in stats["subtopic_distribution"].items():
            print(f"  {sub}: {info['count']} ({info['percentage']}%)")

        print("\nWeekly history (first 10 points):")
        for point in stats["history"][:10]:
            print(point)
