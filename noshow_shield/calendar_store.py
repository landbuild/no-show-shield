"""JSON-file calendar store.

Deliberately boring: a single JSON file the operator can read and edit by hand.
The demo schedule ships in data/demo-schedule.json; `sync` copies it into the
working store so demo source data is never mutated.
"""
from __future__ import annotations

import json
import os
import tempfile
from typing import List, Optional

from .models import Booking


class CalendarStore:
    def __init__(self, path: str):
        self.path = path
        self._bookings: List[Booking] = []
        if os.path.exists(path):
            self._load()

    def _load(self) -> None:
        with open(self.path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self._bookings = [Booking.from_dict(b) for b in payload.get("bookings", [])]

    def save(self) -> None:
        payload = {"bookings": [b.to_dict() for b in self._bookings]}
        # Atomic write: never leave a half-written calendar behind.
        d = os.path.dirname(os.path.abspath(self.path)) or "."
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def sync_from(self, source_path: str) -> int:
        with open(source_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self._bookings = [Booking.from_dict(b) for b in payload.get("bookings", [])]
        self.save()
        return len(self._bookings)

    def bookings_for(self, date: str, statuses: Optional[set] = None) -> List[Booking]:
        rows = [b for b in self._bookings if b.date == date]
        if statuses is not None:
            rows = [b for b in rows if b.status in statuses]
        return sorted(rows, key=lambda b: b.time)

    def all_bookings(self) -> List[Booking]:
        return list(self._bookings)

    def get(self, booking_id: str) -> Optional[Booking]:
        for b in self._bookings:
            if b.booking_id == booking_id:
                return b
        return None

    def update(self, booking: Booking) -> None:
        for i, b in enumerate(self._bookings):
            if b.booking_id == booking.booking_id:
                self._bookings[i] = booking
                self.save()
                return
        raise KeyError(f"booking {booking.booking_id} not in store")
