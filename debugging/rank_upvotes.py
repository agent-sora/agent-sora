#!/usr/bin/env python3
"""Re-pull true upvote counts from the HuggingFace daily-papers API for every
candidate (full feed + shortlist) for a given papers_date, rank them, and write
the top 6 arxiv ids to episodes/feed/picks/ids-<date>.txt.

Usage: .venv/bin/python debugging/rank_upvotes.py <papers_date>
"""
import json
import sys
import urllib.request
from pathlib import Path

PC = Path("/home/patrick/papercast")


def main() -> None:
    d = sys.argv[1]
    raw = json.load(open(PC / f"episodes/feed/papers-{d}.json"))
    feed = raw["papers"] if isinstance(raw, dict) else raw
    sel = json.load(open(PC / f"episodes/feed/selected-{d}.json"))
    cands = sorted({p["arxiv_id"] for p in feed} | {p["arxiv_id"] for p in sel})
    print("CANDIDATES:", cands)

    rows = []
    for pid in cands:
        try:
            with urllib.request.urlopen(
                f"https://huggingface.co/api/papers/{pid}", timeout=30
            ) as r:
                data = json.load(r)
            rows.append(
                (
                    int(data.get("upvotes", 0)),
                    pid,
                    data.get("title", "?"),
                    data.get("publishedAt"),
                )
            )
        except Exception as e:  # noqa: BLE001
            rows.append((None, pid, f"ERR {e}", None))

    rows.sort(key=lambda x: (x[0] is None, -(x[0] or 0)))
    print("\nTRUE UPVOTES (desc):")
    for up, pid, title, pub in rows:
        print(f"  {up}\t{pid}\t{title}")

    picks_dir = PC / "episodes/feed/picks"
    picks_dir.mkdir(parents=True, exist_ok=True)
    (picks_dir / f"upvotes-{d}.json").write_text(json.dumps(rows, indent=1))
    top6 = [pid for _, pid, _, _ in rows[:6]]
    (picks_dir / f"ids-{d}.txt").write_text("\n".join(top6) + "\n")
    print("\nTOP6 PICKS:", top6)


if __name__ == "__main__":
    main()
