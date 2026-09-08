# C2 — Most Valuable Feedback survey draft

> For Nathan's review before submission (click C5 in docs/NATHAN-CONNECT.md).
> Rules verified 2026-09-08: eligibility = registered on Devpost + survey
> completed within the Feedback Period (Jul 23, 2026 9:30 PM SGT –
> **Sep 18, 2026 11:45 PM SGT**); winning feedback = "actionable comments
> that the Sponsor can use to improve CALL-E or related documentation".
> One submission per entrant. Grounded in the C1 build log; items marked
> [VERIFY LIVE] should be confirmed or cut after the first real SDK calls
> on Sep 10–11 — nothing unverified should be submitted as observed fact.

## Context (for the survey's "tell us about your project" style questions)

I built No-Show Shield, an appointment-confirmation agent for solo trades
businesses (Python SDK, structured result schemas, budget-guarded live
calls), submitted to this hackathon. The feedback below is from that build.

## 1. Destination number should be a first-class parameter

The quickstart pattern puts the destination number inside the free-text
`task` ("Call <E164_PHONE> and ask..."). In a real app this is fragile: the
number can't be validated, masked, or overridden without string surgery, and
a prompt-injection-ish bug (e.g. a customer name containing digits) could in
principle change who gets called. Suggestion: accept `to: "+61..."` as a
dedicated, validated parameter on `calls.create*`, and treat a number in the
task text as a fallback. We ended up wrapping every call in our own E.164
validator and an `--override-phone` layer to get this safety.

## 2. A sandbox/simulator mode would protect the free tier and your funnel

The free tier is 20 calls and there is no documented way to exercise the call
loop without spending them. We had to build a full mock provider before
touching the SDK — most hackathon teams won't, and will burn their 20 calls
on integration bugs, then churn. A `CALLE_SANDBOX=1` mode (or
`client.calls.simulate(...)`) that runs the agent conversation against a text
transcript and returns a normal call object with `structured_result` would
make the first hour with the platform dramatically better.

## 3. Timeouts and non-blocking patterns for `create_and_wait` [VERIFY LIVE]

`create_and_wait` is the only completion pattern shown in the quickstart. A
confirmation run over N bookings is sequential phone calls; one hung call
blocks the batch. Documenting a per-call timeout parameter, a
`create` + poll pattern, and/or a webhook callback (if these exist, they are
not in the quickstart) would help anyone building batch calling.

## 4. Documentation placement gaps (all reproducible today)

- The supported-regions/languages table lives in the
  `call-e-integrations` repo README, not on docs.heycall-e.com. Whether you
  can call +61 (you can) is a go/no-go fact for a build — it belongs in the
  main docs next to the quickstart.
- Free-tier size and the additional-calls request path appear on marketing/
  hackathon pages but not in the docs. Developers plan dev-call budgets
  around this number; put it where developers read.
- The Python package is `calle-ai` on PyPI but imports as `calle`, while the
  TS package is `@call-e/calle`. One naming table at the top of the
  quickstart would remove a papercut every new user hits.

## 5. Result-schema guidance from a working example

What worked for us: one required enum (`confirmation_status`, 5 values) plus
two optional strings extracted reliably; our first instinct — a larger nested
schema — felt riskier for a 60-second call. A docs page of "schema patterns
that extract well from short calls" (enum + verbatim-capture string + notes)
with real transcripts would save every team the same trial and error.
[VERIFY LIVE: confirm the small schema does extract cleanly on real calls
before citing reliability.]

## 6. Small praise, specific

`create_and_wait` returning `taskCompleted` + `completionConfidence` +
`evidence` alongside the structured result is genuinely good API design — we
mapped confidence straight into our operator summary so a human eyeballs the
low-confidence outcomes. More of the API surface should assume the caller is
an unattended agent like this.

---
*Authorship note if the survey asks: feedback drafted from the project's
build log with AI assistance (Anthropic Claude), reviewed and submitted by
the entrant.*
