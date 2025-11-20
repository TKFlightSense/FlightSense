from dataclasses import dataclass
from typing import Optional, Dict, Union


@dataclass
class DataFilter:
    """Filter parameters for processed data queries."""

    limit: Optional[int] = None
    label_type: Optional[Union[str, SentimentLabel]] = None
    label_status: Optional[Union[str, StatusSuffix]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    only_without_ticket: bool = False


    def validate(self) -> Dict[str, str]:
        """Validate filter parameters and return errors if any."""
        errors = {}

        if self.limit is not None and self.limit <= 0:
            errors["limit"] = "Limit must be greater than 0"

        if self.label_type:
            if isinstance(self.label_type, str):
                try:
                    SentimentLabel[self.label_type.upper().replace("-", "_")]
                except KeyError:
                    valid_types = [label.value for label in SentimentLabel]
                    errors["label_type"] = (
                        f"Invalid label_type. Must be one of: {valid_types}"
                    )

        if self.label_status:
            if isinstance(self.label_status, str):
                try:
                    StatusSuffix[self.label_status.upper()]
                except KeyError:
                    errors["label_status"] = (
                        "Invalid label_status. Must be 'POSITIVE' or 'NEGATIVE'"
                    )

        if self.date_from and self.date_to:
            # Basic date validation (you can make this more robust)
            if self.date_from > self.date_to:
                errors["date_range"] = "date_from must be before date_to"

        return errors

    def to_enum(self) -> "DataFilter":
        """Convert string values to enums."""
        if isinstance(self.label_type, str):
            try:
                self.label_type = SentimentLabel[
                    self.label_type.upper().replace("-", "_")
                ]
            except KeyError:
                pass  # Keep as string, will be caught in validation

        if isinstance(self.label_status, str):
            try:
                self.label_status = StatusSuffix[self.label_status.upper()]
            except KeyError:
                pass  # Keep as string, will be caught in validation

        return self

    @classmethod
    def from_dict(cls, data: Dict) -> "DataFilter":
        return cls(
            limit=data.get("limit"),
            label_type=data.get("label_type"),
            label_status=data.get("label_status"),
            date_from=data.get("date_from"),
            date_to=data.get("date_to"),
            only_without_ticket=data.get("only_without_ticket", False),
        )


@dataclass
class StatisticsFilter:
    """Filter parameters for statistics queries."""

    metric_name: Optional[str] = None
    pos_source: Optional[str] = None
    limit: Optional[int] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    aggregated: bool = False

    def validate(self) -> Dict[str, str]:
        """Validate filter parameters."""
        errors = {}

        if self.limit is not None and self.limit <= 0:
            errors["limit"] = "Limit must be greater than 0"

        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                errors["date_range"] = "date_from must be before date_to"

        return errors

    @classmethod
    def from_dict(cls, data: Dict) -> "StatisticsFilter":
        """Create StatisticsFilter from dictionary."""
        return cls(
            metric_name=data.get("metric_name"),
            pos_source=data.get("pos_source"),
            limit=data.get("limit"),
            date_from=data.get("date_from"),
            date_to=data.get("date_to"),
            aggregated=data.get("aggregated", False),
        )
