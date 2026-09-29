from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from src.models.bar import OHLCVBar


class BaseClient(ABC):
    provider_name: str

    @abstractmethod
    def fetch_daily_bars(
        self,
        *,
        canonical_symbol: str,
        provider_symbol: str,
        asset_class: str,
        currency: str | None,
        start: date,
        end: date,
    ) -> list[OHLCVBar]:
        """Fetch normalized daily bars for one symbol and date range."""
        raise NotImplementedError
