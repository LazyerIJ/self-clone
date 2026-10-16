#!/usr/bin/env python3
"""Prints the clone home's permission settings as JSON (clone-init writes it to .claude/settings.json).
Sources are read-only, secrets are never read, nothing is pushed. Roots come from clone.json.

  python3 -I tools/settings.py > .claude/settings.json

Connected MCP servers differ per person: after /survey, add their *write* tools to `deny`
(send_message, create_*, update_*, delete_*, execute_query …) and their read tools to `allow`.
"""
import json
import os

H = os.path.expanduser("~")
HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(HOME, "clone.json"), encoding="utf-8"))


def x(p):
    return os.path.expanduser(p).rstrip("/")


roots = [x(p) for p in CFG.get("work_roots", []) + CFG.get("notes_dirs", []) + CFG.get("extra_read_dirs", [])]
dirs = roots + [f"{H}/.claude", f"{H}/.codex/sessions"]

allow = [
    "Bash(python3 -I tools/tree.py:*)", "Bash(python3 -I tools/inventory.py:*)",
    "Bash(git add:*)", "Bash(git commit:*)", "Bash(git mv:*)", "Bash(git status:*)", "Bash(git --no-pager:*)",
    "Bash(git -C:*)", "Bash(ls:*)", "Bash(wc:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(grep:*)", "Bash(find:*)", "Bash(sed -n:*)",
    f"Read({H}/.claude/projects/**)", f"Read({H}/.claude/history.jsonl)", f"Read({H}/.zsh_history)", f"Read({H}/.bash_history)",
    "Edit(./tree/**)", "Write(./tree/**)", "Write(./sources/**)", "Edit(./exams/**)", "Write(./exams/**)",
] + [f"Read({r}/**)" for r in roots]

deny = [
    "Read(**/.env*)", "Read(**/*.pem)", "Read(**/*.key)", "Read(**/*.p12)", "Read(**/id_rsa*)", "Read(**/id_ed25519*)",
    "Read(**/.mcp.json)", f"Read({H}/.claude.json)", f"Read({H}/.config/**)", f"Read({H}/.aws/**)", f"Read({H}/.kube/**)",
    f"Read({H}/.netrc)", f"Read({H}/.codex/config.toml)",
    "Bash(git push:*)", "Bash(git -C * push:*)", "Bash(git -C * commit:*)", "Bash(git -C * checkout:*)", "Bash(git -C * reset:*)",
    "Bash(env)", "Bash(printenv:*)",
    # internal names, ticket keys and code must not leak into a web search
    "WebSearch", "WebFetch",
] + [f"Read({x(p)})" for p in CFG.get("never_read", [])]

print(json.dumps({"permissions": {"additionalDirectories": dirs, "allow": allow, "deny": deny}}, ensure_ascii=False, indent=2))
