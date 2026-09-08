# Demo video — beat sheet

**Rules constraints (verified 2026-09-08):** video must be **under 3 minutes**,
public on YouTube/Vimeo, and "should include footage that shows the Project
functioning on the device for which it was built" — for a phone-call agent,
that is a phone on camera receiving the live call. No copyrighted
music/material. Narration not required; captions suffice (Nathan may voice it
if he prefers — either is compliant).

**Set-up before recording:** terminal with repo open, `calendar.json` synced
from the demo schedule, Nathan's handset on the desk in frame, ledger showing
budget headroom. One full rehearsal live run first (uses 1–2 calls), then
record. Reserve: never exceed 6 real calls across rehearsal + takes.

Total target 2:40 — leaves 20s safety margin under the 3:00 limit.

| Beat | Time | On screen | Caption / voice line |
|---|---|---|---|
| 1. The problem | 0:00–0:15 | Title card + a booking sheet with a struck-out row | "Every no-show costs a solo tradie the whole slot. No-Show Shield calls tomorrow's bookings for you." |
| 2. The schedule | 0:15–0:35 | `python3 -m noshow_shield preview --date <demo date>` — 5 bookings listed | "Tomorrow's book, straight from a plain JSON calendar. These are fictional numbers — the live call goes to my own phone." |
| 3. Launch the run | 0:35–0:50 | `run --date <demo date> --live --override-phone +61…` typed and entered; budget line visible | "One command. Every call is metered against the free tier by a hard budget guard." |
| 4. THE MONEY SHOT | 0:50–1:50 | Phone rings on camera; Nathan answers on speaker; agent self-identifies as AI, confirms the appointment; Nathan asks to reschedule to Thursday afternoon | Live audio, captioned. This beat is the demo — do not trim it. |
| 5. Structured outcome | 1:50–2:15 | Terminal: run report showing `reschedule_requested (wants: Thursday afternoon…)` written back; `cat calendar.json` snippet | "The conversation came back as structured data and the calendar updated itself." |
| 6. Operator summary | 2:15–2:30 | `summary --date <demo date>` — totals + "Needs you: …" line | "One glance: who's confirmed, who needs a callback." |
| 7. Close | 2:30–2:40 | Repo + architecture diagram card | "Built on CALL-E's Python SDK. Repo, tests, and honest limits in the README." |

**Contingencies:**
- Call drops / ASR mangles the reschedule: stop, re-run (budget allows 3
  recorded attempts). Do not splice mid-beat — the device beat should be one
  continuous take so it reads as live.
- If live latency pushes past 3:00, trim beats 1 and 7, never beat 4.
- If the agent mishears, leave it in if the structured result is still
  correct — recovery is more convincing than perfection.
