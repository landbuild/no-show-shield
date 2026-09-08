"""The confirmation run: call every pending booking for a date, apply results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .budget import BudgetExceeded, CallBudget
from .calendar_store import CalendarStore
from .models import (
    CALL_FAILED,
    CONFIRMED,
    CANCELLED,
    NO_ANSWER,
    PENDING,
    RESCHEDULE,
    UNKNOWN,
    Booking,
    valid_e164,
)
from .providers import build_task


@dataclass
class RunReport:
    date: str
    attempted: List[Booking]
    skipped: List[tuple]  # (booking, reason)

    def summary_text(self, business_name: str) -> str:
        lines = [f"{business_name} — confirmation run for {self.date}", "-" * 46]
        counts: dict = {}
        for b in self.attempted:
            counts[b.status] = counts.get(b.status, 0) + 1
            line = f"{b.time}  {b.customer_name:<18} {b.service:<22} -> {b.status}"
            if b.status == RESCHEDULE and b.reschedule_preference:
                line += f"  (wants: {b.reschedule_preference})"
            lines.append(line)
        for b, reason in self.skipped:
            lines.append(f"{b.time}  {b.customer_name:<18} {b.service:<22} -> SKIPPED ({reason})")
        lines.append("-" * 46)
        follow_up = [
            b for b in self.attempted
            if b.status in (RESCHEDULE, NO_ANSWER, UNKNOWN, CALL_FAILED)
        ]
        lines.append(
            "Totals: "
            + ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
            + (f"; skipped={len(self.skipped)}" if self.skipped else "")
        )
        if follow_up:
            lines.append("Needs you: " + ", ".join(b.customer_name for b in follow_up))
        else:
            lines.append("Needs you: nothing — book is clean.")
        return "\n".join(lines)


class ConfirmationAgent:
    def __init__(
        self,
        store: CalendarStore,
        provider,
        budget: Optional[CallBudget] = None,
        business_name: str = "the business",
        override_phone: Optional[str] = None,
    ):
        self.store = store
        self.provider = provider
        self.budget = budget
        self.business_name = business_name
        self.override_phone = override_phone
        if override_phone and not valid_e164(override_phone):
            raise ValueError(f"--override-phone must be E.164, got {override_phone!r}")

    def run(self, date: str) -> RunReport:
        attempted: List[Booking] = []
        skipped: List[tuple] = []
        for booking in self.store.bookings_for(date, statuses={PENDING, NO_ANSWER}):
            target = self.override_phone or booking.phone
            if not valid_e164(target):
                skipped.append((booking, f"invalid phone {booking.phone!r}"))
                continue
            if self.budget is not None:
                try:
                    self.budget.check()
                except BudgetExceeded as exc:
                    skipped.append((booking, str(exc)))
                    continue
                self.budget.record(booking.booking_id, note=self.provider.name)
            task = build_task(booking, self.business_name, self.override_phone)
            result = self.provider.place_call(booking, task)
            booking.status = result.status
            booking.reschedule_preference = result.reschedule_preference
            booking.notes = result.notes
            booking.call_id = result.call_id
            self.store.update(booking)
            attempted.append(booking)
        return RunReport(date=date, attempted=attempted, skipped=skipped)
