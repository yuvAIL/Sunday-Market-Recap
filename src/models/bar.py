from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Optional


@dataclass(frozen=True)
class OHLCVBar:
    symbol: str
    asset_class: str
    provider: str
    provider_symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float]
    adjusted_close: Optional[float]
    currency: Optional[str]
    fetched_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
