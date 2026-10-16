#!/usr/bin/env python3
"""Local source inventory — counts only 'where, how much, when' of the work traces on this machine. It never reads content.

  python3 -I tools/inventory.py > sources/local.md

Anything that could be a secret is not even named: shell commands keep only their first word, ssh keeps only Host aliases.
External systems (issue tracker, chat, code host, wiki, error tracker) are not counted here — that is /survey's job.
Roots and filters come from clone.json.
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
from collections import Counter

H = os.path.expanduser("~")
HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(HOME, "clone.json"), encoding="utf-8"))
SKIP_DIRS = {"node_modules", ".venv", "venv", ".git", "__pycache__", "dist", "build"}


def x(p):
    return os.path.expanduser(p)


def day(ts):
    return dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def git(repo, *args):
    try:
        return subprocess.run(["git", "-C", repo, "--no-pager", *args], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def is_repo(p):
    return os.path.exists(os.path.join(p, ".git"))


def repo_line(path):
    rel = os.path.relpath(path, H)
    marks = [m for m, p in ((".claude", ".claude"), ("CLAUDE.md", "CLAUDE.md"), ("AGENTS.md", "AGENTS.md")) if os.path.exists(os.path.join(path, p))]
    hd = [w for w in CFG.get("harness_dirs", []) if os.path.isdir(os.path.join(path, w))]
    hn = sum(len(os.listdir(os.path.join(path, w))) for w in hd)
    if is_repo(path):
        last = git(path, "log", "-1", "--format=%cs")
        author = CFG.get("git_author") or ""
        mine = git(path, "log", f"--author={author}", "--format=%cs").splitlines() if author else []
        span = f"{mine[-1]}~{mine[0]}" if mine else "-"
        remote = re.sub(r"//[^@/]+@", "//", git(path, "remote", "get-url", "origin"))
        return f"| `~/{rel}` | git | {last or '-'} | {len(mine)} ({span}) | {' '.join(marks) or '-'} | {hn or '-'} | {remote or '-'} |"
    return f"| `~/{rel}` | folder | {day(os.path.getmtime(path))} | - | {' '.join(marks) or '-'} | {hn or '-'} | - |"


def work_dirs():
    """Folders under each work root down to work_root_depth; stops descending at git repos."""
    out, maxd = [], CFG.get("work_root_depth", 2)

    def visit(p, d):
        out.append(p)
        if d >= maxd or is_repo(p):
            return
        for sub in sorted(os.listdir(p)):
            sp = os.path.join(p, sub)
            if os.path.isdir(sp) and not sub.startswith(".") and sub not in SKIP_DIRS:
                visit(sp, d + 1)

    for root in CFG.get("work_roots", []):
        r = x(root)
        if not os.path.isdir(r):
            continue
        for top in sorted(os.listdir(r)):
            p = os.path.join(r, top)
            if os.path.isdir(p) and not top.startswith("."):
                visit(p, 1)
    return out


def claude_projects():
    rows, keys = [], CFG.get("session_match", [])
    for d in sorted(glob.glob(os.path.join(H, ".claude", "projects", "*"))):
        name = os.path.basename(d)
        if keys and not any(k in name for k in keys):
            continue
        js = glob.glob(os.path.join(d, "*.jsonl"))
        mem = glob.glob(os.path.join(d, "memory", "*.md"))
        if not js and not mem:
            continue
        size = sum(os.path.getsize(j) for j in js) / 1e6
        times = sorted(os.path.getmtime(j) for j in js)
        span = f"{day(times[0])}~{day(times[-1])}" if times else "-"
        rows.append(f"| `{name}` | {len(js)} | {size:.0f}MB | {span} | {len(mem)} |")
    return rows


def history():
    p = os.path.join(H, ".claude", "history.jsonl")
    if not os.path.exists(p):
        return ["(none)"]
    per, first, last = Counter(), None, None
    for line in open(p, encoding="utf-8", errors="ignore"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        proj = (r.get("project") or "?").replace(H, "~")
        ts = r.get("timestamp")
        if isinstance(ts, (int, float)):
            t = ts / 1000 if ts > 1e12 else ts
            first = t if first is None or t < first else first
            last = t if last is None or t > last else last
        per[proj] += 1
    head = f"{sum(per.values())} lines · {day(first) if first else '?'}~{day(last) if last else '?'}"
    return [head, "", "| project | prompts |", "|---|---|", *[f"| `{k}` | {v} |" for k, v in per.most_common(40)]]


def codex():
    c = Counter()
    for f in glob.glob(os.path.join(H, ".codex", "sessions", "*", "*", "*", "*.jsonl")):
        c[f.split(os.sep)[-4] + "-" + f.split(os.sep)[-3]] += 1
    return [f"| {k} | {v} |" for k, v in sorted(c.items())] or ["| (none) | |"]


def shell():
    for name in (".zsh_history", ".bash_history"):
        p = os.path.join(H, name)
        if os.path.exists(p):
            break
    else:
        return ["(none)"]
    c, ts = Counter(), []
    for line in open(p, encoding="utf-8", errors="ignore"):
        m = re.match(r"^: (\d+):\d+;(.*)", line)
        cmd = m.group(2) if m else line
        if m:
            ts.append(int(m.group(1)))
        tok = cmd.strip().split(" ", 1)[0] if cmd.strip() else ""
        if tok and re.match(r"^[A-Za-z0-9_./][A-Za-z0-9_./-]*$", tok) and "=" not in tok:
            c[os.path.basename(tok)] += 1
    span = f"{day(min(ts))}~{day(max(ts))}" if ts else "no timestamps"
    return [f"`~/{name}` {sum(c.values())} lines · {span} · top 50 first words (arguments are never copied)", "",
            ", ".join(f"`{k}` {v}" for k, v in c.most_common(50))]


def ssh_hosts():
    p = os.path.join(H, ".ssh", "config")
    if not os.path.exists(p):
        return "(none)"
    hosts = []
    for line in open(p, encoding="utf-8", errors="ignore"):
        m = re.match(r"^\s*Host\s+(.+)", line)
        if m:
            hosts += [h for h in m.group(1).split() if "*" not in h and not re.match(r"^[0-9.:]+$", h)]
    return ", ".join(f"`{h}`" for h in dict.fromkeys(hosts)) or "(none)"


def apps():
    d = "/Applications"
    return ", ".join(sorted(a[:-4] for a in os.listdir(d) if a.endswith(".app"))) if os.path.isdir(d) else "(not macOS)"


def main():
    print(f"# Local source inventory (generated {dt.date.today()} by `tools/inventory.py` — do not edit by hand)\n")
    print("## Work folders (clone.json work_roots)\n")
    print("| path | kind | last change | my commits (span) | harness | harness outputs | origin |")
    print("|---|---|---|---|---|---|---|")
    for p in work_dirs():
        print(repo_line(p))
    print("\n## Claude sessions and auto-memory (~/.claude/projects)\n")
    print("| project folder | sessions | size | span | memory |")
    print("|---|---|---|---|---|")
    print("\n".join(claude_projects()))
    print("\n## Prompt history (~/.claude/history.jsonl)\n")
    print("\n".join(history()))
    print("\n## Codex sessions (~/.codex/sessions, per month)\n")
    print("| month | sessions |\n|---|---|")
    print("\n".join(codex()))
    print("\n## Shell history\n")
    print("\n".join(shell()))
    print("\n## Network and access\n")
    print(f"- ssh Host aliases: {ssh_hosts()}")
    print("\n## Apps and global tools\n")
    print(f"- apps: {apps()}")
    print(f"- global skills (~/.claude/skills): {', '.join(f'`{os.path.basename(d)}`' for d in sorted(glob.glob(os.path.join(H, '.claude', 'skills', '*')))) or '(none)'}")
    for nd in CFG.get("notes_dirs", []):
        p = x(nd)
        items = sorted(v for v in os.listdir(p) if not v.startswith(".")) if os.path.isdir(p) else []
        print(f"- notes `{nd}`: {', '.join(items) or '(none)'}")


if __name__ == "__main__":
    main()
