---
name: exam
description: Tests whether the self-clone tree can stand in for its owner. A sub-agent that reads only the tree solves real work (replaying a past ticket or an ops scenario), the answer is graded against the sources, and every hole is pinned into the node where it belongs. Use for @exam in the frontier, "/exam", "test the tree".
---

# exam — solve real work from the tree alone

grow fills nodes; exam checks that those nodes **actually get the work done**.
One call handles **one problem**. Run from the clone home. `RULES.md` is the source of truth; the owner's name is in `clone.json`.

## 1. Pick a problem
Take the number of files in `exams/log/` modulo 3 to pick the type (0→R, 1→S, 2→G).

**R. Replay** — re-solve a past job whose answer exists in the sources. The most honest test.
- Pick one ticket from the harness outputs (`clone.json harness_dirs` inside the work repos) or the issue tracker that is not yet in `exams/log/`.
  - check: `grep -rl <key> exams/log`
  - mix types (bugfix · feature · ops request · outage) and repos evenly.
- Give the answerer **only the request as it first arrived** — the level of a chat thread or ticket summary.
  - no solution, result file or commits.
  - remove customer information when summarising.

**S. Scenario** — pick one `[ ]` (unsolved) or `[re]` (solve again) from `exams/bank.md`.

**G. New problem** — through these lenses, lay out 5–10 questions that poke the tree's weak spots. Use the most painful one now and add the rest to `exams/bank.md` as `[ ]`.
- roles: newly joined developer / product manager / security reviewer / support engineer / code reviewer / whoever is on call
- inverted: "if the clone trusted only this tree and caused an incident, where would it be"
- constraints: CI is broken / release freeze / owner on leave / upstream API outage / reviewer absent / late at night
- a problem **must end in action**.
  - good: "when …, what do you type and what do you leave for whom"
  - bad: "what is …"

## 2. The answer — a sub-agent that starts from the tree
Launch one `Explore` sub-agent with the Agent tool. The answerer must not roam the sources freely, so this session never answers in its place. Like the real clone, it **starts from the tree and opens only what the tree points to** — this measures whether the map is exact. Prompt:

> You are the clone of <owner>, working on this machine in their place. First read **`<clone home>/tree/`**.
> Beyond it you may open **only the local paths written in tree nodes (and files directly inside them)**. Do not grep or find around to locate paths that are not in the tree. No web, no command execution.
> For steps that need an external source you cannot open (issue tracker, chat, wiki, servers), write `[open: <pointer from the tree> — what to check]`.
> For every source you read, note "which node pointed me here".
> The work below just arrived. Answer as the owner would, as **an actual sequence of actions**:
> where to connect → what command or query to type → what to look at and how to judge → what to leave for whom.
> Attach the supporting node path to each step. Never invent steps that are not in the tree — write `[not in tree: what is needed]`.
> Mark anything uncertain `[guess]`.
> Steps that need business logic or code detail are not solved directly — hand them off as `[harness: <repo> — <what to tell/ask>]` (that is the repo's Claude harness's job).
> End with "can this work be finished end to end: yes/no + where it blocks".
> Work: <problem>

## 3. Grading — this session, against the sources
Build the answer key from the sources.
- R: that ticket's task notes, review notes, PR and commits, ticket comments, chat thread, the repo's session records
- S · G: node evidence plus source research

Score the answer on five axes, 0–5 each (25 total).
- **Correct**: do the facts match the sources? `[harness: …]` and `[open: …]` **are correct if they point to the right place**. Do not deduct for not memorising content. Deduct if the place is wrong or vague ("some doc somewhere").
- **Executable**: are the user-seat commands, paths, screens and harness entries typeable as written?
- **Judgement**: at each fork, did it choose by the owner's criteria? For R, compare with the real approvals.
- **People**: does it leave the right things for the right people and get the right sign-offs?
- **Complete**: nothing missing from start to end (reply and record included)?

When pinning holes: not knowing content that is already written (the harness's, a doc's) is not a tree hole. A hole is **a missing or wrong map** (didn't know where to open, opened the wrong place, the path to open was blocked) or **missing judgement, custom or people knowledge that is written nowhere**. Each hole line carries the location of the right answer.

Replacement verdict: "can replace" only at 22/25 or more with no `[not in tree]` and no `[guess]`. Do not grade generously. When in doubt, grade lower.

## 4. Pin the holes — back into the tree
For each hole, decide the node it should live in (check with `tree.py show`).
- If the node exists, add `- [exam <today> <problem id>] <what was missing, one line>` to its `## Unknown`. If it was settled, set it `growing`, and its settled ancestors too.
- If there is no place for it, add `- [exam …] <new branch name>: <why>` to the closest parent's `## Candidates`. Set that parent `growing` if it was settled.
- If you found a wrong fact, fix it on the spot and attach the evidence.
- For holes whose answer you already confirmed in the sources, include the answer pointer in `## Unknown` (so grow can use it right away). Writing the node body is grow's job.

## 5. Record and commit
- Write `exams/log/<YYYY-MM-DD>-<HHMM>-<R|S|G>-<slug>.md`:
  - problem
  - answer summary (≤ 20 lines)
  - score per axis with reasons
  - replacement verdict
  - hole list (→ nodes pinned)
- Update `exams/bank.md`:
  - mark solved items `[x 18/25]`.
  - under 22, add `[re]` so it gets solved again.
  - append 1–2 harder follow-up questions that came up, as `[ ]`.
- Check and commit:
  ```
  python3 -I tools/tree.py lint
  git add exams <nodes touched>
  git commit -q -m "exam(<R|S|G>): <problem, one line> — <score>/25, holes <n>"
  ```

## 6. Report (one or two lines)
`exam <id>: <score>/25 (<can/cannot replace>) — holes n → <nodes>. Next frontier: <path>`
