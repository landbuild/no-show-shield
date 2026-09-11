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


def humanise_when(date_str: str, time_str: str, today=None) -> str:
    """Turn an ISO date + 24h time into something a person would say aloud.

    '2026-09-12' + '09:30' (called the day before) -> 'tomorrow at 9:30 in the
    morning'. Spoken agents read ISO dates out digit by digit, which is the
    fastest way to sound like a robot.
    """
    from datetime import date as _date, datetime

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        t = datetime.strptime(time_str, "%H:%M").time()
    except (TypeError, ValueError):
        return f"on {date_str} at {time_str}"

    today = today or _date.today()
    delta = (d - today).days
    if delta == 0:
        day = "today"
    elif delta == 1:
        day = "tomorrow"
    elif 2 <= delta <= 6:
        day = f"this {d.strftime('%A')}"
    else:
        day = f"{d.strftime('%A')} the {d.day}"

    part = (
        "in the morning" if t.hour < 12
        else "in the afternoon" if t.hour < 17
        else "in the evening"
    )
    hour12 = t.hour % 12 or 12
    clock = f"{hour12}:{t.minute:02d}" if t.minute else str(hour12)
    return f"{day} at {clock} {part}"


def build_task(booking: Booking, business_name: str, target_phone: Optional[str] = None) -> str:
    """The natural-language task handed to CALL-E for one confirmation call.

    Carries explicit manner guidance as well as the procedure: the first live
    calls sounded stilted because the task said what to do and nothing about
    how to sound, and fed the model raw ISO dates.
    """
    phone = target_phone or booking.phone
    when = humanise_when(booking.date, booking.time)
    return (
        f"Call {phone} and ask for {booking.customer_name}. You are making a short "
        f"appointment-confirmation call for {business_name}, an Australian trades "
        f"business.\n\n"
        f"HOW TO SOUND\n"
        f"- Warm, brisk, human. Short sentences, contractions, everyday words. Like a "
        f"good receptionist, not someone reading a script.\n"
        f"- In your first breath, say once that you're an AI assistant calling from "
        f"{business_name}. Don't mention it again.\n"
        f"- Ask one thing, then stop and listen. Never stack two questions in a turn.\n"
        f"- Keep every turn to a sentence or two. Don't recite their answer back in full.\n"
        f"- Say the time the way a person would: \"{when}\". Never read a date as digits "
        f"or in year-month-day form.\n"
        f"- No filler pleasantries, no corporate phrasing, no apologising for existing.\n"
        f"- If they talk over you, stop and let them finish.\n\n"
        f"WHAT TO DO\n"
        f"1. Greet them, say who you are, check you're speaking with {booking.customer_name}.\n"
        f"2. Say you're confirming their {booking.service.lower()} {when}, and ask if that "
        f"still suits.\n"
        f"3. If it suits: thank them, say you'll see them then, end the call.\n"
        f"4. If they want a different time: ask what day and time would suit, say the new "
        f"preference back once so they know you caught it, and tell them {business_name} "
        f"will text to lock it in. Never promise a specific slot yourself.\n"
        f"5. If they cancel: no problem, say you'll take it out of the book, end politely.\n"
        f"6. Wrong number or asked not to call: apologise briefly, end immediately, report "
        f"the outcome as unknown with a note.\n\n"
        f"Keep the whole call under 90 seconds. Never argue and never try to talk them out "
        f"of a change."
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

        # The SDK returns a plain JSON dict (verified against calle-ai source:
        # create_and_wait -> JsonObject), not an attribute-style object. Read
        # both shapes, and probe the plausible homes for the structured verdict.
        def _get(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        structured = None
        for key in ("structured_result", "result", "structured_output", "output"):
            candidate = _get(call, key)
            if isinstance(candidate, dict) and candidate:
                structured = candidate
                break
        if structured is None:
            recips = _get(call, "recipient_results") or _get(call, "recipients") or []
            if isinstance(recips, list) and recips:
                structured = (
                    _get(recips[0], "structured_result")
                    or _get(recips[0], "result")
                    or {}
                )
        if not isinstance(structured, dict):
            structured = {}

        # Ground-truth dump for validation runs: the full raw response, so an
        # unexpected shape is diagnosable without burning another call.
        # (last-call-debug.json is gitignored.)
        try:
            import json as _json

            with open("last-call-debug.json", "w") as fh:
                _json.dump(call if isinstance(call, dict) else repr(call), fh, indent=2, default=str)
        except Exception:
            pass

        status = _STATUS_MAP.get(structured.get("confirmation_status"), UNKNOWN)
        conf = _get(call, "completion_confidence")
        score = conf.get("score") if isinstance(conf, dict) else getattr(conf, "score", None)
        return CallResult(
            status=status,
            reschedule_preference=structured.get("reschedule_preference", ""),
            notes=structured.get("notes", ""),
            call_id=_get(call, "id"),
            confidence=score,
            raw={
                "provider": "call-e",
                "status": _get(call, "status"),
                "response_keys": sorted(call.keys()) if isinstance(call, dict) else None,
            },
        )
