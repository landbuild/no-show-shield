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

**What we learned.** Small result schemas extract reliably from live calls;
putting the destination number inside the task string (per the quickstart
pattern) makes number-hygiene the caller's job, so we wrapped it in E.164
validation and an override path; and a 20-call free tier forces exactly the
mock-first architecture that made the project more testable anyway.

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
