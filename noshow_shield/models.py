"""Data models for No-Show Shield."""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Optional

# Booking lifecycle statuses.
PENDING = "pending"                # not yet called
CONFIRMED = "confirmed"            # customer said yes
RESCHEDULE = "reschedule_requested"
CANCELLED = "cancelled"
NO_ANSWER = "no_answer"
UNKNOWN = "unknown"                # call happened, outcome unclear
CALL_FAILED = "call_failed"        # provider error / budget refusal

TERMINAL = {CONFIRMED, CANCELLED}
CALL_OUTCOMES = {CONFIRMED, RESCHEDULE, CANCELLED, NO_ANSWER, UNKNOWN}

E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")


def valid_e164(number: str) -> bool:
    return bool(E164_RE.match(number or ""))


@dataclass
class Booking:
    """One appointment row from the operator's schedule."""

    booking_id: str
    customer_name: str
    phone: str                      # E.164; demo data uses ACMA fictional numbers
    date: str                       # YYYY-MM-DD (local)
    time: str                       # HH:MM (local, 24h)
    service: str
    status: str = PENDING
    reschedule_preference: str = ""
    notes: str = ""
    call_id: Optional[str] = None
    # Demo/mock only: forces a MockProvider outcome. Ignored by the live provider.
    mock_scenario: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Booking":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass
class CallResult:
    """Normalised result of one confirmation call, provider-agnostic."""

    status: str                     # one of CALL_OUTCOMES or CALL_FAILED
    reschedule_preference: str = ""
    notes: str = ""
    call_id: Optional[str] = None
    confidence: Optional[float] = None
    raw: dict = field(default_factory=dict)
