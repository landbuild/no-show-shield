# Devpost submission draft — No-Show Shield

> Paste-ready text for the CALL-E "Your Code Is Calling" submission form.
> Fields marked [NATHAN] need his values at submission time.

**Project name:** No-Show Shield

**Elevator pitch (one line):**
An agent that calls tomorrow's bookings for solo trades businesses, handles
"yes / reschedule / cancel" conversationally, and hands back an updated
calendar — no-shows caught the night before, not at the kerb.

## About the project

**What it does.** No-Show Shield reads a solo operator's bookings from a plain
JSON calendar, places a real confirmation call to each customer through
CALL-E, and understands the outcome conversationally: a "yes" marks the slot
confirmed, a reschedule request captures the customer's preferred time
verbatim, a cancellation frees the slot, and a no-answer is queued for
re-attempt. The run ends with a one-glance summary: who's locked in, and the
short list that needs the operator.

**Why it matters.** A missed appointment costs a solo tradie the entire slot
— fuel, travel time, and the job that could have filled it. Confirmation
calls work, but nobody running a one-person business has an hour each evening
to make them. This is the most boring possible use of an AI that can hold a
phone call, which is exactly why it is practical.

**How it's built.** Python on the CALL-E Python SDK (`calle-ai`). Each
booking becomes a natural-language `task` plus a JSON `result_schema`
(`confirmation_status` enum + reschedule preference + notes), so the
conversation comes back as structured data that a state machine can apply to
the calendar. The architecture is offline-first: a deterministic mock
provider stands in for telephony behind the same interface, which let the
whole pipeline be built and tested (10 automated tests) without spending the
free-tier call budget — a hard, ledger-backed call cap then meters every real
call. Safety is designed in: the agent announces itself as an AI on every
call, bails out instantly on "wrong number", and live demo calls can only be
routed to a number the operator supplies at run time — no real customer
number exists anywhere in the project.

**What we learned.** Four things, all from calls that actually happened:

1. *Correct data, wrong voice.* Our first live calls returned perfect
structured results while sounding robotic — and nothing in the API would have
told us, because CALL-E exposes a summary and evidence but no transcript. We
only caught it because a human was holding the phone. If the call quality
matters, put a person on the far end before you ship.
2. *Never pass ISO dates to a spoken agent.* We were interpolating
"2026-09-12 at 09:30" into the task; the agent read it out digit by digit.
Rendering "tomorrow at 9:30 in the morning" before the string reaches the
model fixed it instantly.
3. *A task needs manner, not just procedure.* The original prompt said what to
do and nothing about how to sound. Adding an explicit block — short turns, one
question at a time, disclose the AI once up front, yield if interrupted — did
more for call quality than any schema change.
4. *First-call latency is real.* The first call of a session took roughly four
minutes between `create` and the phone ringing; later calls connected in
seconds. There is no queued/dialing state to distinguish "waiting" from
"broken", which matters when a run blocks on it.

Small result schemas extract reliably; putting the destination number inside
the task string (per the quickstart pattern) makes number-hygiene the caller's
job, so we wrapped it in E.164 validation and an override path; and a 20-call
free tier forces exactly the mock-first architecture that made the project
more testable anyway.

**What's honestly not in it.** No SMS send-back, no calendar-platform
integrations, no retry scheduler — a JSON file in, an updated JSON file and a
summary out. Scope was chosen so that everything present works end-to-end.

**AI usage (voluntary disclosure).** Built with AI coding assistants
(Anthropic Claude) under the direction of the entrant. Pre-existing work
incorporated: the CALL-E SDK and the Python standard library.

## Form fields

- **Demo video URL:** https://youtu.be/hOCdDwYFgmU
- **Pull request URL:** https://github.com/CALLE-AI/awesome-phone-call-agents/pull/483
- **CALL-E account email:** [the Gmail you created for the CALL-E platform]
- **Demo app URL (optional):** leave blank (local CLI project)
- **Built with:** python, call-e, calle-ai

- **Source repo:** https://github.com/landbuild/no-show-shield
