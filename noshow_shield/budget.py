"""Hard call-budget guard.

The CALL-E free tier is 20 calls. That is the binding constraint of this build:
dev iteration runs against the mock provider only, and every *real* call is
recorded in a ledger before it is placed. The guard refuses to place a call
that would exceed the configured cap — there is no override flag by design.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

DEFAULT_CAP = 14  # of the 20 free calls; raised from 8 on 2026-09-11 for the recording session (6 still reserved)


class BudgetExceeded(RuntimeError):
    pass


class CallBudget:
    def __init__(self, ledger_path: str, cap: int = DEFAULT_CAP):
        self.ledger_path = ledger_path
        self.cap = cap

    def _entries(self) -> list:
        if not os.path.exists(self.ledger_path):
            return []
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            return json.load(f).get("calls", [])

    @property
    def used(self) -> int:
        return len(self._entries())

    @property
    def remaining(self) -> int:
        return max(0, self.cap - self.used)

    def check(self) -> None:
        if self.used >= self.cap:
            raise BudgetExceeded(
                f"Real-call budget exhausted ({self.used}/{self.cap}). "
                "Raise the cap deliberately in config, or keep using --mock."
            )

    def record(self, booking_id: str, note: str = "") -> None:
        entries = self._entries()
        entries.append(
            {
                "booking_id": booking_id,
                "at": datetime.now(timezone.utc).isoformat(),
                "note": note,
            }
        )
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump({"calls": entries}, f, indent=2)
