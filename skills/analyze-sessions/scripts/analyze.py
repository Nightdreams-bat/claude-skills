#!/usr/bin/env python3
"""Analyze local Claude Code session logs. Stdlib only."""
import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"

# Estimated USD per 1M tokens (input, output). Directional only.
PRICES = {
    "opus":   (15.0, 75.0),
    "sonnet": (3.0, 15.0),
    "haiku":  (0.80, 4.0),
}


def price_for(model: str):
    m = (model or "").lower()
    for key, p in PRICES.items():
        if key in m:
            return p
    return PRICES["sonnet"]


def iter_sessions(days=None, project=None):
    if not PROJECTS.exists():
        return
    cutoff = None
    if days:
        cutoff = time.time() - days * 86400
    for slug_dir in sorted(PROJECTS.iterdir()):
        if not slug_dir.is_dir():
            continue
        if project and project.lower() not in slug_dir.name.lower():
            continue
        for f in sorted(slug_dir.glob("*.jsonl")):
            if cutoff and f.stat().st_mtime < cutoff:
                continue
            yield slug_dir.name, f


def read_lines(f: Path):
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def rec_date(rec):
    ts = rec.get("timestamp")
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().date()
    except ValueError:
        return None


def usage_tokens(u):
    """Return (billable_input_equiv, output). Cache reads priced at 0.1x,
    cache writes at 1.25x, per Anthropic's published multipliers."""
    if not u:
        return 0, 0
    fresh = u.get("input_tokens", 0) or 0
    cread = u.get("cache_read_input_tokens", 0) or 0
    cwrite = u.get("cache_creation_input_tokens", 0) or 0
    inp = fresh + cwrite * 1.25 + cread * 0.10
    out = u.get("output_tokens", 0) or 0
    return inp, out


def cmd_cost(args):
    by_day = defaultdict(lambda: [0, 0, 0.0])
    by_model = defaultdict(lambda: [0, 0, 0.0])
    for _slug, f in iter_sessions(args.days, args.project):
        for rec in read_lines(f):
            if rec.get("type") != "assistant":
                continue
            msg = rec.get("message", {})
            model = msg.get("model", "?")
            inp, out = usage_tokens(msg.get("usage"))
            pin, pout = price_for(model)
            cost = inp / 1e6 * pin + out / 1e6 * pout
            d = rec_date(rec)
            key = d.isoformat() if d else "?"
            for bucket in (by_day[key], by_model[model]):
                bucket[0] += inp
                bucket[1] += out
                bucket[2] += cost
    _print_cost_table("By day", by_day)
    print()
    _print_cost_table("By model", by_model)
    total = sum(v[2] for v in by_day.values())
    print(f"\nEstimated total: ${total:.2f}  (directional, not billing-accurate)")


def _print_cost_table(title, d):
    print(f"{title}:")
    print(f"  {'key':<22} {'in tok':>12} {'out tok':>12} {'est $':>10}")
    for k in sorted(d):
        i, o, c = d[k]
        print(f"  {k:<22} {i:>12,} {o:>12,} {c:>10.2f}")


def cmd_tools(args):
    c = Counter()
    for _slug, f in iter_sessions(args.days, None):
        for rec in read_lines(f):
            if rec.get("type") != "assistant":
                continue
            for block in rec.get("message", {}).get("content", []) or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    c[block.get("name", "?")] += 1
    print(f"{'tool':<28} {'calls':>8}")
    for name, n in c.most_common():
        print(f"{name:<28} {n:>8,}")


def cmd_prompts(args):
    rows = []
    for slug, f in iter_sessions(args.days, None):
        for rec in read_lines(f):
            if rec.get("type") != "user":
                continue
            content = rec.get("message", {}).get("content")
            text = ""
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "text":
                        text = b.get("text", "")
                        break
            text = text.strip()
            if not text or text.startswith("<") or "tool_result" in text[:40]:
                continue
            first = text.splitlines()[0][:140]
            rows.append((rec.get("timestamp", ""), slug.replace("C--", "").replace("-", "/"), first))
    rows.sort(reverse=True)
    for ts, proj, first in rows[: args.top]:
        print(f"{ts[:16]:<17} {first}")


def cmd_sessions(args):
    print(f"{'date':<12} {'turns':>6} {'in tok':>12} {'out tok':>12} {'est $':>8}  project / session")
    out_rows = []
    for slug, f in iter_sessions(args.days, None):
        turns = tin = tout = 0
        cost = 0.0
        last = None
        for rec in read_lines(f):
            t = rec.get("type")
            if t == "user":
                turns += 1
            elif t == "assistant":
                msg = rec.get("message", {})
                i, o = usage_tokens(msg.get("usage"))
                pin, pout = price_for(msg.get("model", ""))
                cost += i / 1e6 * pin + o / 1e6 * pout
                tin += i
                tout += o
            d = rec_date(rec)
            if d:
                last = d
        out_rows.append((last.isoformat() if last else "?", turns, tin, tout, cost, slug, f.stem[:8]))
    for date, turns, tin, tout, cost, slug, sid in sorted(out_rows, reverse=True):
        print(f"{date:<12} {turns:>6} {tin:>12,} {tout:>12,} {cost:>8.2f}  {slug}/{sid}")


def cmd_render(args):
    target = args.session
    path = Path(target)
    if not path.exists():
        matches = list(PROJECTS.glob(f"*/{target}*.jsonl"))
        if not matches:
            print(f"No session file matching {target!r}", file=sys.stderr)
            return 1
        path = matches[0]
    for rec in read_lines(path):
        t = rec.get("type")
        if t not in ("user", "assistant"):
            continue
        msg = rec.get("message", {})
        content = msg.get("content")
        print(f"\n=== {t.upper()} {rec.get('timestamp', '')[:19]} ===")
        if isinstance(content, str):
            print(content)
        elif isinstance(content, list):
            for b in content:
                if not isinstance(b, dict):
                    continue
                bt = b.get("type")
                if bt == "text":
                    print(b.get("text", ""))
                elif bt == "thinking":
                    print(f"[thinking] {b.get('thinking', '')[:500]}")
                elif bt == "tool_use":
                    print(f"[tool_use {b.get('name')}] {json.dumps(b.get('input', {}))[:400]}")
                elif bt == "tool_result":
                    r = b.get("content", "")
                    if isinstance(r, list):
                        r = " ".join(x.get("text", "") for x in r if isinstance(x, dict))
                    print(f"[tool_result] {str(r)[:400]}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("cost")
    pc.add_argument("--days", type=int)
    pc.add_argument("--project")
    pc.set_defaults(func=cmd_cost)

    pt = sub.add_parser("tools")
    pt.add_argument("--days", type=int)
    pt.set_defaults(func=cmd_tools)

    pp = sub.add_parser("prompts")
    pp.add_argument("--days", type=int)
    pp.add_argument("--top", type=int, default=40)
    pp.set_defaults(func=cmd_prompts)

    ps = sub.add_parser("sessions")
    ps.add_argument("--days", type=int)
    ps.set_defaults(func=cmd_sessions)

    pr = sub.add_parser("render")
    pr.add_argument("session")
    pr.set_defaults(func=cmd_render)

    args = p.parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
