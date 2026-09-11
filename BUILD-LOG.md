# Build log — No-Show Shield (C1)

Honest, dated record of the build. This log is also the raw material for the
C2 "Most Valuable Feedback" survey draft (`C2-FEEDBACK-DRAFT.md`).

## 2026-09-08 — session 1 (contest re-verification + core build)

### Rules re-verification (live fetch, call-e.devpost.com + /rules)
- Contest OPEN. Deadline **Sep 14, 2026, 11:45 PM SGT** — the rules page reads
  PM, not the AM of our Aug 13 pessimistic note. We keep the internal
  Sep 12 freeze regardless; the extra 12 hours is buffer, not plan.
- Australia eligible (exclusions verbatim: Brazil, Quebec, Russia, Crimea,
  Cuba, Iran, North Korea + OFAC). Prizes are USD cash (+ platform credits).
- **Most Valuable Feedback**: $200 × 5, requires Devpost registration + the
  CALL-E Feedback Survey, submitted during the **Feedback Period: Jul 23,
  2026 9:30 PM SGT – Sep 18, 2026 11:45 PM SGT**. One submission per entrant.
  The open item from doc 25 §5.2 is now closed: the period is live and
  outlasts the main deadline by 4 days.
- Submission artifacts: PR to `CALLE-AI/awesome-phone-call-agents` (the repo's
  Contribution Areas explicitly list "appointment confirmation" under
  `skills/` — our concept is on-list), <3-min public video showing the project
  "functioning on the device", CALL-E account email; demo URL optional.
- Rules silent on AI usage; voluntary disclosure adopted (AI-DISCLOSURE.md).
- Platform surface confirmed from docs.heycall-e.com quickstart: Python SDK
  `calle-ai`, auth via `CALLE_API_KEY` env var (keys from
  dashboard.heycall-e.com), `client.calls.create_and_wait(task=...,
  result_schema=...)`, structured result + completion confidence on the
  returned call object. AU (+61) outbound supported per the integrations
  repo's regions table ("Local" line region).

### Design decisions
- **Offline-first.** Everything except the actual telephony runs with stdlib
  Python and a deterministic MockProvider; the live CalleProvider is a thin
  adapter behind the same `CallResult` interface. Reason: the 20-free-call
  budget is the binding constraint — dev iteration must cost zero calls.
- **Budget guard with no override flag.** Ledger file, default cap 8 real
  calls, reserving 12 for demo takes. Exhaustion degrades to skipped
  bookings, never to spend or an ask.
- **`--live` requires `--override-phone`.** Real calls can only be routed to
  a number the operator supplies at run time. No real number in the repo;
  demo data uses ACMA-reserved fictional numbers (0491 570 xxx).
- **Call script hardening in the task prompt**: agent self-identifies as AI,
  wrong-number bailout, no arguing, 90-second target, reschedule preference
  captured verbatim but no slot promised (the operator confirms by text).
- Result schema kept to one required enum + two optional strings — small
  schemas seemed the reliable path for structured extraction from a call.

### Built and tested
- `noshow_shield/` package: models (E.164 validation, booking lifecycle),
  atomic-write JSON calendar store, mock + live providers, budget ledger,
  confirmation agent, argparse CLI (`sync` / `preview` / `run` / `summary`).
- 10 offline tests green (`python3 -m unittest discover -s tests`), covering
  scenario application, re-call exclusion for confirmed bookings, invalid
  phone skip, budget refusal mid-run, override-phone validation.
- End-to-end mock demo run verified: 5 bookings -> 2 confirmed, 1 reschedule
  (preference captured), 1 no-answer, 1 cancelled; summary flags the two
  needs-attention customers.

### Friction points observed (feeds C2)
- The quickstart's TS and Python examples put the destination number inside
  the free-text `task` rather than a dedicated parameter — easy to get wrong,
  and it makes number-hygiene (masking, validation) the caller's problem.
- Free-tier size (20 calls) vs. no documented sandbox/simulator: nothing in
  the docs indicates a way to test the call loop without burning quota.
- `create_and_wait` blocks; no documented per-call timeout or webhook
  alternative in the quickstart excerpt we could retrieve.
- Docs discoverability: supported-regions table lives in the integrations
  repo README, not the main docs site; free-tier details not in the docs at
  all (only on the marketing/contest pages).

### Not yet done (waits on Nathan's account — see docs/NATHAN-CONNECT.md)
- First live call against the real SDK (validates the CalleProvider field
  mapping: `structured_result`, `completion_confidence`, `id`).
- Video recording (needs one rehearsal live run + one recorded take;
  budgeted ≤6 real calls total, cap leaves 8).
- PR branch push + Devpost form (Nathan clicks only).

## 2026-09-08 — session 1 (continued): submission docs
- README (honest capability statement), AI-DISCLOSURE, DEVPOST draft,
  demo beat sheet (<3 min per rules), PR entry draft under `pr-draft/`,
  C2 feedback draft, Nathan 15-minute connection guide.
- Spend: AU$0. No compute quote requested; none needed (local Python +
  free-tier calls only).

## Live validation — 2026-09-10 (day 28)

Two validation calls to the operator's handset (budget 2/8 used):
1. Call 1 parsed `unknown` → root cause found in minutes: `create_and_wait`
   returns a plain JSON dict (verified in SDK source), but the provider read it
   with `getattr` — the attribute miss made every verdict fall through to
   UNKNOWN. The field name itself (`structured_result.confirmation_status`) was
   correct all along; only the access pattern was wrong.
2. Post-fix call parsed `confirmed` end-to-end: live call → conversation →
   structured verdict → calendar write-back → clean operator summary.
   Raw-response debug dump confirmed ground truth: verdict at top-level
   `structured_result` with fields `confirmation_status`, `notes`.

Fifth consecutive instance of the sprint's mock-vs-real pattern: first live
execution surfaced exactly one integration defect. The demo (Sitting B) now
exercises a proven path. Remaining budget: 6 calls for ≤3 takes + rehearsal.

## Prompt quality pass — 2026-09-11 (recording session)

Live calls returned correct structured verdicts but sounded stilted. Root cause
in `build_task`: the prompt specified procedure only, with no manner guidance,
and interpolated raw ISO values ("... on 2026-09-12 at 09:30"), which spoken
agents read out digit by digit.

Fixes: new `humanise_when()` renders "tomorrow at 9:30 in the morning" relative
to the call date; the task now carries an explicit HOW TO SOUND block (short
turns, one question at a time, contractions, single AI disclosure up front, no
filler, yield on interruption) alongside the numbered procedure. Disclosure and
the never-promise-a-slot rule are unchanged.

Also logged as C2 feedback: the platform exposes no transcript, so a call with a
correct verdict but poor phrasing is invisible to the API — we only caught this
because a human was on the other end of the line.
