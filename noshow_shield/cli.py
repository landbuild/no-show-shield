"""No-Show Shield CLI.

    python -m noshow_shield sync data/demo-schedule.json
    python -m noshow_shield preview --date 2026-09-11
    python -m noshow_shield run --date 2026-09-11                # mock (default)
    python -m noshow_shield run --date 2026-09-11 --live \
        --override-phone +61XXXXXXXXX                            # real CALL-E calls
    python -m noshow_shield summary --date 2026-09-11

Safety defaults: mock unless --live; --live requires CALLE_API_KEY; every live
call is metered by the ledger (cap 8 of the 20 free calls). --override-phone
routes every call of the run to one number you control — this is how the demo
is made against the operator's own phone without any real customer number ever
entering the repo.
"""
from __future__ import annotations

import argparse
import sys

from .agent import ConfirmationAgent
from .budget import CallBudget
from .calendar_store import CalendarStore
from .models import PENDING

STORE_PATH = "calendar.json"
LEDGER_PATH = "call-ledger.json"
BUSINESS = "Shorewood Plumbing (demo)"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="noshow-shield", description="Appointment-confirmation calling agent on CALL-E.")
    p.add_argument("--store", default=STORE_PATH, help="calendar store path (default: calendar.json)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("sync", help="load a schedule file into the working calendar")
    sp.add_argument("source")

    pv = sub.add_parser("preview", help="show who would be called for a date")
    pv.add_argument("--date", required=True)

    rn = sub.add_parser("run", help="place confirmation calls for a date")
    rn.add_argument("--date", required=True)
    rn.add_argument("--live", action="store_true", help="use CALL-E (requires CALLE_API_KEY); default is mock")
    rn.add_argument("--override-phone", default=None, help="E.164 number that receives ALL calls this run (demo mode)")
    rn.add_argument("--business", default=BUSINESS)

    sm = sub.add_parser("summary", help="print the operator summary for a date")
    sm.add_argument("--date", required=True)
    sm.add_argument("--business", default=BUSINESS)

    args = p.parse_args(argv)
    store = CalendarStore(args.store)

    if args.cmd == "sync":
        n = store.sync_from(args.source)
        print(f"Loaded {n} bookings into {args.store}")
        return 0

    if args.cmd == "preview":
        rows = store.bookings_for(args.date, statuses={PENDING})
        if not rows:
            print(f"No pending bookings for {args.date}.")
            return 0
        print(f"Would call for {args.date}:")
        for b in rows:
            print(f"  {b.time}  {b.customer_name:<18} {b.service:<22} {b.phone}")
        return 0

    if args.cmd == "run":
        if args.live:
            if not args.override_phone:
                print(
                    "Refusing --live without --override-phone: demo policy is that "
                    "real calls only go to a number you control.",
                    file=sys.stderr,
                )
                return 2
            from .providers import CalleProvider

            provider = CalleProvider()
            budget = CallBudget(LEDGER_PATH)
            print(f"LIVE run via CALL-E. Budget: {budget.used}/{budget.cap} used.")
        else:
            from .providers import MockProvider

            provider = MockProvider()
            budget = None
            print("Mock run (no credentials needed, no calls placed).")

        agent = ConfirmationAgent(
            store,
            provider,
            budget=budget,
            business_name=args.business,
            override_phone=args.override_phone,
        )
        report = agent.run(args.date)
        print()
        print(report.summary_text(args.business))
        return 0

    if args.cmd == "summary":
        from .agent import RunReport

        rows = store.bookings_for(args.date)
        called = [b for b in rows if b.status != PENDING]
        report = RunReport(date=args.date, attempted=called, skipped=[])
        print(report.summary_text(args.business))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
