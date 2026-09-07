#!/usr/bin/env python
"""Dump pages 16-19 of the SolarWM paper (2609.02886) — the evaluation
section that fell between the page 8-15 and 19-28 windows — to
episodes/feed/text/2609.02886-exp2.txt using pymupdf."""
import os
import pymupdf

PC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(PC, 'episodes/feed/meta/2609.02886.pdf'))
t = "".join(doc[p].get_text() for p in range(16, min(19, doc.page_count)))
out = os.path.join(PC, 'episodes/feed/text/2609.02886-exp2.txt')
with open(out, 'w') as fh:
    fh.write(t)
print(out, len(t))
