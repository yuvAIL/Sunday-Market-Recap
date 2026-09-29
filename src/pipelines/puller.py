from __future__ import annotations

import logging
from datetime import date

from src.clients.base import BaseClient
from src.config.loader import AppConfig
from src.config.symbols import SymbolEntry, SymbolRegistry
from src.storage.local import LocalStorage

logger = logging.getLogger(__name__)


class DataPuller:
    def __init__(self, config: AppConfig, client: BaseClient) -> None:
        self.config = config
        self.client = client
        self.registry = SymbolRegistry(config)
        self.storage = LocalStorage(config.output_dir)

    def _select(self, group: str | None, symbol: str | None) -> list[SymbolEntry]:
        if group and symbol:
            raise ValueError("Use either --group or --symbol, not both.")
        if symbol:
            return [self.registry.for_symbol(symbol)]
        if group:
            return self.registry.for_group(group)
        return self.registry.all()

    def run(
        self,
        *,
        start: date | None = None,
        end: date | None = None,
        group: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, int]:
        start = start or date.fromisoformat(self.config.default_start)
        end = end or date.today()
        if start > end:
            raise ValueError("Start date must be on or before end date.")

        selected = self._select(group, symbol)
        summary = {"symbols": len(selected), "updated": 0, "skipped": 0, "failed": 0}

        for entry in selected:
            try:
                gaps = self.storage.missing_ranges(entry.group, entry.canonical, start, end)
                if not gaps:
                    logger.info("%s is already up to date", entry.canonical)
                    summary["skipped"] += 1
                    continue

                pulled = []
                for gap_start, gap_end in gaps:
                    logger.info(
                        "Fetching %s (%s) %s → %s",
                        entry.canonical,
                        entry.provider_symbol,
                        gap_start,
                        gap_end,
                    )
                    pulled.extend(
                        self.client.fetch_daily_bars(
                            canonical_symbol=entry.canonical,
                            provider_symbol=entry.provider_symbol,
                            asset_class=entry.asset_class,
                            currency=entry.currency,
                            start=gap_start,
                            end=gap_end,
                        )
                    )

                path = self.storage.upsert(entry.group, entry.canonical, pulled)
                logger.info("Saved %d bars to %s", len(pulled), path)
                summary["updated"] += 1
            except Exception:
                logger.exception("Failed to update %s", entry.canonical)
                summary["failed"] += 1

        logger.info("Run summary: %s", summary)
        return summary
