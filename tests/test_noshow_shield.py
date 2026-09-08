"""Offline test suite — runs with stdlib unittest, no SDK, no network."""
import json
import os
import tempfile
import unittest

from noshow_shield.agent import ConfirmationAgent
from noshow_shield.budget import BudgetExceeded, CallBudget
from noshow_shield.calendar_store import CalendarStore
from noshow_shield.models import (
    CONFIRMED,
    NO_ANSWER,
    PENDING,
    RESCHEDULE,
    Booking,
    valid_e164,
)
from noshow_shield.providers import MockProvider, build_task


def make_store(tmpdir, bookings):
    path = os.path.join(tmpdir, "calendar.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"bookings": [b.to_dict() for b in bookings]}, f)
    return CalendarStore(path)


def booking(i, scenario="confirm", **kw):
    defaults = dict(
        booking_id=f"bk-{i:03d}",
        customer_name=f"Customer {i}",
        phone="+61491570156",
        date="2026-09-11",
        time=f"{8 + i:02d}:00",
        service="Demo service",
        mock_scenario=scenario,
    )
    defaults.update(kw)
    return Booking(**defaults)


class TestModels(unittest.TestCase):
    def test_e164(self):
        self.assertTrue(valid_e164("+61491570156"))
        self.assertFalse(valid_e164("0491570156"))
        self.assertFalse(valid_e164("+0491570156"))
        self.assertFalse(valid_e164(""))

    def test_task_never_contains_calendar_number_when_overridden(self):
        b = booking(1, phone="+61491570156")
        task = build_task(b, "Acme", target_phone="+61400000000")
        self.assertNotIn("+61491570156", task)
        self.assertIn("+61400000000", task)
        self.assertIn("AI assistant", task)


class TestStore(unittest.TestCase):
    def test_roundtrip_and_update(self):
        with tempfile.TemporaryDirectory() as d:
            store = make_store(d, [booking(1), booking(2)])
            rows = store.bookings_for("2026-09-11")
            self.assertEqual(len(rows), 2)
            rows[0].status = CONFIRMED
            store.update(rows[0])
            reloaded = CalendarStore(store.path)
            self.assertEqual(reloaded.get("bk-001").status, CONFIRMED)

    def test_sync_copies_source(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "src.json")
            with open(src, "w", encoding="utf-8") as f:
                json.dump({"bookings": [booking(7).to_dict()]}, f)
            store = CalendarStore(os.path.join(d, "cal.json"))
            self.assertEqual(store.sync_from(src), 1)
            self.assertEqual(store.get("bk-007").status, PENDING)


class TestAgentRun(unittest.TestCase):
    def test_mock_run_applies_scenarios(self):
        with tempfile.TemporaryDirectory() as d:
            store = make_store(
                d,
                [
                    booking(1, "confirm"),
                    booking(2, "reschedule"),
                    booking(3, "no_answer"),
                ],
            )
            agent = ConfirmationAgent(store, MockProvider(), business_name="Acme")
            report = agent.run("2026-09-11")
            self.assertEqual(len(report.attempted), 3)
            self.assertEqual(store.get("bk-001").status, CONFIRMED)
            self.assertEqual(store.get("bk-002").status, RESCHEDULE)
            self.assertTrue(store.get("bk-002").reschedule_preference)
            self.assertEqual(store.get("bk-003").status, NO_ANSWER)
            text = report.summary_text("Acme")
            self.assertIn("Needs you:", text)
            self.assertIn("Customer 2", text)

    def test_invalid_phone_is_skipped_not_fatal(self):
        with tempfile.TemporaryDirectory() as d:
            store = make_store(d, [booking(1, phone="not-a-number"), booking(2)])
            agent = ConfirmationAgent(store, MockProvider())
            report = agent.run("2026-09-11")
            self.assertEqual(len(report.attempted), 1)
            self.assertEqual(len(report.skipped), 1)

    def test_confirmed_bookings_not_recalled(self):
        with tempfile.TemporaryDirectory() as d:
            store = make_store(d, [booking(1, status=CONFIRMED), booking(2)])
            agent = ConfirmationAgent(store, MockProvider())
            report = agent.run("2026-09-11")
            self.assertEqual([b.booking_id for b in report.attempted], ["bk-002"])

    def test_override_phone_must_be_e164(self):
        with tempfile.TemporaryDirectory() as d:
            store = make_store(d, [booking(1)])
            with self.assertRaises(ValueError):
                ConfirmationAgent(store, MockProvider(), override_phone="0491570156")


class TestBudget(unittest.TestCase):
    def test_budget_blocks_at_cap(self):
        with tempfile.TemporaryDirectory() as d:
            budget = CallBudget(os.path.join(d, "ledger.json"), cap=2)
            budget.check()
            budget.record("bk-001")
            budget.record("bk-002")
            self.assertEqual(budget.remaining, 0)
            with self.assertRaises(BudgetExceeded):
                budget.check()

    def test_agent_skips_when_budget_gone(self):
        with tempfile.TemporaryDirectory() as d:
            store = make_store(d, [booking(1), booking(2), booking(3)])
            budget = CallBudget(os.path.join(d, "ledger.json"), cap=2)
            agent = ConfirmationAgent(store, MockProvider(), budget=budget)
            report = agent.run("2026-09-11")
            self.assertEqual(len(report.attempted), 2)
            self.assertEqual(len(report.skipped), 1)
            self.assertIn("budget", report.skipped[0][1].lower())


if __name__ == "__main__":
    unittest.main()
