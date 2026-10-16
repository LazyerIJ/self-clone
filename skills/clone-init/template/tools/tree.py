#!/usr/bin/env python3
"""self-clone shape tool — it never judges content. Shape checks, next-node picking, stats and skeletons only.

  python3 -I tools/tree.py lint [--under P]            shape violations + floor misses on nodes touched this step (exit 1 if any)
  python3 -I tools/tree.py frontier [-n N] [--under P]  next steps (violation → @exam → exam holes → pinned cases → below floor → stub → unknowns → refresh; never empty)
  python3 -I tools/tree.py floor [--under P]           settled nodes that miss the floor test (shape.json floor)
  python3 -I tools/tree.py show <path>                 ancestor context + node + children + siblings (the input of one grow step)
  python3 -I tools/tree.py new <path> <title>          branch skeleton (stub)
  python3 -I tools/tree.py stats                       depth, branch count, leaves, state distribution
<path> is relative to tree/ (e.g. systems/billing). The root is '.'.
Section headings, exam-line format and all limits live in tools/shape.json.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import Counter

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREE = os.path.join(HOME, "tree")
SHAPE = json.load(open(os.path.join(HOME, "tools", "shape.json"), encoding="utf-8"))
SLUG = re.compile(SHAPE["slug"])
S = SHAPE["sections"]
REL_LINE = re.compile(r"^-\s*([a-z]+)\s*:\s*(\S+)")
POINTER = re.compile(r"[A-Z][A-Z0-9]+-\d+|`[^`]+`|#\S+|\b[0-9a-f]{7,40}\b|https?://")
EXAM = re.compile(SHAPE["exam_line"], re.I)
UNSURE = [w.lower() for w in SHAPE.get("unsure_words", [])]
PATH_PTR = re.compile(r"`(~?/[^`*?\s]+)`")


def sect(sec, key):
    return sec.get(S[key])


def parse(path):
    text = open(path, encoding="utf-8").read()
    head, body = {}, text
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    head[k.strip()] = v.strip()
            body = text[end + 4:].lstrip("\n")
    sections, cur = {}, None
    for line in body.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            sections[cur] = []
        elif cur is not None and line.strip():
            sections[cur].append(line.rstrip())
    return head, body, sections


def walk():
    """(rel_dir, subdirs, leaves) — hidden folders are skipped."""
    for root, dirs, files in os.walk(TREE):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        rel = os.path.relpath(root, TREE)
        leaves = sorted(f for f in files if f.endswith(".md") and f != "_branch.md")
        yield rel, dirs, leaves


def depth(rel):
    return 0 if rel == "." else rel.count("/") + 1


def under_ok(rel, under):
    return not under or rel == under or rel.startswith(under.rstrip("/") + "/")


def days_ago(day_str):
    try:
        return (dt.date.today() - dt.date.fromisoformat(day_str)).days
    except Exception:
        return None


def changed_nodes():
    """Branches changed or added since HEAD — the nodes this step touched."""
    r = subprocess.run(["git", "-C", HOME, "status", "--porcelain", "--untracked-files=all", "--", "tree"], capture_output=True, text=True)
    out = set()
    for line in r.stdout.splitlines():
        path = line[3:].split(" -> ")[-1].strip().strip('"')
        if path.startswith("tree/"):
            out.add(os.path.dirname(path[5:]) or ".")
    return out


def floor_fail(rel, sec, dirs):
    """Why a settled node misses the machine-checkable part of the floor test. Content judgement (one thing, doable as-is) is grow's job."""
    F = SHAPE["floor"]
    why = []
    if dirs:
        for d in dirs:
            bp = os.path.join(TREE, rel, d, "_branch.md")
            if os.path.exists(bp) and parse(bp)[0].get("state") != "settled":
                why.append(f"child {d} not settled")
        return why
    md = F.get("min_depth_by_facet", {}).get(rel.split("/")[0], F["min_depth"])
    if depth(rel) < md:
        why.append(f"depth {depth(rel)} < {md} — there is still a split left")
    for k in F["sections"]:
        if not sect(sec, k):
            why.append(f"no '## {S[k]}'")
    ev = [l for l in sect(sec, "evidence") or [] if l.lstrip().startswith("-")]
    if len(ev) < SHAPE["settled_min_evidence"]:
        why.append(f"evidence {len(ev)} < {SHAPE['settled_min_evidence']}")
    if sect(sec, "cases") is not None:
        cases = [l for l in sect(sec, "cases") if l.lstrip().startswith("-") and POINTER.search(l)]
        if len(cases) < F["min_cases"]:
            why.append(f"cases with a pointer {len(cases)} < {F['min_cases']}")
    if sect(sec, "exam") is not None:
        ms = [EXAM.match(l.strip()) for l in sect(sec, "exam")]
        ok = [m for m in ms if m and not any(w in m.group(2).lower() for w in UNSURE)]
        if len(ok) < F["min_exam"]:
            why.append(f"answered exam items {len(ok)} < {F['min_exam']} ('- Q: … A: …')")
    run = sect(sec, "run") or []
    items = [l for l in run if l.startswith("- ")]
    if len(items) > F["max_exec_items"]:
        why.append(f"run items {len(items)} > {F['max_exec_items']} — push each transition/step/decision down into a child")
    syms = set(re.findall(F["code_symbol_regex"], "\n".join(run + (sect(sec, "what") or []))))
    if len(syms) > F["max_symbols"]:
        why.append(f"{len(syms)} code symbols in run — code and logic belong to the repo harness; replace with 'ask the <repo> harness'")
    what = " ".join(sect(sec, "what") or [])
    hits = [w for w in F["bundle_words"] if w in what]
    if hits:
        why.append(f"bundle signal in what {hits} — one child per step/branch")
    return why


def check_rels(where, base, sec, errs):
    for line in sect(sec, "relations") or []:
        m = REL_LINE.match(line.strip())
        if not m:
            errs.append(f"{where}: relation line must be '- <rel>: <relative path>' ({line.strip()[:40]})")
            continue
        rel, target = m.groups()
        if rel not in SHAPE["rels"]:
            errs.append(f"{where}: relation '{rel}' is not in {SHAPE['rels']}")
        if not os.path.exists(os.path.normpath(os.path.join(base, target))):
            errs.append(f"{where}: relation target missing {target}")


def lint(under=None):
    errs, warns, stems, below = [], [], {}, []
    changed = changed_nodes()
    for rel, dirs, leaves in walk():
        if not under_ok(rel, under):
            continue
        bpath = os.path.join(TREE, rel, "_branch.md")
        if rel != "." and not SLUG.match(os.path.basename(rel)):
            errs.append(f"{rel}: branch name breaks the slug rule ({SHAPE['slug']})")
        if not os.path.exists(bpath):
            errs.append(f"{rel}: no _branch.md")
            continue
        head, body, sec = parse(bpath)
        state = head.get("state", "")
        if head.get("kind") != "branch":
            errs.append(f"{rel}/_branch.md: needs kind: branch")
        if not head.get("title"):
            errs.append(f"{rel}/_branch.md: needs a title")
        if head.get("checked") and days_ago(head["checked"]) is None:
            errs.append(f"{rel}/_branch.md: checked must be YYYY-MM-DD")
        if state not in SHAPE["branch_states"]:
            errs.append(f"{rel}/_branch.md: state must be one of {SHAPE['branch_states']}")
        for k in SHAPE["branch_sections_required"].get(state, []):
            if not sect(sec, k):
                errs.append(f"{rel}/_branch.md: '## {S[k]}' is empty (state={state})")
        n = len(body.splitlines())
        if n > SHAPE["max_body_lines"]:
            errs.append(f"{rel}/_branch.md: body {n} lines > {SHAPE['max_body_lines']} — split it into children")
        kids = len(dirs) + len(leaves)
        sh = SHAPE.get("max_children_shallow", {})
        cap = sh["max"] if depth(rel) < sh.get("depth_below", 0) else SHAPE["max_children"]
        if kids > cap:
            errs.append(f"{rel}: {kids} children > {cap} — group them under a higher concept, one level down")
        if rel != "." and len(dirs) == 1 and not leaves:
            errs.append(f"{rel}: only one child branch — that is not a split. Split into two or more, or merge the child up")
        if len(leaves) > SHAPE["max_leaves"]:
            errs.append(f"{rel}: {len(leaves)} leaves > {SHAPE['max_leaves']} — turn leaves into branches or merge them")
        if state == "settled" and sect(sec, "unknown"):
            errs.append(f"{rel}/_branch.md: settled but '## {S['unknown']}' is not empty — set growing")
        if state == "settled":
            ff = floor_fail(rel, sec, dirs)
            if ff and rel in changed:
                errs.append(f"{rel}/_branch.md: settled but below floor — {'; '.join(ff)} (set growing if you can't fill it)")
            elif ff:
                below.append((rel, ff))
        if state == "growing" and kids == 0 and not sect(sec, "unknown"):
            warns.append(f"{rel}: growing with no children and no unknowns — settle it or split it")
        check_rels(rel, os.path.join(TREE, rel), sec, errs)
        for leaf in leaves:
            stem = leaf[:-3]
            lp = os.path.join(TREE, rel, leaf)
            if not SLUG.match(stem):
                errs.append(f"{rel}/{leaf}: leaf name breaks the slug rule")
            if stem in stems:
                errs.append(f"{rel}/{leaf}: duplicate leaf name ({stems[stem]})")
            stems[stem] = rel
            lh, lbody, lsec = parse(lp)
            if lh.get("kind") not in SHAPE["leaf_kinds"]:
                errs.append(f"{rel}/{leaf}: kind must be one of {SHAPE['leaf_kinds']}")
            if not lh.get("title"):
                errs.append(f"{rel}/{leaf}: needs a title")
            if len(lbody.splitlines()) > SHAPE["max_body_lines"]:
                errs.append(f"{rel}/{leaf}: body over {SHAPE['max_body_lines']} lines")
            check_rels(f"{rel}/{leaf}", os.path.join(TREE, rel), lsec, errs)
    return errs, warns, below


def changed_since(sec, checked):
    """Local path pointers in evidence that changed after the checked date (last commit for git repos, mtime otherwise)."""
    if not checked:
        return []
    try:
        cut = dt.datetime.combine(dt.date.fromisoformat(checked) + dt.timedelta(days=1), dt.time()).timestamp()
    except Exception:
        return []
    hits = []
    for line in sect(sec, "evidence") or []:
        for raw in PATH_PTR.findall(line):
            p = os.path.expanduser(raw.rstrip("/"))
            if not os.path.exists(p):
                continue
            t = os.path.getmtime(p)
            if os.path.isdir(os.path.join(p, ".git")):
                r = subprocess.run(["git", "-C", p, "--no-pager", "log", "-1", "--format=%ct"], capture_output=True, text=True)
                t = int(r.stdout.strip() or 0)
            if t >= cut:
                hits.append(raw)
    return hits


def grows_since_exam():
    r = subprocess.run(["git", "-C", HOME, "--no-pager", "log", "--format=%s", "-300"], capture_output=True, text=True)
    n = 0
    for s in r.stdout.splitlines():
        if s.startswith("exam"):
            return n
        if s.startswith("grow"):
            n += 1
    return n


def marked(sec, tag):
    return [l for k in ("unknown", "candidates") for l in sect(sec, k) or [] if f"[{tag}" in l]


def frontier(n, under=None):
    """Priority: 0 shape violation → 1 @exam (after exam_every grows) → 1.5 exam holes ([exam] lines) → 1.6 pinned cases ([case] lines)
    → 2 settled below floor (shallow first) → 3 stub → 4 growing with unknowns → 5 sources changed → 6 parent whose children all settled
    → 7 refresh nodes not looked at for a while. '@survey' goes first when the source map is old. Empty → @exam: the frontier is never empty.
    With --under (parallel loops) there is no @survey/@exam."""
    errs, _, below = lint(under)
    out, seen = [], set()
    local = os.path.join(HOME, "sources", "local.md")
    sv = (dt.date.today() - dt.date.fromtimestamp(os.path.getmtime(local))).days if os.path.exists(local) else 999
    if not under and sv >= SHAPE.get("survey_days", 7):
        out.append((-1, 0, 0, "@survey", f"source map is {sv} days old — run the /survey procedure first"))
    g = grows_since_exam()
    if not under and g >= SHAPE.get("exam_every", 10):
        out.append((1, 0, 0, "@exam", f"{g} grows since the last exam — /exam: solve real work from the tree alone and find holes"))
    for rel, dirs, leaves in walk():
        bpath = os.path.join(TREE, rel, "_branch.md")
        if rel in seen or not os.path.exists(bpath) or not under_ok(rel, under):
            continue
        sec = parse(bpath)[2]
        holes = marked(sec, "exam")
        if holes:
            seen.add(rel)
            out.append((1.5, -len(holes), depth(rel), rel, f"exam holes {len(holes)} — fill the [exam] lines first"))
            continue
        cases = marked(sec, "case")
        if cases:
            seen.add(rel)
            out.append((1.6, -len(cases), depth(rel), rel, f"pinned cases {len(cases)} — fold the [case] lines in first"))
    for rel, ff in below:
        if rel not in seen:
            seen.add(rel)
            out.append((2, depth(rel), -len(ff), rel, "below floor: " + "; ".join(ff[:3])))
    for e in errs:
        node = e.split(":", 1)[0].replace("/_branch.md", "")
        if node.endswith(".md"):
            node = os.path.dirname(node) or "."
        if node not in seen:
            seen.add(node)
            out.append((0, depth(node), 0, node, "violation: " + e.split(":", 1)[1].strip()))
    revisit = SHAPE.get("revisit_days", 14)
    for rel, dirs, leaves in walk():
        bpath = os.path.join(TREE, rel, "_branch.md")
        if rel in seen or not os.path.exists(bpath) or not under_ok(rel, under):
            continue
        head, _, sec = parse(bpath)
        st = head.get("state")
        unknown = len(sect(sec, "unknown") or [])
        checked = head.get("checked", "")
        age = days_ago(checked)
        if st == "stub":
            out.append((3, depth(rel), -unknown, rel, f"stub, unknowns {unknown}"))
            continue
        if st == "growing" and unknown:
            out.append((4, depth(rel), -unknown, rel, f"growing, unknowns {unknown}"))
            continue
        ch = changed_since(sec, checked)
        if ch:
            out.append((5, depth(rel), -len(ch), rel, f"refresh: sources changed {', '.join(ch[:3])}"))
            continue
        if st == "growing" and dirs:
            kids = [parse(os.path.join(TREE, rel, d, "_branch.md"))[0] for d in dirs if os.path.exists(os.path.join(TREE, rel, d, "_branch.md"))]
            if kids and all(k.get("state") == "settled" for k in kids) and any(k.get("checked", "") > checked for k in kids):
                out.append((6, depth(rel), 0, rel, "review: all children settled — recheck split, boundary and relations, then settle"))
                continue
        if age is None or age >= revisit:
            out.append((7, -(age if age is not None else 9999), depth(rel), rel, f"refresh: last checked {checked or 'never'}"))
    out.sort()
    for _, _, _, rel, why in out[:n]:
        print(f"{rel}\t(depth {depth(rel) if not rel.startswith('@') else '-'}) {why}")
    if not out:
        if under:
            print("(frontier empty in this range — widen the range or /exam)")
        else:
            print("@exam\t(depth -) nothing left to do — /exam: solve harder real work and find holes")


def title_of(rel):
    p = os.path.join(TREE, rel, "_branch.md")
    if not os.path.exists(p):
        return "?"
    h = parse(p)[0]
    return f"{h.get('title', '?')} [{h.get('state', '?')}]"


def show(rel):
    rel = os.path.normpath(rel)
    parts = [] if rel == "." else rel.split("/")
    print("# Ancestors")
    for i in range(len(parts)):
        anc = "/".join(parts[:i]) or "."
        what = " ".join(sect(parse(os.path.join(TREE, anc, "_branch.md"))[2], "what") or [])[:200]
        print(f"- {anc}: {title_of(anc)} — {what}")
    print(f"\n# Node {rel}/_branch.md\n")
    print(open(os.path.join(TREE, rel, "_branch.md"), encoding="utf-8").read())
    d = os.path.join(TREE, rel)
    kids = sorted(k for k in os.listdir(d) if not k.startswith(".") and k != "_branch.md")
    print("# Children")
    for k in kids:
        if os.path.isdir(os.path.join(d, k)):
            print(f"- {k}/: {title_of(os.path.join(rel, k))}")
        elif k.endswith(".md"):
            lh = parse(os.path.join(d, k))[0]
            print(f"- {k} (leaf {lh.get('kind', '?')}): {lh.get('title', '?')}")
    if not kids:
        print("- (none)")
    if parts:
        par = "/".join(parts[:-1]) or "."
        sib = sorted(s for s in os.listdir(os.path.join(TREE, par)) if os.path.isdir(os.path.join(TREE, par, s)) and not s.startswith(".") and s != parts[-1])
        print("\n# Siblings")
        for s in sib:
            print(f"- {s}/: {title_of(os.path.join(par, s))}")
        if not sib:
            print("- (none)")


def new(rel, title):
    rel = os.path.normpath(rel)
    d = os.path.join(TREE, rel)
    parent = os.path.dirname(d)
    if not os.path.exists(os.path.join(parent, "_branch.md")):
        sys.exit(f"no parent branch: {os.path.relpath(parent, TREE)}")
    if not SLUG.match(os.path.basename(rel)):
        sys.exit(f"slug rule broken: {os.path.basename(rel)}")
    if os.path.exists(d):
        sys.exit(f"already exists: {rel}")
    os.makedirs(d)
    body = "".join(f"\n## {S[k]}\n" + ("(one or two lines)\n" if k == "what" else "") for k in ("what", "boundary", "evidence", "relations", "unknown"))
    with open(os.path.join(d, "_branch.md"), "w", encoding="utf-8") as f:
        f.write(f"---\nkind: branch\ntitle: {title}\nstate: stub\nchecked: {dt.date.today()}\n---\n{body}")
    print(f"created: {rel}/_branch.md (stub)")


def stats():
    st, depths, fan, leaves_n, branches = Counter(), [], Counter(), 0, 0
    for rel, dirs, leaves in walk():
        branches += 1
        bp = os.path.join(TREE, rel, "_branch.md")
        h = parse(bp)[0] if os.path.exists(bp) else {}
        st[h.get("state", "?")] += 1
        fan[len(dirs) + len(leaves)] += 1
        leaves_n += len(leaves)
        if not dirs:
            depths.append(depth(rel))
    print(f"branches {branches} · leaves {leaves_n} · states {dict(st)}")
    if depths:
        print(f"end-branch depth: max {max(depths)} · mean {sum(depths)/len(depths):.2f} · distribution {dict(sorted(Counter(depths).items()))}")
    print(f"children distribution: {dict(sorted(fan.items()))}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd, under = a[0], None
    if "--under" in a:
        i = a.index("--under")
        under = os.path.normpath(a[i + 1])
        del a[i:i + 2]
    if cmd == "lint":
        e, w, b = lint(under)
        for x in e:
            print("E", x)
        for x in w:
            print("W", x)
        print(f"violations {len(e)} · warnings {len(w)} · below floor (untouched settled) {len(b)}")
        sys.exit(1 if e else 0)
    elif cmd == "floor":
        for rel, ff in lint(under)[2]:
            print(f"{rel}\t{'; '.join(ff)}")
    elif cmd == "frontier":
        frontier(int(a[2]) if len(a) > 2 and a[1] == "-n" else 10, under)
    elif cmd == "show":
        show(a[1] if len(a) > 1 else ".")
    elif cmd == "new":
        new(a[1], " ".join(a[2:]))
    elif cmd == "stats":
        stats()
    else:
        sys.exit(__doc__)
