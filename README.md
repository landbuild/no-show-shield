# No-Show Shield

An appointment-confirmation calling agent for solo trades and service
businesses, built on [CALL-E](https://www.heycall-e.com/). It reads tomorrow's
bookings from a plain JSON calendar, places a real confirmation call to each
customer, understands "yes / reschedule / cancel" conversationally, writes the
outcome back to the calendar, and hands the operator a one-glance summary of
exactly which slots need attention.

No-shows are a quantifiable cost for every solo operator. This closes the gap
with one command a day.

## What it honestly is (and is not)

**Working now, offline, no account needed:**
- Full pipeline: schedule sync -> preview -> confirmation run -> operator summary
- Deterministic mock call provider (scenario-driven), so every path —
  confirmed, reschedule with preference capture, cancel, no-answer, invalid
  number, budget refusal — is testable and tested (10 offline tests)
- Hard call-budget ledger and E.164 validation

**Working with a CALL-E account (`CALLE_API_KEY`):**
- Real outbound calls via the CALL-E Python SDK (`calle-ai`), structured
  results via `result_schema`, mapped into the same pipeline

**Not built (deliberately, for scope honesty):**
- No SMS send-back (the summary is printed/written to file; SMS is a roadmap item)
- No calendar-platform integrations (JSON file in, JSON file out)
- No retry scheduler — re-running the command re-attempts `no_answer` bookings
- The live path is code-complete but exercised against the SDK only after
  account connection; the mock provider is the tested reference behavior

## Spin-up

```bash
# 1. No dependencies needed for mock mode (Python 3.10+, stdlib only)
python3 -m unittest discover -s tests        # run the test suite

# 2. Load the demo schedule and run offline
python3 -m noshow_shield sync data/demo-schedule.json
python3 -m noshow_shield preview --date 2026-09-11
python3 -m noshow_shield run --date 2026-09-11          # mock, no calls placed

# 3. Live mode (requires a CALL-E account, 20 free calls on signup)
pip install calle-ai
export CALLE_API_KEY="..."                   # from dashboard.heycall-e.com
python3 -m noshow_shield run --date 2026-09-11 --live \
    --override-phone +61XXXXXXXXX            # ALL calls go to this number
```

## Safety and privacy posture

- **Live calls only ever go to a number the operator supplies at run time**
  (`--override-phone`, mandatory with `--live`). No real phone number exists
  anywhere in this repository; the demo dataset uses ACMA-reserved fictional
  Australian numbers.
- The agent announces itself as an AI assistant at the start of every call,
  never argues, hangs up immediately on "wrong number / don't call me", and
  keeps calls under 90 seconds by instruction.
- A ledger-backed budget guard caps real calls (default 8) below the free
  tier (20) with no override flag — exhaustion degrades to skips, never spend.

## Architecture

```
data/demo-schedule.json --sync--> calendar.json (CalendarStore)
                                        |
                       ConfirmationAgent.run(date)
                       |        |         |
                  CallBudget  build_task  provider
                  (ledger,    (call       ├── MockProvider (offline, deterministic)
                   hard cap)   script)    └── CalleProvider (calle-ai SDK,
                                               result_schema -> structured outcome)
                                        |
                          outcome written back to calendar.json
                                        |
                          RunReport.summary_text() -> operator
```

## AI usage

Built with AI coding assistants (Anthropic Claude) under the direction of the
entrant. See [AI-DISCLOSURE.md](AI-DISCLOSURE.md). Pre-existing work
incorporated: the CALL-E SDK and Python standard library only.
