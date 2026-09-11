#!/usr/bin/env python3
"""Scan the full daily feed for standing-rule papers that the top-6 cut may have
missed.

Standing rules (override the top-6 cut):
  a. FOUNDATION-MODEL TECH REPORTS: any paper introducing a NEW foundation model.
  b. REASONING-MODEL TOPOLOGY: papers on topological/architectural changes to
     reasoning LMs (looping/recurrent depth, weight tying, adaptive computation,
     alternative attention (linear/fast-weight/SSM), latent/continuous CoT).
     Closed-loop agents / human-in-the-loop do NOT qualify.

Prints every feed paper with its title + a summary window around any topology/
foundation-model keyword hit, so a human (or the cron agent) can judge whether
each hit is a true qualifying paper.

Usage: .venv/bin/python debugging/scan_standing_rules.py <papers_date>
"""
import json
import re
import sys
from pathlib import Path

PC = Path("/home/patrick/papercast")

# Architecture/topology patterns that CAN qualify under rule (b).
TOPO = [
    r"latent[- ]space (language|reasoning)",
    r"continuous (chain|thought|co[- ]?t)",
    r"latent (chain|thought|co[- ]?t|reasoning)",
    r"next[- ]concept",
    r"weight[- ]tied",
    r"recurrent (depth|transformer|language model|reasoning)",
    r"looping (transformer|language model|reasoning)",
    r"adaptive computation time|adaptive (depth|computation)",
    r"linear attention",
    r"fast[- ]weight",
    r"\bssm\b|state[- ]space model|state[- ]space sequence",
    r"mamba|hyena",
    r"recurrent depth",
    r"test[- ]time (training|adaptation|adaptation)",
    r"scaling test[- ]time",
]
# Foundation-model introduction patterns for rule (a).
FOUNDATION = [
    r"\bintroduc(e|es|ing)\b[^.]{0,120}\b(new|a)\b[^.]{0,80}foundation model",
    r"\bfoundation model\b[^.]{0,120}(introduc|present|release|launch|open[- ]sourc)",
    r"(we|introducing) (present|introduce|release)[^.]{0,80}\b(a )?(new|multi[- ]?modal|unified|omni|frontier)?\b model",
    r"technical report",
]
NEG = [r"human[- ]in[- ]the[- ]loop", r"closed[- ]loop (agent|policy|control|robot)",
       r"feedback loop"]


def main() -> None:
    d = sys.argv[1]
    raw = json.load(open(PC / f"episodes/feed/papers-{d}.json"))
    feed = raw["papers"] if isinstance(raw, dict) else raw
    print(f"FEED SIZE: {len(feed)}")
    for p in feed:
        text = (p.get("title", "") + " " + p.get("summary", "")).lower()
        hits = set()
        for pat in TOPO:
            if re.search(pat, text):
                hits.add("TOPO:" + pat[:30])
        for pat in FOUNDATION:
            if re.search(pat, text):
                hits.add("FOUND:" + pat[:30])
        negs = [pat for pat in NEG if re.search(pat, text)]
        if hits:
            print("=" * 78)
            print(f"{p['arxiv_id']}  upvotes={p.get('upvotes')}  {p.get('title','')[:90]}")
            print("  HITS:", "; ".join(sorted(hits)))
            if negs:
                print("  NEG-FLAGS:", "; ".join(negs))
            # show context windows
            t = p.get("summary", "")
            for pat in TOPO + FOUNDATION:
                for m in re.finditer(pat, t, re.IGNORECASE):
                    s, e = max(0, m.start() - 120), min(len(t), m.end() + 120)
                    print(f"  [{pat[:20]}] ...{t[s:e]}...")
                    break  # first hit per pattern is enough


if __name__ == "__main__":
    main()
