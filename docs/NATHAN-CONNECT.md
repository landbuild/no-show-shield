# Nathan — connection guide and click list

Everything below is a Nathan click. AB performs none of these. Total ~75 min
across three sittings. All dates respect the internal freeze **Fri Sep 12**;
the external deadline is Sep 14, 11:45 **PM** SGT (confirmed live 2026-09-08
— later than our recorded AM reading, but the freeze stands).

## Sitting A — accounts (15 min, do by Wed Sep 10)

| # | Click | Time |
|---|---|---|
| A1 | Create CALL-E account at heycall-e.com (grants 20 free calls) | 5 min |
| A2 | Dashboard -> Account -> API keys -> create key; then in a terminal: `export CALLE_API_KEY="<key>"` (or tell AB it exists — never paste the key into chat or any file that gets committed) | 3 min |
| A3 | Register for the hackathon on call-e.devpost.com (Devpost account you already have from ATA) | 4 min |
| A4 | Open the Feedback Survey link from the contest page just to sight it (period confirmed open until Sep 18, 11:45 PM SGT) — do not submit yet | 2 min |

After A2, AB runs the first live SDK call **to your phone only** (you supply
the number at the terminal via `--override-phone`), validates the field
mapping, and reports call-budget usage. Estimated 2 calls.

## Sitting B — demo recording (30 min, Thu Sep 11)

| # | Click | Time |
|---|---|---|
| B1 | Sit with phone on camera; AB drives the terminal per docs/DEMO-SCRIPT.md; you answer the live call (one rehearsal + up to 3 takes, ≤6 calls total) | 20 min |
| B2 | Upload the chosen take to YouTube (public), grab the URL | 5 min |
| B3 | Confirm you're happy with the take (integrity check: nothing staged is presented as unstaged) | 5 min |

## Sitting C — submission (30 min, Fri Sep 12 — freeze day)

| # | Click | Time |
|---|---|---|
| C1 | GitHub: create public repo `no-show-shield` under your account, push this local repo (`git remote add origin … && git push -u origin main`) | 5 min |
| C2 | Fork `CALLE-AI/awesome-phone-call-agents`, copy `pr-draft/skills/no-show-shield/` into `skills/no-show-shield/`, add the README index line from `pr-draft/README-ENTRY.md`, run their `python3 scripts/validate_repository.py`, click **Create pull request** with the PR text from `pr-draft/PR-DESCRIPTION.md` | 10 min |
| C3 | Integrity review (not delegable): read AI-DISCLOSURE.md and DEVPOST.md — confirm no false claims | 5 min |
| C4 | Devpost form: paste DEVPOST.md text, video URL, PR URL, CALL-E account email -> **Submit** | 8 min |
| C5 | C2 feedback: read `C2-FEEDBACK-DRAFT.md`, edit anything you disagree with, submit the Feedback Survey (deadline Sep 18, but do it while the form is open) | 15 min* |

*C5 can slip to the weekend without risk — its own deadline is Sep 18,
11:45 PM SGT.

## Standing rules honoured
- No organiser contact; the PR is a submission mechanism — if maintainers
  request changes, AB drafts mechanical fixes only, you click.
- Spend: AU$0. No compute tranche requested; nothing here costs money. If
  the free 20 calls somehow exhaust, we stop — we do not use the
  +200-call request form without a fresh decision from you.
- The API key stays in your shell/keychain; it is never committed, logged,
  or pasted into documents.
