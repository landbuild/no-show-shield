# no-show-shield

Appointment-confirmation calling skill: reads a day's bookings from a JSON
calendar, places a CALL-E confirmation call per booking with a structured
result schema (`confirmed / reschedule_requested / cancelled / no_answer /
unknown`), writes outcomes back to the calendar, and emits an operator
summary of the slots that need attention.

Source project: https://github.com/landbuild/no-show-shield
Hackathon entry for CALL-E "Your Code Is Calling".

## Setup

```bash
pip install calle-ai
export CALLE_API_KEY="..."        # dashboard.heycall-e.com -> API keys
git clone https://github.com/landbuild/no-show-shield
cd no-show-shield
python3 -m noshow_shield sync data/demo-schedule.json
```

## Usage

```bash
python3 -m noshow_shield preview --date 2026-09-11     # who would be called
python3 -m noshow_shield run --date 2026-09-11         # offline mock run
python3 -m noshow_shield run --date 2026-09-11 --live \
    --override-phone +61XXXXXXXXX                      # real calls, one target number
python3 -m noshow_shield summary --date 2026-09-11
```

All sample phone numbers are fictional (ACMA-reserved +61 491 570 xxx range).
`--override-phone` routes every live call of a run to a single number you
control, for testing and demos.

## Side effects

- Places outbound phone calls when run with `--live` (and only then).
- Writes booking outcomes to the local `calendar.json` and appends every
  real call to `call-ledger.json`.
- No network activity at all in the default mock mode.

## Cancellation behavior

- A ledger-backed budget guard (default cap 8 calls) refuses further live
  calls once the cap is reached — remaining bookings are reported as skipped,
  and the run completes cleanly.
- The call task instructs the agent to end the call immediately and record
  `unknown` if the callee reports a wrong number or asks not to be called.
- Interrupting the process between calls loses nothing: outcomes are written
  back per booking (atomic file replace), and confirmed/cancelled bookings
  are never re-called on the next run.
