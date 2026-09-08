# PR title

Add no-show-shield: appointment-confirmation skill (hackathon entry)

# PR description

Adds `skills/no-show-shield/` — an appointment-confirmation calling skill for
solo trades/service businesses, submitted as a "Your Code Is Calling"
hackathon entry.

- Reads a day's bookings from a JSON calendar, places one confirmation call
  per booking via the CALL-E Python SDK with a structured `result_schema`,
  writes `confirmed / reschedule_requested / cancelled / no_answer` outcomes
  back, and emits an operator summary.
- Follows the contribution guidelines: scoped to the appointment-confirmation
  skill area, documents setup/usage/side effects/cancellation behavior, all
  sample numbers are fictional (ACMA-reserved range), validated with
  `scripts/validate_repository.py`.
- Full source, tests, and demo video are linked in the skill README.

Checklist:
- [x] Skill folder with README (setup, usage, side effects, cancellation)
- [x] One-line README index entry, no marketing language
- [x] Masked/fictional phone numbers only
- [x] `python3 scripts/validate_repository.py` passes locally
