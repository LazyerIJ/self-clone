---
name: grow
description: Grows the self-clone tree by one step — picks the top node of the frontier, reads its sources to the end, then either splits it one level down or fills the floor test (run · cases · exam). With a ticket key or chat-thread link as the argument, it only pins that case into every node it touches. Use for "/grow", "/grow <range>", "/grow ABC-123", "/grow <thread link>", "grow the tree", "next node", "put this case in the tree", and inside /loop.
---

# grow — top-down, one node at a time, all the way to the floor

The goal is **that the clone can start from this tree, open the knowledge on this machine that the tree points to, and do the owner's work in their place**. The tree is not a copy of knowledge; it is "how the user uses knowledge" (what is where, when to open it, whom to ask, how to judge). The bar is not "can explain the concept". It is "can do exactly what the owner would do in the terminal, the chat app and the issue tracker".
One call handles **one node**. Run every command from the clone home. `RULES.md` is the source of truth; section headings are in `tools/shape.json`.

## 0. Range
- Without an argument the whole tree is in range.
- With a path (`/grow systems`) only that subtree is (for parallel loops): add `--under <range>` to every command below.
- With **a single case** — a ticket key (`ABC-123`), a chat-thread link, a task name in a harness output folder — do only **0-a. Pin a case** and stop (no growing).

## 0-a. Pin a case — one case as the entrance
A single case never grows a node directly. Mark every node it touches and let the frontier order (`pinned cases`) do the growing — so the tree does not grow lopsided, and practice nodes get the same case as work nodes.
1. Follow the chain of section 3 to the end: request (thread) → ticket → work (harness outputs, sessions) → judgement (approvals) → change (merge request, commits) → deploy → reply. Write only what you opened.
2. Find every node it touches (`grep -rl`, `tree.py show`) — not one per facet, all of them:
   - work: the deepest node of this work type
   - practice: the criterion node at every point where the owner approved or decided (choosing a reviewer, accepting a risk, rolling back, touching production data…)
   - systems · env · org: the systems, access paths, people and organisations involved
3. Pin one line into each node's `## Candidates`: `- [case <key>] <what to look at here, one line> — <pointer>`. Skip if the same key is already there.
   If no node fits, pin into the closest parent: `[case <key>] no fitting branch — <what>` (the branch is decided when growing).
4. Do not change `checked` or state of pinned nodes. `tree.py lint` → add only the pinned paths → `git commit -q -m "case(<key>): pinned into <n> nodes"`.
5. Report: `case <key>: pinned — <node paths>. It comes up in the frontier as pinned cases.`

## 1. Pick
```
python3 -I tools/tree.py frontier -n 5 [--under <range>]
```
Take the top one. Its reason decides this step:
- `@survey` → run the whole `/survey` procedure, report, stop.
- `@exam` → run the whole `/exam` procedure, report, stop.
- `violation` → **restructure** (4-b)
- `exam holes` → **grow** (4-a). First open the answer pointer on each `[exam]` line and fill it, then delete the line.
- `pinned cases` → **grow** (4-a). First open the case chain of each `[case]` line and fold it into this node (cases · run · exam · unknown · relations), then delete the line. If the node was settled, re-run the floor test afterwards. Raise a new branch only when two or more different cases take the same branch — with only one, leave a note in `## Candidates` without `[case]`.
- `below floor` → **regrow** (4-a). First set `state: growing`. Having been settled before guarantees nothing.
- `stub` · `growing, unknowns` → **grow** (4-a)
- `refresh: sources changed` · `refresh: last checked` · `review` → **refresh** (4-d)

**The frontier is never empty.** When there seems to be nothing to do, it says `@exam`. Never report "the tree is complete" or "nothing left".

## 2. Read the context
```
python3 -I tools/tree.py show <path>
```
- Read the ancestors and siblings.
- First check by what criterion this node was split from its siblings (first line of the parent's `## Boundary`).
- `[exam …]` lines in `## Unknown` are holes a real exam hit. Fill those first.
- `[case …]` lines in `## Candidates` are pinned cases. Fold them in right after `[exam]`.

## 3. Dig the sources to the end (read-only)
Start from the node's `## Evidence`, `## Unknown`, `## Candidates`. The source maps are `sources/local.md`, `sources/external.md`, `sources/access.md`.
**Never write from a pointer alone. Only what you actually opened in this step becomes evidence.**

**Local**
- **Sources that are already written** (code, repo docs, skills, wiki, notes, memory): do not copy content. You open them to make **the map exact** — exact location (path, page id, doc name), which questions it answers, how to open it, whether it is still alive.
- **Code**: that is the repo harness's. Read only **enough to route**: which repo, which harness skill, which doc owns this work, and which admin commands or job names the owner types by hand.
- **Harness outputs**: real cases and the owner's approvals live here — the folders in `clone.json harness_dirs` inside each repo (task notes, ADRs, result write-ups, review notes).
- **The owner's Claude sessions**: instructions they gave, choices they made, commands they ran in each repo.
  - `~/.claude/projects/<project>/*.jsonl`, `~/.claude/history.jsonl`, `~/.codex/sessions/`
  - These are large. `grep` for a ticket key or a word, read only around it, summarise.
- **Shell history** (`~/.zsh_history`): copy command shapes **as they are**, masking tokens, passwords, IPs and customer identifiers as `<…>`.
- **Also**: `git log`, `~/.claude/projects/*/memory/`, `~/.ssh/config` (aliases only), notes folders.

**External (read only)** — use exactly the tools `sources/access.md` marks as working:
- issue tracker: search by key, by assignee/reporter/commenter = owner; read description and comments
- wiki: search, read pages, walk the page tree of a space
- chat (MCP): search by ticket key, system name, `from:me` → read the thread
- code host: merge request descriptions and diff summaries
- error tracker, dashboards: names and definitions only. Never run queries that could return customer rows.

**Follow every case as a chain to the end**: request (thread) → ticket → work (task file, session) → judgement (gates, approvals) → change (MR, commits) → deploy → reply (thread). That chain becomes `## Cases`.

**When stuck**: only after trying **three or more** sources, record it in `## Unknown`:
- shape: `- <question> — tried: <where>, blocked: <why>`
- for servers you have no access to, trace server facts backwards from code, config, harness, tickets and conversations.

**Never**
- open secret files
- use credentials directly to call an API
- handle customer data
- write to a source (commit, comment, state change, message)
- put internal names, tickets or code into a web search
- copy customer names, accounts, contacts. People are recorded by name and work role only.

## 4. Write
**a. Grow / regrow**
1. **Diverge, then converge**
   Before choosing children, lay out **5–10 possible axes and items** for splitting this node, grounded in what the sources show, through these lenses:
   - stages: first → last
   - situations: normal / exception / outage
   - targets: per client, system, screen
   - people: who requests, who decides
   - time: daily / monthly / holidays / release day
   - failure: where and how it breaks
   - inverted: "how would someone ruin this by trusting only this node" — the answer is a missing branch

   Then pick **the one axis the owner actually splits by when working** and converge to 2–3 children (from depth 3 the cap is 3 — go deep, not wide).
   - Useful unchosen axes go to the children's level or to `## Candidates`.
   - The laid-out list itself is not written into the node.
2. Facts about action — commands, CLI shapes, ids, limits — go into `## Run`, not `## Boundary` (Boundary is only the split criterion and in/out). Fix `## What` at 1–3 lines. If you find yourself listing stages, branches or variants, those are children.
3. Create children with `python3 -I tools/tree.py new <path>/<slug> <title>`.
   - Fill each child's `## What` (one line), the `## Evidence` you know, and concrete `## Unknown` items from the sources you opened.
   - Write the split criterion on the first line of `## Boundary`.
   - Four or more → raise an intermediate concept and group. Never make a single-child branch (that is only one more level of name, not a split).
   - **How to go deep**: if the decision part of an end branch's `## Run` has two or more condition → action pairs, each condition is a child. If `## Cases` took different branches, those branches are children. If there are several targets (clients, endpoints, event types, screens), targets are children. **Move** the parent's cases and exam items into the right children, then find more cases in the sources until each child has two.
4. While regrowing, ask of every sentence **"where is this already written?"**. If it is, delete it and replace it with a one-line map `- <question/situation> → <location> (<how to open>)`. If it is not (judgement distilled from several cases, customs, people, hand habits), keep it.
   **Strip what belongs to the harness in particular**: code locations, functions, models, state transitions, queries, business-rule detail are removed (their source of truth is the repo) and replaced by one line "ask the `<repo>` harness — source of truth `<doc>`". In cases too, keep the user-seat judgement, approval and reply, not what the code change was.
5. When existing body text moves down into children, **move** it, do not delete it. The parent keeps only definition and boundary.
6. An end branch is `settled` only when it fills every part of the **floor test** below. If anything is missing it stays `growing`. That is not failure, it is honesty.

**b. Restructure** (lint violations: too many children, leaves, lines)
- Too many children: raise middle branches by a common criterion and `git mv` into them. Fix relation links.
- Body too long: move chunks down into child branches.
- Too many leaves: group leaves into a concept branch, or promote them to branches.

**c. Leaf** — only for an unsplittable record (one judgement case, one procedure, one fact). Names unique across the tree.

**d. Refresh**
1. `sources changed`: look only at what appeared after `checked` — `git log --since`, new harness outputs, new tickets and threads for those keys.
2. `last checked`: check the evidence is still alive and look for new related tickets and threads. **Adding one more case is the default.**
3. Both: re-run the floor test. If new sources change an exam answer, fix it. If the node turned out to be a bundle, set `growing` and split.
4. `review` (a parent whose children all settled): check the following, then settle the parent:
   - siblings are split by one criterion
   - no missing branch — count again from the sources
   - no missing `## Relations` between children

**Every step**
- Put `checked: <today YYYY-MM-DD>` in the front matter of every node touched (including new children).
- When it connects to another branch, add `## Relations`. Never write the same content in two places.

## 5. Check and commit
```
python3 -I tools/tree.py lint [--under <range>]   # must be E 0 to commit — touched settled nodes are also machine-checked against the floor
git add <paths touched>                            # parallel loops exist, so add only what this step created or changed, not -A tree
git commit -q -m "grow(<path>): <what was done, one line>"
```
- Fix remaining lint violations. If the floor cannot be filled, leave it `growing`.
- On an `index.lock` conflict, retry a moment later.

## 6. Report (one or two lines)
`<path>: <grow/restructure/refresh> — children a·b·c, cases n, exam n, unknown n. Next frontier: <path>`
- Inside /loop, the next step is called by /loop.
- Never ask the owner. When blocked, record it in `## Unknown` and move to the next node.

## Floor test — the condition for settled (depth has no end; more detail is better)
An end branch is `settled` only when it meets **all** of these. 1–3 are judged by grow, 4–8 machine-checked by `tree.py lint`.

1. **It is one thing** — it points at one real thing.
   - e.g. one batch job, one API, one event type, one state transition, one approval point, one request type from a person, one command sequence, one alert.
   - "N stages", plurals, "… in general", "… related" are bundles.
   - If What contains ①②, each of those is a child.
2. **It can be done as written** — the clone reads this node and its ancestors, **opens what the node points to**, and acts without asking or guessing. The pointers must be exact ("somewhere in the docs" fails; a doc path or page id passes).
   - The exact command, screen path, channel, decision condition, and where to hand off to a harness (repo, skill, prompt shape) are all there.
   - A step that needs business logic passes if it ends in "tell/ask the `<repo>` harness <what>"; written content passes as "open `<location>` and look at <what>". The content itself is not memorised in the tree.
   - "Look at the sources" does not pass.
3. **It is not wrong** — every fact written was checked by opening the source.
4. **Depth ≥ `floor.min_depth`** (`min_depth_by_facet` lets map-like facets such as systems be shallower) — a shallow end branch still has a split left. `## Run` ≤ `max_exec_items` items, body ≤ 40 lines — beyond that it is a bundle.
5. **`## Run`** — what the clone actually does for this work. Each facet writes something different:
   - work · practice: where (repo path, host alias, screen, channel) → what (shell command **as is**, harness entry command and what to tell it; secrets as `<…>`) → judgement (user-seat condition → action) → what to leave (ticket, thread, file, commit-message shape)
   - systems: **a map only** — when work on this system comes up: the repo/harness to open and its skill, the source-of-truth doc, the owner (person), the alerts and channels it rings, the deploy path. No code, models or state transitions.
   - env: the path to reach it (prerequisites like VPN or bastion → alias → command), the check command, failure symptoms and what to do
   - org: how to work with this person or organisation (channel, how requests arrive, how replies look, decision rights)
6. **`## Cases`** — two or more real events, a pointer on each line.
   - shape: `- ABC-123 (YYYY-MM): what happened → what the owner did or decided → result`
7. **`## Exam`** — three or more questions the person doing this work would really get, answerable straight from this node.
   - shape: `- Q: … A: …`
   - answers containing "unknown" or "guess" do not count.
   - bad: "what is this system"
   - good: "the nightly backup job failed — what is the first command?", "a deploy freeze starts tomorrow — what do you hold back and whom do you tell?"
8. `## Unknown` is empty and `## Evidence` has three or more pointers of this node's own.

A **branch** (a node with children) is settled when every child is settled and the branches cover the sources without gaps.

A feel for the floor per facet (examples; deeper is fine):
- systems: service → area → feature → flow → **one job / API / event / state transition** (e.g. blog/api/comments/moderation/spam-hook)
- work: work type → subtype → situation → stage → **one decision point / command sequence** (e.g. bugs/regression/bisect/local-repro/first-bad-commit)
- env: area → means → target → **one path step** (e.g. devices/laptop/ssh/jump-host)
- org: organisation → team → person → **one request type** (e.g. colleagues/design/<person>/review-request)
- practice: principle → approval point → **one criterion**. Judgement cases under it are leaves.

As cases pile up, raise branches by the criterion that separates them and go down. That is how the tree gets deep.

## Judgement
- Split criteria follow **how the owner actually splits things when working** (harness stages, approval points, system boundaries, clients, failure types).
- Go top-down, but every end must reach a tangible action.
- The user's seat (where the owner judges, approves, signs off) becomes a node. That is where the clone will sit. Its criteria are pulled from real approval records.
