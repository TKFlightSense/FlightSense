import pandas as pd


def load_reviews(file_path: str) -> pd.DataFrame:
    """
    Load the reviews database from CSV or Excel.
    Expects columns:
      - review (str)
      - labels (str)  [not strictly required anymore]
      - flight_delay_cancellation (int: -1,0,1)
      - checkin_boarding_process (int: -1,0,1)
      - baggage_issues (int: -1,0,1)
      - inflight_experience (int: -1,0,1)
      - pricing_fees (int: -1,0,1)
      - online_booking (int: -1,0,1)
      - date (str/datetime)
    """
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Parse date column if present
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Basic sanity filter: keep only rows with non-empty review
    if "review" in df.columns:
        df = df.dropna(subset=["review"])

    return df
