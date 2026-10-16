---
name: clone-init
description: Sets up a self-clone home — a local git folder holding the knowledge tree of how you work (tree/, tools/, sources/, exams/, RULES.md), so that /grow, /exam and /survey can start growing a clone of you as a user. Use for "/clone-init", "set up self-clone", "start a clone of me", "make a work tree of my job".
---

# clone-init — make the clone home

The clone home is a folder of its own (default `~/self-clone-home`). It is never inside a work repo, and it has no git remote.
This skill's base directory holds `template/` — copy from there.

## 1. Ask (one question block, only what cannot be guessed)
- Where to put the home (default `~/self-clone-home`). Stop if it exists and is not empty.
- The owner's name (how the tree should call them) and their git author string (for "my commits"; suggest `git config user.name`).
- Work roots — folders that hold their repos (suggest the ones that exist among `~/code`, `~/src`, `~/projects`, `~/dev`, `~/work`).
- Notes folders (Obsidian vaults etc.) and folders that must never be read (customer data, personal).

## 2. Copy and fill
```
cp -R <base>/template/ <home>/
mv <home>/gitignore <home>/.gitignore
```
- Write the answers into `<home>/clone.json` (`owner`, `git_author`, `work_roots`, `notes_dirs`, `never_read`). Keep `session_match` as the last path segment of each work root (Claude project folder names contain it).
- Replace `checked: 2000-01-01` with today in every `tree/**/_branch.md`.
- `printf '@RULES.md\n' > <home>/CLAUDE.md`
- `mkdir -p <home>/.claude && python3 -I <home>/tools/settings.py > <home>/.claude/settings.json` — if your permission settings block the write to `.claude/`, print the command and ask the owner to run it.

## 3. First commit
```
cd <home> && git init -q && python3 -I tools/tree.py lint && git add -A && git commit -q -m "init: self-clone home"
```

## 4. Report
Tell the owner, in a few lines:
- the home path, and that every later command runs **from a Claude Code session opened in that folder** (`cd <home> && claude`)
- next steps: `/survey` (map of sources and access) → `/grow` (one node) → `/loop /grow` (keep growing) → `/exam` comes up by itself
- `tools/shape.json` holds every limit (depth, children, sections); `RULES.md` is the constitution and can be edited
- after /survey, add the write tools of their connected MCP servers to `deny` in `tools/settings.py` and regenerate settings
