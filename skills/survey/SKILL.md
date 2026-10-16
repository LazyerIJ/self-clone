---
name: survey
description: Refreshes the self-clone source map — the local source list (inventory.py), the access paths to external work systems (sources/access.md), and how far the owner is involved in each external system (sources/external.md). Use for "/survey", "refresh sources", "check connections", and for @survey in the frontier.
---

# survey — what is where and how to reach it (a map, not content)

Run from the clone home.

## 1. Local
```
python3 -I tools/inventory.py > sources/local.md
```

## 2. Access paths — `sources/access.md`
For every work system, find **a read tool that carries its own credentials** and confirm it once with a harmless read. Never look at or write down credential values.

Look at what this session actually has: connected MCP servers (their tool list), authenticated CLIs (`gh auth status`, `glab auth status`, `aws sts get-caller-identity`…), and plugins. Typical rows:

| system | tool | check call |
|---|---|---|
| issue tracker (Jira, Linear, GitHub Issues…) | MCP or authenticated CLI | who-am-I |
| wiki (Confluence, Notion…) | MCP or CLI | who-am-I · list spaces |
| chat (Slack, Teams…) | MCP | read own profile |
| code host (GitHub, GitLab…) | `gh` / `glab` | current user |
| error tracker (Sentry…) | MCP | list organisations — if unauthenticated: "human hand: authenticate in `/mcp`" |
| dashboards (Metabase, Grafana…) | MCP | list databases/dashboards |
| notes (Obsidian…) | MCP or the folder itself | list files |
| other | server **names and kinds only** from `.mcp.json` / `~/.claude.json` (never values) | — |

Shape of `sources/access.md`: system | tool | status (✓/✗/human hand) | why blocked | checked at.
- A system whose credentials exist on this machine but has no such tool (e.g. a key only in some config file) is written only as "credential location: <path> — not connected, human hand". **Never pull that key out.**
- For every working MCP server, note which of its tools write (send, create, update, delete, run query). Remind the owner to deny them in `tools/settings.py`.

## 3. Scope — `sources/external.md` (read only; scope, volume, period only)
| system | what to count |
|---|---|
| issue tracker | project keys of issues the owner was assignee/reporter/commenter on, period, status mix, epic/component/label names |
| wiki | space keys and names, pages the owner wrote — count and topics |
| chat | channels the owner is in with a one-line purpose, the channels they talk most in, the people they talk with most (by role) |
| code host | projects the owner committed to or opened MRs in, group structure, MR count and period |
| error tracker | organisation and project names, issue volume |
| dashboards | collection/dashboard names (what is watched as a metric) |

Shape: one section per system, a table (scope · volume · period · candidate tree link), and a final "not reachable" list.

## 4. Feed the tree
If a newly seen area is not in the tree, add one line to **the `## Candidates` of the closest existing branch** (do not create branches — that is /grow's job).
```
python3 -I tools/tree.py lint && git add -A sources tree && git commit -q -m "survey: <summary>"
```
