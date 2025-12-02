from __future__ import annotations
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import os
import json
import smtplib
from email.message import EmailMessage

import pandas as pd

from services.db_service.mysql_db_service import MySQLDbService
# from packages.stats.statistics_service import StatisticsService  # if you have one
# from packages.llm.summarizer import Summarizer  # you can add this later


def _load_email_config() -> Dict[str, Any]:
    """Load email configuration from JSON file."""
    config_path = Path("models/artifacts/email_config.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Email config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_department_routing_config() -> Dict[str, Any]:
    """Load department routing configuration from JSON file."""
    config_path = Path("models/artifacts/department_routing.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Department routing config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# Load configurations from JSON files
_EMAIL_CONFIG = _load_email_config()
_ROUTING_CONFIG = _load_department_routing_config()

DEPARTMENT_RECIPIENTS = _EMAIL_CONFIG["department_recipients"]
EMAIL_SUBJECT_TEMPLATE = _EMAIL_CONFIG["email_subject_template"]
DEFAULT_DAYS_LOOKBACK = _EMAIL_CONFIG["default_days_lookback"]


@dataclass
class EmailConfig:
    smtp_host: str
    smtp_port: int
    username: str
    password: str
    from_addr: str


class EmailSummaryAgent:
    def __init__(self, db: Optional[MySQLDbService] = None, email_config: Optional[EmailConfig] = None):
        self.db = db or MySQLDbService()
        self.email_config = email_config or EmailConfig(
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USER", ""),
            password=os.getenv("SMTP_PASS", ""),
            from_addr=os.getenv("SMTP_FROM", "reports@airline.com"),
        )
        # self.summarizer = Summarizer(...)

    def _fetch_department_feedback(self, department_labels: List[str], days: int = 1) -> pd.DataFrame:
        # simplest approach: retrieve a window and filter by labels in Python
        today = date.today()
        start_date = (today - timedelta(days=days)).isoformat()
        df = self.db.get_processed_data(date_from=start_date)  # then filter by labels list

        mask = df["labels"].fillna("").apply(
            lambda s: any(lbl in s.split(",") for lbl in department_labels)
        )
        return df[mask]

    def _build_email_body(self, dept: str, df: pd.DataFrame) -> str:
        total = len(df)
        if total == 0:
            return f"No new feedback for {dept} in the selected period."

        # Simple stats (you can replace with packages/stats logic)
        label_counts = (
            df["labels"]
            .fillna("")
            .str.split(",")
            .explode()
            .str.strip()
            .value_counts()
            .to_dict()
        )

        lines = []
        lines.append(f"Daily feedback report for **{dept}**")
        lines.append("")
        lines.append(f"Total feedback items: {total}")
        lines.append("")
        lines.append("Counts by label:")
        for lbl, cnt in label_counts.items():
            if lbl:
                lines.append(f"- {lbl}: {cnt}")

        # You can sample a few raw reviews:
        sample = df["review"].head(5)
        lines.append("")
        lines.append("Sample feedback:")
        for i, text in enumerate(sample, start=1):
            lines.append(f"{i}. {text}")

        # Later: ask LLM to generate a nicer summary
        # summary = self.summarizer.summarize(df["review"].tolist())
        # lines.insert(1, f"Summary: {summary}\n")

        return "\n".join(lines)

    def _send_email(self, to_addrs: List[str], subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = self.email_config.from_addr
        msg["To"] = ", ".join(to_addrs)
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(self.email_config.smtp_host, self.email_config.smtp_port) as server:
            server.starttls()
            server.login(self.email_config.username, self.email_config.password)
            server.send_message(msg)

    def send_daily_reports(self):
        # Load department labels from configuration
        department_labels = _ROUTING_CONFIG["department_labels"]

        for dept, labels in department_labels.items():
            df = self._fetch_department_feedback(labels, days=DEFAULT_DAYS_LOOKBACK)
            body = self._build_email_body(dept, df)
            recipients = DEPARTMENT_RECIPIENTS.get(dept, [])
            if not recipients:
                continue
            self._send_email(
                to_addrs=recipients,
                subject=EMAIL_SUBJECT_TEMPLATE.format(department=dept),
                body=body,
            )
