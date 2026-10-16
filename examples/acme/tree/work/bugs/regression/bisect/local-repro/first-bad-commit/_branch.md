---
kind: branch
title: Find the first bad commit
state: settled
checked: 2026-10-14
---
## What
Run `git bisect` on the laptop between the last good release tag and `main` until one commit is left.

## Boundary
One step: from "it reproduces locally" to "this commit broke it". Handing it off is the sibling `culprit-handoff`.

## Evidence
- `~/.zsh_history` — `git bisect run make test-fast` shape, 31 runs since 2025-12
- `~/code/acme-api/Makefile` target `test-fast` (owned by the acme-api harness)
- ACME-412 · ACME-431 (Jira) · #backend-bugs threads 2026-08-19, 2026-09-30

## Relations
- about: ../culprit-handoff/_branch.md

## Run
- where: `~/code/acme-api`, clean tree (`git stash -u` first if dirty)
- what: `git bisect start main <last-good-tag> && git bisect run make test-fast TEST=<failing test>`; the last good tag is the newest `v*` tag the reporter says worked
- judge: lands on a dependency bump → stop, go to `culprit-handoff` (Priya owns deps); lands on a migration → never re-run it locally, ask the acme-api harness "explain what <sha> changes in the schema"
- leave: comment on the ticket `first bad: <sha> (<author>), found by bisect`, then `git bisect reset`

## Cases
- ACME-412 (2026-08): CSV export lost the header row → bisect landed on a pandas bump → handed to Priya, pinned the version → fixed same day
- ACME-431 (2026-09): `/orders` 30% slower → bisect landed on Alex's own N+1 query → asked the harness for a fix, reviewed it → merged next morning

## Exam
- Q: Bisect lands on a dependency bump. What now? A: Stop, do not patch it yourself — hand it to Priya with the sha (culprit-handoff).
- Q: Which range do you bisect? A: From the newest `v*` tag the reporter confirms worked, to `main`.
- Q: What goes on the ticket? A: `first bad: <sha> (<author>), found by bisect`, then `git bisect reset`.
