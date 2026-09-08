"""Call providers: CALL-E (live) and Mock (offline dev/demo).

The agent only ever sees `CallResult`, so everything except this module runs
identically with or without platform credentials.
"""
from __future__ import annotations

import os
from typing import Optional

from .models import (
    CANCELLED,
    CALL_FAILED,
    CONFIRMED,
    NO_ANSWER,
    RESCHEDULE,
    UNKNOWN,
    Booking,
    CallResult,
)

RESULT_SCHEMA = {
    "type": "object",
    "required": ["confirmation_status"],
    "properties": {
        "confirmation_status": {
            "type": "string",
            "enum": [
                "confirmed",
                "reschedule_requested",
                "cancelled",
                "no_answer",
                "unknown",
            ],
        },
        "reschedule_preference": {
            "type": "string",
            "description": "Customer's preferred alternative day/time, verbatim, if they asked to reschedule.",
        },
        "notes": {
            "type": "string",
            "description": "One-sentence summary of anything else the customer said that the operator should know.",
        },
    },
}


def build_task(booking: Booking, business_name: str, target_phone: Optional[str] = None) -> str:
    """The natural-language task handed to CALL-E for one confirmation call."""
    phone = target_phone or booking.phone
    return (
        f"Call {phone}. You are an automated assistant calling on behalf of "
        f"{business_name}. Say clearly at the start that you are an AI assistant "
        f"making a quick appointment confirmation call. "
        f"Ask for {booking.customer_name}, and confirm their appointment for "
        f"{booking.service} on {booking.date} at {booking.time}. "
        f"If they confirm, thank them and end the call. "
        f"If they want to reschedule, ask for their preferred day and time and "
        f"tell them {business_name} will text to lock it in — do not promise a "
        f"specific new slot yourself. "
        f"If they cancel, acknowledge politely and end the call. "
        f"If the person says it is a wrong number or asks not to be called, "
        f"apologise, end the call immediately, and report the outcome as unknown "
        f"with a note. Keep the whole call under 90 seconds and never argue."
    )


class MockProvider:
    """Deterministic offline provider.

    Uses booking.mock_scenario when present, else derives a stable outcome from
    the booking id, so demo runs are reproducible without credentials.
    """

    name = "mock"

    _SCENARIOS = {
        "confirm": CallResult(CONFIRMED, notes="Customer confirmed, no changes."),
        "reschedule": CallResult(
            RESCHEDULE,
            reschedule_preference="Thursday afternoon, after 2pm",
            notes="Customer asked to move the appointment.",
        ),
        "cancel": CallResult(CANCELLED, notes="Customer cancelled outright."),
        "no_answer": CallResult(NO_ANSWER, notes="Rang out; no voicemail left."),
        "unknown": CallResult(UNKNOWN, notes="Line answered but outcome unclear."),
    }
    _ROTATION = ["confirm", "reschedule", "confirm", "no_answer", "cancel"]

    def place_call(self, booking: Booking, task: str) -> CallResult:
        key = booking.mock_scenario
        if key not in self._SCENARIOS:
            key = self._ROTATION[sum(booking.booking_id.encode()) % len(self._ROTATION)]
        base = self._SCENARIOS[key]
        return CallResult(
            status=base.status,
            reschedule_preference=base.reschedule_preference,
            notes=base.notes,
            call_id=f"mock-{booking.booking_id}",
            confidence=1.0,
            raw={"provider": "mock", "scenario": key, "task": task},
        )


class CalleProvider:
    """Live CALL-E provider (Python SDK: `pip install calle-ai`).

    Requires CALLE_API_KEY in the environment. Import is lazy so the rest of
    the project runs with no SDK installed.
    """

    name = "call-e"

    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.environ.get("CALLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "CALLE_API_KEY is not set. See docs/NATHAN-CONNECT.md — "
                "until then, run with --mock."
            )
        from calle import CalleClient  # lazy: only needed for live calls

        self._client = CalleClient(api_key=api_key)

    def place_call(self, booking: Booking, task: str) -> CallResult:
        _STATUS_MAP = {
            "confirmed": CONFIRMED,
            "reschedule_requested": RESCHEDULE,
            "cancelled": CANCELLED,
            "no_answer": NO_ANSWER,
            "unknown": UNKNOWN,
        }
        try:
            call = self._client.calls.create_and_wait(
                task=task,
                result_schema=RESULT_SCHEMA,
            )
        except Exception as exc:  # provider/network failure must never crash a run
            return CallResult(CALL_FAILED, notes=f"provider error: {exc}")

        structured = getattr(call, "structured_result", None) or {}
        status = _STATUS_MAP.get(structured.get("confirmation_status"), UNKNOWN)
        confidence = getattr(call, "completion_confidence", None)
        score = getattr(confidence, "score", None) if confidence else None
        return CallResult(
            status=status,
            reschedule_preference=structured.get("reschedule_preference", ""),
            notes=structured.get("notes", ""),
            call_id=getattr(call, "id", None),
            confidence=score,
            raw={"provider": "call-e", "status": getattr(call, "status", None)},
        )
