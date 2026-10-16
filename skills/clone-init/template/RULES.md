# self-clone — a deep knowledge tree of how the owner works

This folder is a **top-down tree of all the work the owner (see `clone.json`) has left traces of on this machine**.
It is the map and the habits that **an agent reads first when it works on this machine as the owner — as the user, not as a developer inside one repo**. Below, that agent is called *the clone*.
Paths and slugs are lowercase ASCII.

## What goes in, what stays out
- The bar is **can the clone start from this tree, open what the tree points to, and do the owner's work in their place**. A concept explanation is only the start.
- The point of view is **a user who uses the knowledge stored on this machine**. The owner does not memorise rules, code or documents — they know what is where, when to open it, whom to ask, and how to judge what they see. The tree holds exactly that.
- The clone replaces **the owner as a user**. It does not replace the Claude harness inside each repo (that repo's `CLAUDE.md`, skills, docs). Business logic and code detail are the harness's job.
- **One-line rule**: anything **already written down** somewhere reachable (repo docs, `CLAUDE.md`, skills, wiki pages, notes vaults, ticket descriptions, memory) is never rewritten in the tree — write only "where it is, in which situation and why you open it, and the path to open it (VPN, command, MCP)". Write in the body **only what is written nowhere**.
- In — knowledge of the user's seat (mostly written nowhere):
  - how work arrives (channel, requester, ticket), whom it is done with, what is left behind (reply, record, ticket transition)
  - which repo/harness to open and what to tell it (entry command, skill, prompt shape), and on what basis the owner decides where the harness stops (real approval cases)
  - what the owner does by hand outside the harness (access paths, shell commands, deploy buttons, ops replies)
  - **routing**: when a work question comes up, where to ask (which repo harness, which doc, which wiki page, which person) and how to open it
  - **distilled judgement**: patterns and criteria pulled from many cases scattered over chat threads, approval records and sessions. A pointer to one thread is not usable, so this is written in the body (with case pointers as evidence)
  - undocumented customs, order of operations, command habits, how to work with people
- Out — anything already written. Typically the harness's: code structure, functions/models/fields, state machines, queries, business-rule detail. The tree points with one line: "ask the `<repo>` harness — source of truth `<doc>`".
  - Test: **if Claude opened in that repo could answer it alone, it does not go in the tree.**
- No copying of originals (long code blocks, documents, conversations). Summarise facts and attach pointers (path, ticket key, commit, channel, link).

## Split of labour — code owns shape, Claude Code owns content
- Code is only `tools/tree.py` (lint · frontier · floor · show · new · stats), `tools/inventory.py` (local source list), `tools/shape.json` (shape constants), `tools/settings.py` (permissions).
- What to group into which branch and what to write in a node is **decided by Claude Code through `/grow`**. Judgement rules never go into code.

## Shape rules (a deep, narrow tree)
`tools/shape.json` is the source of truth and `tree.py lint` is the judge.
- Branch = folder, one `_branch.md` per branch. A branch's knowledge lives in its `_branch.md` body (do not multiply leaves).
- ≤ 3 children per branch (≤ 5 at depth 0–2), no single-child branches, ≤ 2 leaves, body ≤ 40 lines. End branches must pass the **floor test** in the grow skill to be settled. **When it overflows, do not widen — raise a higher concept and go one level down.**
- A leaf (`<slug>.md`) only for an atomic record with no further concept to split — one judgement case, one procedure, one fact. Leaf names are unique across the tree.
- Siblings are **split by one criterion** (MECE). Write the criterion on the first line of `## Boundary`.
- If something belongs in two places, keep it in one and link from the other with `same`/`about` in `## Relations` — no copies. That is the graph on top of the tree.

## `_branch.md` shape
```
---
kind: branch
title: Title
state: stub | growing | settled
checked: YYYY-MM-DD
---
## What        — definition in 1–3 lines (if you list steps or kinds, those are children)
## Boundary    — first line: the criterion that splits the children. Then what comes here / what does not
## Evidence    — pointer list (`~/code/...`, ABC-123, #channel, commit sha, URL)
## Relations   — `- <rel>: <relative path>` (rel: uses · depends · serves · owner · about · same)
## Run         — end branch: what the clone actually does for this work (command, path, decision condition, what to leave)
## Cases       — end branch: two or more real events `- ABC-123 (YYYY-MM): what happened → what the owner did → result`
## Exam        — end branch: three or more real questions `- Q: … A: …`
## Unknown     — what is not known yet (`[exam …]` = a hole found by an exam). frontier uses this count to pick the next step
## Candidates  — (optional) sub-items without a place yet. grow groups them into children
```
- `checked` is the last day the node was looked at — the basis for refresh (sources changed, stale).
- `stub`: name and What only. `growing`: has Boundary and Evidence, children being grown. `settled`: passes every floor test.
- settled is not permanent. When `/exam` finds a hole, that node and its ancestors go back to growing.
- Leaf front matter: `kind` (fact · preference · pattern · todo · device · procedure · role · doc), `title`, and `description` for procedures.

## Boundaries — what is kept
- **Never move secrets or credentials**: `.env*`, `*.pem`, `*.key`, tokens, passwords, IPs, customer identifiers. Only record that they exist: "credential location: (path) — content not recorded".
- **Read external systems deeply, but never touch credentials**: use only tools that carry their own credentials (MCP servers, an already-authenticated CLI). Never pull a key out to call an API directly — if there is no tool, write "not connected, human hand". The access map is `sources/access.md`.
- Servers you have no access to from this machine are drawn from sources (docs, harness, tickets, conversations), not by connecting.
- **No customer or personal data**: customer folders are recorded as existing only (`clone.json never_read`). People are recorded by role and working relationship only — no contacts, no private life.
- Prompts, chat and ticket bodies are summarised, never quoted.
- **Read-only**: never write to source repos or external systems (commits, comments, state changes, messages). The only place written is this folder.
- This folder is a local git repo with no remote. Do not push it.

## Running it
- One node at a time: `/grow` (grows the top of the frontier). Repeat with `/loop /grow`. Parallel by range: `/loop /grow systems` etc.
- Feeding one case: `/grow ABC-123` or `/grow <chat thread link>` — follows that case's chain and only pins `[case <key>]` into `## Candidates` of every node it touches. Growing happens later, when frontier raises it right after `[exam]`.
- Exam: `/exam` — a sub-agent that reads only the tree solves real work (replaying past tickets, scenarios), it is graded against the sources, and holes are pinned into nodes. Every `exam_every` grows the frontier raises `@exam`; when there is nothing left it also says `@exam` (the loop never ends). Records live in `exams/`.
- Refresh the source map: `python3 -I tools/inventory.py > sources/local.md` for local, `/survey` for external.
- Check shape: `python3 -I tools/tree.py lint` · `stats`.
