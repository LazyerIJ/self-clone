<div align="center">

**English** · [한국어](README.ko.md)

# self-clone

### Teach an agent to do your job — then make it pass the exam.

**Your repos have harnesses that know the code. Nothing knows *you*. self-clone does.**

[![Claude Code skill](https://img.shields.io/badge/Claude_Code-plugin-1b1b19?style=flat-square&logo=claude&logoColor=white)](#install)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-SKILL.md-1b1b19?style=flat-square)](https://agentskills.io)
[![Python stdlib only](https://img.shields.io/badge/dependencies-0-1b1b19?style=flat-square)](#requirements)
[![Read-only](https://img.shields.io/badge/sources-read--only-1b1b19?style=flat-square)](#what-it-never-does)
[![MIT](https://img.shields.io/badge/license-MIT-1b1b19?style=flat-square)](LICENSE)

[Quick start](#quick-start) · [What a grown node looks like](#what-a-grown-node-looks-like) · [The exam loop](#the-exam-loop) · [How it works](#how-it-works) · [FAQ](#faq)

<code>/plugin marketplace add LazyerIJ/self-clone</code>

<br /><br />

<img src="docs/demo.svg" width="860" alt="Illustrative run: /loop /grow grows the knowledge tree one node at a time; /exam replays a real ticket using only the tree and scores 14/25; the holes are grown; the retake scores 23/25." />

</div>

---

Every repo you work in already has a Claude harness — `CLAUDE.md`, skills, docs — that knows the code. What no harness knows is **the person at the keyboard**: where work comes in, which repo and skill you open for it, what you type by hand outside the harness, whom you ask, and how you decide at the moments the harness stops and waits for you.

self-clone grows that knowledge into a **deep, narrow tree** from the traces already on your machine — Claude sessions, shell history, task notes, git logs, tickets, chat threads. Then it **tests the tree**: a sub-agent that may read *only the tree* replays a real past ticket, gets graded against what you actually did, and every gap is pinned back into the tree to be grown next.

Run it in a loop and it never finishes. It just keeps getting closer to you.

## Quick start

```
/plugin marketplace add LazyerIJ/self-clone
/plugin install self-clone@self-clone
/clone-init
```

`/clone-init` asks five things (home folder, your name, where your repos live, notes folders, folders it must never read) and creates your **clone home** — a local git folder with no remote. Then:

```
cd ~/self-clone-home && claude
/survey          # map your sources: repos, sessions, shell, and which tracker/chat/wiki are reachable
/loop /grow      # grow one node per step, forever; /exam comes up on its own every 10 grows
```

Want to feed it something specific? `/grow ACME-412` or `/grow <chat thread link>` follows that case end to end and pins it into every node it touches.

## What a grown node looks like

A settled end node from [`examples/acme`](examples/acme/tree/work/bugs/regression/bisect/local-repro/first-bad-commit/_branch.md) — a fictional engineer, Alex:

```markdown
## Run
- where: `~/code/acme-api`, clean tree (`git stash -u` first if dirty)
- what: `git bisect start main <last-good-tag> && git bisect run make test-fast TEST=<failing test>`
- judge: lands on a dependency bump → stop, go to `culprit-handoff` (Priya owns deps);
         lands on a migration → never re-run it locally, ask the acme-api harness what <sha> changes
- leave: comment on the ticket `first bad: <sha> (<author>), found by bisect`, then `git bisect reset`

## Cases
- ACME-412 (2026-08): CSV export lost the header row → bisect hit a pandas bump → handed to Priya → fixed same day
- ACME-431 (2026-09): `/orders` 30% slower → bisect hit Alex's own N+1 → asked the harness for a fix → merged next morning

## Exam
- Q: Bisect lands on a dependency bump. What now? A: Stop — hand it to Priya with the sha.
```

No code is copied in. The tree holds **where things are, when to open them, whom to ask and how you judge** — and points to the repo harness for everything it already knows.

### It also works with the tools your team already uses

If your work runs through Slack, Jira, GitLab, Confluence or Sentry, connect them as MCP servers or CLIs and `/survey` picks them up. Each one holds a piece of the story — the request in a thread, the ticket, the merge request, the alert — and `/grow` follows a case through all of them, so the tree learns *how a request travels* from the first message to the final reply. It only ever reads: no messages, comments, transitions or merges.

One real tree grown this way reached ~750 nodes, ~430 real cases and ~1,100 exam questions in three days of `/loop /grow`.

## The exam loop

Most "agent memory" is never checked. Here, every 10 grows the frontier raises `@exam`:

1. **Pick real work** — replay a past ticket (only the original request is shown), a scenario from the bank, or a new question aimed at the tree's weakest spot.
2. **Answer from the tree only** — an Explore sub-agent may open only paths the tree points to. Missing steps must be marked `[not in tree]`, uncertain ones `[guess]`, code questions handed off as `[harness: <repo> — <ask>]`.
3. **Grade against the sources** — correct · executable · judgement · people · complete, 0–5 each. **22/25 with no `[not in tree]` or `[guess]`** = "can replace".
4. **Pin the holes** — each gap goes into the `## Unknown` of the node it belongs to, and settled nodes drop back to growing. `/grow` fills `[exam]` holes first.

See a [sample exam log](examples/acme/exams/log/2026-10-02-1410-R-checkout-500.md): 14/25 → four grows → 23/25.

## How it works

| skill | what it does |
|---|---|
| `/clone-init` | creates the clone home: `tree/`, `tools/`, `sources/`, `exams/`, `RULES.md` |
| `/survey` | maps local sources and which external systems are reachable — through tools that carry their own credentials |
| `/grow` | grows **one node** per call: reads its sources to the end, then splits it one level down or fills the floor test |
| `/exam` | the loop above |

**Code owns shape, the model owns content.** `tools/tree.py` (Python stdlib only) enforces a deep, narrow shape — ≤ 3 children per branch, no single-child branches, ≤ 40-line bodies, one split criterion per level — and picks the next step: shape violations → exam holes → pinned cases → nodes below the floor → stubs → unknowns → stale nodes. What goes where is decided by Claude.

**The floor test.** An end node is `settled` only when it is *one thing*, *can be done as written* (exact command, path, channel, decision rule — or "ask the `<repo>` harness <what>"), *is not wrong* (every fact was opened and checked), is deep enough, and has `## Run`, two real `## Cases` with pointers, three `## Exam` Q&As and no `## Unknown`.

```
tree/
├── work/       what you do          → bugs/regression/bisect/local-repro/first-bad-commit
├── practice/   how you judge        → approvals/reviewer-choice/…
├── systems/    what you work on     → a map: repo, harness, doc, owner, alerts
├── env/        where, with what     → devices/laptop/ssh/jump-host
└── org/        with whom            → colleagues/design/<person>/review-request
```

## What it never does

- **reads secrets** — `.env*`, keys, tokens are denied; it only notes that a credential exists
- **writes anywhere but the clone home** — source repos and external systems are read-only; no commits, comments, messages or state changes
- **stores customer or personal data**, or quotes chat and ticket bodies verbatim
- **copies what is already written** — code, docs and wiki pages get a pointer, not a copy
- **leaves your machine** — the clone home has no git remote, and web search is denied so internal names never reach it

## Install

**Claude Code** (recommended)
```
/plugin marketplace add LazyerIJ/self-clone
/plugin install self-clone@self-clone
```

**skills CLI**
```
npx skills add https://github.com/LazyerIJ/self-clone
```

**Manually** — copy `skills/*` into `~/.claude/skills/`.

The skills follow the [Agent Skills](https://agentskills.io) `SKILL.md` format. They are built and tested on Claude Code; `/exam` uses Claude Code's sub-agents and `/loop`, so other agents may need adapting.

## Requirements

Claude Code · Python 3.9+ (standard library only) · git.

## Configuration

- `tools/shape.json` — every limit: depth, fan-out, floor test, revisit days, exam frequency, and the section headings themselves (switch `## What` to `## 무엇` or any language).
- `clone.json` — your name, work roots, harness output folders, notes folders, never-read folders.
- `RULES.md` — the constitution your clone follows. Edit it.

## FAQ

**Isn't this just a big `CLAUDE.md` or memory file?**
No. Memory grows sideways and is never tested. This tree is forced to go deep (one split criterion per level, a floor test before anything is "done"), it refuses to copy what is already written, and an exam keeps proving where it is wrong.

**Does anything get uploaded?**
Nothing beyond your normal Claude Code session. The clone home is a local git folder with no remote, and the generated permissions deny web search, `git push` and reading secrets.

**How long until it is useful?**
The first `/survey` and a few dozen grows give you a usable map. "Can replace" on a real replayed ticket is the bar — the exam log tells you honestly how far away that is.

**Can I use it for non-engineering work?**
Yes. The facets (work · practice · systems · env · org) fit any desk job; rename them in `tree/` and `RULES.md`.

## Star history

<a href="https://star-history.com/#LazyerIJ/self-clone&Date"><img src="https://api.star-history.com/svg?repos=LazyerIJ/self-clone&type=Date" width="600" alt="Star history chart" /></a>

## License

MIT
