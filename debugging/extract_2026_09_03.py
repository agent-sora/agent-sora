#!/usr/bin/env python
"""Extract arXiv PDF text for the 2026-09-03 Papercast batch.

Writes episodes/feed/text/<id>.txt (pages 0-7), <id>-more.txt (pages 8-15),
and <id>-experiments.txt (pages 19-28, only when the paper has more than
18 pages) for each arxiv id in episodes/feed/picks/ids-2026-09-03.txt,
using pymupdf (NOT the fitz module).
"""
import os
import sys
import pymupdf

PC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = sys.argv[1] if len(sys.argv) > 1 else '2026-09-03'
IDS_FILE = os.path.join(PC, f"episodes/feed/picks/ids-{D}.txt")
OUTDIR = os.path.join(PC, "episodes/feed/text")
os.makedirs(OUTDIR, exist_ok=True)

with open(IDS_FILE) as f:
    ids = [l.strip() for l in f if l.strip()]

for i in ids:
    cands = [
        os.path.join(PC, f"episodes/feed/meta/{i}.pdf"),
        os.path.join(PC, f"episodes/feed/meta/{i.replace('.', '-')}.pdf"),
    ]
    path = next((c for c in cands if os.path.exists(c)), cands[0])
    doc = pymupdf.open(path)
    pages = doc.page_count
    first = "".join(doc[p].get_text() for p in range(0, min(8, pages)))
    more = "".join(doc[p].get_text() for p in range(8, min(16, pages)))
    with open(f"{OUTDIR}/{i}.txt", "w") as fh:
        fh.write(first)
    with open(f"{OUTDIR}/{i}-more.txt", "w") as fh:
        fh.write(more)
    line = f"{i} pages:{pages} first:{len(first)} more:{len(more)}"
    if pages > 18:
        exp = "".join(doc[p].get_text() for p in range(19, min(29, pages)))
        with open(f"{OUTDIR}/{i}-experiments.txt", "w") as fh:
            fh.write(exp)
        line += f" experiments:{len(exp)}"
    print(line)
