"""
history.py — Calculation history management and CSV export.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime

from constants import HISTORY_MAX
from trig_engine import TrigResult


@dataclass
class HistoryEntry:
    """A single history record."""
    timestamp: str
    ratio: str
    angle_str: str          # e.g. "31°"
    unit: str
    degrees: float
    radians: float
    gradians: float
    value: str              # decimal or "Undefined"
    exact_value: str | None

    def short_label(self) -> str:
        """One-line summary, e.g. 'sin(31°) = 0.515038074910'."""
        sym = self.ratio.lower()
        return f"{sym}({self.angle_str}) = {self.value}"

    def full_text(self) -> str:
        """Multi-line copy block."""
        lines = [
            f"Ratio     : {self.ratio}",
            f"Angle     : {self.angle_str}",
            f"Degrees   : {self.degrees:.8f}°",
            f"Radians   : {self.radians:.8f}",
            f"Gradians  : {self.gradians:.8f}",
            f"Value     : {self.value}",
        ]
        if self.exact_value:
            lines.append(f"Exact     : {self.exact_value}")
        lines.append(f"Timestamp : {self.timestamp}")
        return "\n".join(lines)


class HistoryManager:
    """Thread-safe (GIL is enough for a single-threaded Tk app) history store."""

    def __init__(self) -> None:
        self._entries: list[HistoryEntry] = []

    # ── Write ─────────────────────────────────────────────────────────────────

    def push(self, result: TrigResult) -> None:
        """Add a new entry from a :class:`TrigResult`. Caps at HISTORY_MAX."""
        deg = result.degrees
        angle_str = f"{deg:.6g}°"

        entry = HistoryEntry(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            ratio=result.ratio,
            angle_str=angle_str,
            unit=result.input_unit,
            degrees=result.degrees,
            radians=result.radians,
            gradians=result.gradians,
            value=result.value,
            exact_value=result.exact_value,
        )

        # Avoid identical consecutive duplicates (live-typing produces many).
        if self._entries and self._same(self._entries[0], entry):
            return

        self._entries.insert(0, entry)
        if len(self._entries) > HISTORY_MAX:
            self._entries = self._entries[:HISTORY_MAX]

    def clear(self) -> None:
        self._entries.clear()

    # ── Read ──────────────────────────────────────────────────────────────────

    @property
    def entries(self) -> list[HistoryEntry]:
        return self._entries

    def search(self, query: str) -> list[HistoryEntry]:
        """Return entries whose short_label contains *query* (case-insensitive)."""
        q = query.strip().lower()
        if not q:
            return self._entries
        return [e for e in self._entries if q in e.short_label().lower()]

    # ── Export ────────────────────────────────────────────────────────────────

    def to_csv_string(self) -> str:
        """Return the history as a CSV string (UTF-8)."""
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "Timestamp", "Ratio", "Angle", "Degrees", "Radians",
            "Gradians", "Value", "Exact Value",
        ])
        for e in self._entries:
            writer.writerow([
                e.timestamp, e.ratio, e.angle_str,
                f"{e.degrees:.8f}", f"{e.radians:.8f}", f"{e.gradians:.8f}",
                e.value, e.exact_value or "",
            ])
        return buf.getvalue()

    def export_csv(self, filepath: str) -> None:
        """Write the history to *filepath* as a CSV file."""
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write(self.to_csv_string())

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _same(a: HistoryEntry, b: HistoryEntry) -> bool:
        return (
            a.ratio == b.ratio
            and abs(a.degrees - b.degrees) < 1e-9
            and a.value == b.value
        )
