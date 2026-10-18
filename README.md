<div align="center">

**English** · [한국어](README.ko.md)

# self-clone

### Ask it how you'd handle something.<br/>It answers like you would — from one tree.

**Years of your sessions, shell history, tickets and threads, squeezed into a knowledge tree.<br/>Claude reads only that tree, and it still does your job your way.**

[![Claude Code skill](https://img.shields.io/badge/Claude_Code-plugin-1b1b19?style=flat-square&logo=claude&logoColor=white)](#install)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-SKILL.md-1b1b19?style=flat-square)](https://agentskills.io)
[![Python stdlib only](https://img.shields.io/badge/dependencies-0-1b1b19?style=flat-square)](#requirements)
[![Read-only](https://img.shields.io/badge/sources-read--only-1b1b19?style=flat-square)](#what-it-never-does)
[![MIT](https://img.shields.io/badge/license-MIT-1b1b19?style=flat-square)](LICENSE)

[Just ask](#just-ask) · [Quick start](#quick-start) · [What's in a node](#whats-in-a-node) · [The exam](#the-exam-is-the-same-question-graded) · [How it works](#how-it-works) · [FAQ](#faq)

<code>/plugin marketplace add LazyerIJ/self-clone</code>

<br /><br />

<img src="docs/demo.svg" width="860" alt="Illustrative run: /loop /grow grows the knowledge tree one node at a time; /exam replays a real ticket using only the tree and scores 14/25; the holes are grown; the retake scores 23/25." />

</div>

---

## Why

Your repos already have a Claude harness (`CLAUDE.md`, skills, docs) that knows the code. None of them know **you**: where the work comes in, which repo you open for it, the commands you type by hand, who you ping, and how you make the call when the harness stops and waits for you.

That knowledge already exists. It's just scattered across years of Claude sessions, shell history, notes, git logs, tickets and chat threads. Nobody is going to dig through all of that every time you ask a question.

So self-clone digests it once, into a **deep, narrow tree**. After that:

> 🧠 **The tree is the only thing Claude needs to read.**
> No re-reading raw logs, no searching Slack again. You ask about some piece of work, and the answer comes back the way *you* would handle it: same commands, same people, same judgement calls.

And because "trust me, it knows you" isn't good enough, the tree keeps getting tested against what you actually did. Whatever it gets wrong goes back in to be grown next.

## Just ask

Here's what it looks like once the tree has grown. This uses [`examples/acme`](examples/acme), a made-up engineer called Alex:

> **You:** The PDF invoice export lost its totals row after v2.14. How would you handle it?

> **Clone** *(read only `tree/`)*:
> It worked in v2.13, so it's a regression, and the export isn't down, so no hotfix. Bisect it.
>
> 1. In `~/code/acme-api`, `git stash -u` if the tree's dirty.
> 2. `git bisect start main v2.13 && git bisect run make test-fast TEST=<invoice export test>`
> 3. If it lands on a **dependency bump**, stop. Don't patch it yourself, hand the sha to **Priya** (she owns deps). Same thing happened with the CSV header bug, ACME-412.
> 4. If it lands on a **migration**, don't re-run it locally. `[harness: acme-api — what does <sha> change in the schema?]`
> 5. Comment on the ticket: `first bad: <sha> (<author>), found by bisect`, then `git bisect reset`.
>
> 📎 *from* `work/bugs/regression/bisect/local-repro/first-bad-commit`

None of that came from the code. The repo, the tag range, Priya, the "don't touch migrations" rule and the ticket comment all came from Alex's own history, distilled into one node.

When the tree doesn't know something, the clone says so with `[not in tree]` or `[guess]`. It doesn't bluff.

## Quick start

```
/plugin marketplace add LazyerIJ/self-clone
/plugin install self-clone@self-clone
/clone-init
```

`/clone-init` asks five quick things (home folder, your name, where your repos live, notes folders, folders it must never read) and sets up your **clone home**, a local git folder with no remote. Then:

```
cd ~/self-clone-home && claude
/survey          # map your sources: repos, sessions, shell, and any tracker/chat/wiki you can reach
/loop /grow      # grows one node per step, forever; /exam kicks in on its own every 10 grows
```

Want it to learn one specific case? `/grow ACME-412` or `/grow <chat thread link>` follows that case end to end and pins it into every node it touches.

Once you're happy with it, open Claude in the clone home and just ask.

## What's in a node

This is the settled node the answer above came from ([full file](examples/acme/tree/work/bugs/regression/bisect/local-repro/first-bad-commit/_branch.md)):

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

No code gets copied in. A node holds **where things are, when to open them, who to ask and how you decide**, and for anything the repo harness already knows, it just points there.

### Works with your team's tools too

If your work runs through Slack, Jira, GitLab, Confluence or Sentry, hook them up as MCP servers or CLIs and `/survey` will find them. Each one holds a piece of the story (the ask in a thread, the ticket, the MR, the alert), and `/grow` follows a case across all of them. That's how the tree learns *how a request actually travels*, from the first message to the final reply. It only ever reads. No messages, comments, transitions or merges.

One real tree grown this way hit **~750 nodes, ~430 real cases and ~1,100 exam questions** after three days of `/loop /grow`.

## The exam is the same question, graded

Most "agent memory" never gets checked. Here the exam *is* the use case from [Just ask](#just-ask), run on a past ticket where we already know what you did:

1. **Pick real work.** Replay an old ticket (only the original request is shown), a scenario from the bank, or a fresh question aimed at the tree's weakest spot.
2. **Answer from the tree only.** An Explore sub-agent can open only paths the tree points to. Missing steps get marked `[not in tree]`, shaky ones `[guess]`, code questions go out as `[harness: <repo> — <ask>]`.
3. **Grade it against what really happened.** Correct · executable · judgement · people · complete, 0–5 each. **22/25 with no `[not in tree]` or `[guess]`** means *it can replace you* on that one.
4. **Pin the holes.** Each gap goes into the `## Unknown` of the node it belongs to, and that node drops back to growing. `/grow` fills exam holes first.

Here's a [sample exam log](examples/acme/exams/log/2026-10-02-1410-R-checkout-500.md): **14/25 → four grows → 23/25.**

## How it works

| skill | what it does |
|---|---|
| `/clone-init` | sets up the clone home: `tree/`, `tools/`, `sources/`, `exams/`, `RULES.md` |
| `/survey` | maps your local sources and which outside systems are reachable (through tools that carry their own credentials) |
| `/grow` | grows **one node** per call: reads its sources all the way through, then splits it one level down or fills in the floor test |
| `/exam` | the loop above |

**Code owns the shape, the model owns the content.** `tools/tree.py` (Python stdlib only) keeps the tree deep and narrow: ≤ 3 children per branch, no single-child branches, ≤ 40-line bodies, one split rule per level. It also picks what to grow next: shape violations → exam holes → pinned cases → nodes below the floor → stubs → unknowns → stale nodes. What goes where is up to Claude.

**The floor test.** An end node only counts as `settled` when it's *one thing*, *doable as written* (exact command, path, channel, decision rule, or "ask the `<repo>` harness <what>"), *actually right* (every fact was opened and checked), deep enough, and has `## Run`, two real `## Cases` with pointers, three `## Exam` Q&As and no `## Unknown` left.

```
tree/
├── work/       what you do          → bugs/regression/bisect/local-repro/first-bad-commit
├── practice/   how you decide       → approvals/reviewer-choice/…
├── systems/    what you work on     → a map: repo, harness, doc, owner, alerts
├── env/        where, with what     → devices/laptop/ssh/jump-host
└── org/        with whom            → colleagues/design/<person>/review-request
```

## What it never does

- 🔒 **Read secrets.** `.env*`, keys and tokens are blocked; it only notes that a credential exists
- ✋ **Write anywhere but the clone home.** Source repos and outside systems are read-only. No commits, comments, messages or state changes
- 🙈 **Keep customer or personal data**, or quote chat and ticket bodies word for word
- 📎 **Copy what's already written.** Code, docs and wiki pages get a pointer, not a copy
- 🏠 **Leave your machine.** The clone home has no git remote, and web search is blocked so internal names never end up in a search box

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

**Manually**: copy `skills/*` into `~/.claude/skills/`.

The skills use the [Agent Skills](https://agentskills.io) `SKILL.md` format. They're built and tested on Claude Code; `/exam` relies on Claude Code's sub-agents and `/loop`, so other agents may need some tweaking.

## Requirements

Claude Code · Python 3.9+ (standard library only) · git.

## Configuration

- `tools/shape.json`: every limit (depth, fan-out, floor test, revisit days, exam frequency) and the section headings themselves. Switch `## What` to `## 무엇` or any language you like.
- `clone.json`: your name, work roots, harness output folders, notes folders, never-read folders.
- `RULES.md`: the rules your clone lives by. Make them yours.

## FAQ

**Isn't this just a big `CLAUDE.md` or memory file?**
No. Memory piles up sideways and nobody ever checks it. This tree is forced to go deep (one split rule per level, a floor test before anything counts as done), it won't copy what's already written, and the exam keeps showing exactly where it's wrong. That's why the tree alone is enough to answer from.

**Does anything get uploaded?**
Nothing beyond your normal Claude Code session. The clone home is a local git folder with no remote, and the generated permissions block web search, `git push` and reading secrets.

**How long until it's useful?**
The first `/survey` plus a few dozen grows gets you a usable map. The real bar is "can replace" on a replayed ticket, and the exam log will tell you honestly how far off that is.

**Can I use it outside engineering?**
Yes. The facets (work · practice · systems · env · org) fit pretty much any desk job. Rename them in `tree/` and `RULES.md`.

## Star history

<a href="https://star-history.com/#LazyerIJ/self-clone&Date"><img src="https://api.star-history.com/svg?repos=LazyerIJ/self-clone&type=Date" width="600" alt="Star history chart" /></a>

## License

MIT
