from __future__ import annotations

from dataclasses import dataclass

from src.config.loader import AppConfig


@dataclass(frozen=True)
class SymbolEntry:
    canonical: str
    provider_symbol: str
    group: str
    asset_class: str
    currency: str | None


class SymbolRegistry:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._entries: list[SymbolEntry] = []

        for group_name, group_data in config.groups.items():
            asset_class = str(group_data.get("asset_class", group_name))
            group_currency = group_data.get("currency")
            for ticker in group_data.get("tickers", []):
                canonical = str(ticker["canonical"])
                provider_symbol = str(ticker.get(config.provider, canonical))
                currency = ticker.get("currency", group_currency)
                self._entries.append(
                    SymbolEntry(
                        canonical=canonical,
                        provider_symbol=provider_symbol,
                        group=group_name,
                        asset_class=asset_class,
                        currency=currency,
                    )
                )

    def groups(self) -> list[str]:
        return list(self.config.groups.keys())

    def all(self) -> list[SymbolEntry]:
        return list(self._entries)

    def for_group(self, group: str) -> list[SymbolEntry]:
        if group not in self.config.groups:
            raise ValueError(f"Unknown group '{group}'. Available: {', '.join(self.groups())}")
        return [entry for entry in self._entries if entry.group == group]

    def for_symbol(self, symbol: str) -> SymbolEntry:
        target = symbol.upper()
        for entry in self._entries:
            if entry.canonical.upper() == target:
                return entry
        raise ValueError(f"Unknown symbol '{symbol}'.")
