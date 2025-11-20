from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class DataFilter:
    """Filter parameters for processed data queries."""

    limit: Optional[int] = None
    label_type: Optional[str] = None  # e.g. "flight_delay_cancellation" or a fine label
    date_from: Optional[str] = None   # "YYYY-MM-DD"
    date_to: Optional[str] = None     # "YYYY-MM-DD"
    only_without_ticket: bool = False

    def validate(self) -> Dict[str, str]:
        errors: Dict[str, str] = {}

        if self.limit is not None and self.limit <= 0:
            errors["limit"] = "Limit must be greater than 0"

        if self.date_from and self.date_to and self.date_from > self.date_to:
            errors["date_range"] = "date_from must be before date_to"

        return errors

    def to_enum(self) -> "DataFilter":
        """
        Previously converted strings to enums.
        Kept for backwards compatibility – now it simply returns self.
        """
        return self

    @classmethod
    def from_dict(cls, data: Dict) -> "DataFilter":
        return cls(
            limit=data.get("limit"),
            label_type=data.get("label_type"),
            date_from=data.get("date_from"),
            date_to=data.get("date_to"),
            only_without_ticket=data.get("only_without_ticket", False),
        )
