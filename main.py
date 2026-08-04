#!/usr/bin/env python3
"""
Eureka-Static-Intelligence — FinChip Skill
==========================================
Compiles a standardized enterprise FAQ list (+ industry vocabulary, + optional
task flow) into a self-contained static-intelligence chatbox: one HTML file,
no LLM, no backend, no build step — yet conversationally robust, thanks to the
five-layer lexical engine distilled from FinChip Generator v3.0.

Invocation (FinChip call-skill contract):
    python main.py <input.json>                 # -> out/<slug>-chatbox.html
    python main.py <input.json> --out ./dist
    python main.py examples/input_dental.json

The compiler auto-derives what humans usually hand-craft:
  * keywords   — distinctive tokens per question (tf-idf over the corpus)
  * children   — top-2 most-similar nodes (char n-gram cosine) → topic threads
  * quick 10   — explicit "mainline": true flags, else centrality ranking
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

TEMPLATE = Path(__file__).parent / "template" / "chatbox.template.html"
UI = Path(__file__).parent / "template" / "ui.js"

STOP = set("the a an is are was be been do does did can could will would should what when where which who why how i my me we our you your it its this that to of for in on at by and or but if with about into from have has let tell know show give explain please want need just some any more like help get".split())


def slugify(name: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9一-鿿]+", "-", name.lower())).strip("-") or "chatbox"


def stem(t: str) -> str:
    return re.sub(r"e$", "", re.sub(r"(ing|ed|es|s)$", "", t))


def tokens(text: str) -> list[str]:
    out = []
    for m in re.findall(r"[a-z0-9]{3,}", text.lower()):
        if m not in STOP:
            out.append(stem(m))
    for run in re.findall(r"[一-鿿]+", text):
        out += [run[i:i + 2] for i in range(len(run) - 1)]
    return out


def grams(text: str) -> list[str]:
    gs = []
    for w in re.sub(r"[^a-z0-9一-鿿]+", " ", text.lower()).split():
        if re.search(r"[一-鿿]", w):
            gs += [w[i:i + 2] for i in range(len(w) - 1)]
        elif len(w) >= 3:
            p = f"#{w}#"
            gs += [p[i:i + 3] for i in range(len(p) - 2)]
    return gs


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = Path(sys.argv[1])
    out_dir = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path("out")
    data = json.loads(src.read_text(encoding="utf-8"))

    faq = data["faq"]
    n = len(faq)
    assert n >= 10, "Need at least 10 FAQ entries"

    # ids
    seen = set()
    for i, node in enumerate(faq):
        nid = node.get("id") or slugify(node["q"]["en"])[:40] or f"q{i}"
        while nid in seen:
            nid += "x"
        node["id"] = nid
        seen.add(nid)

    # per-node text + token df for auto-keywords
    texts = [node["q"]["en"] + " " + node["q"].get("zh", "") for node in faq]
    df: Counter[str] = Counter()
    node_toks = []
    for t in texts:
        tk = set(tokens(t))
        node_toks.append(tk)
        df.update(tk)

    # auto keywords: up to 6 most distinctive question tokens
    for node, tk in zip(faq, node_toks):
        if not node.get("keywords"):
            ranked = sorted(tk, key=lambda x: (df[x], -len(x)))
            kws = [k for k in ranked if df[k] <= max(2, n // 8)][:6]
            # prefix variants so "cancel" hits keyword "cancellation" etc.
            kws += [k[:6] for k in kws if len(k) > 7 and not re.search(r"[一-鿿]", k)]
            node["keywords"] = list(dict.fromkeys(kws))[:9]

    # n-gram tf-idf vectors for similarity graph
    gdf: Counter[str] = Counter()
    vecs = []
    for node, t in zip(faq, texts):
        tf = Counter(grams(t + " " + node["a"]["en"][:200]))
        vecs.append(tf)
        gdf.update(tf.keys())
    wvecs, norms = [], []
    for tf in vecs:
        wv = {g: (1 + math.log(f)) * math.log(1 + n / gdf[g]) for g, f in tf.items()}
        wvecs.append(wv)
        norms.append(math.sqrt(sum(w * w for w in wv.values())) or 1.0)

    def cos(i: int, j: int) -> float:
        a, b = wvecs[i], wvecs[j]
        if len(b) < len(a):
            a, b = b, a
        return sum(w * b.get(g, 0.0) for g, w in a.items()) / (norms[i] * norms[j])

    sim = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            sim[i][j] = sim[j][i] = cos(i, j)

    # auto children: top-2 similar (threads); auto quick-10: flags else centrality
    for i, node in enumerate(faq):
        if not node.get("children"):
            order = sorted(range(n), key=lambda j: -sim[i][j])
            node["children"] = [faq[j]["id"] for j in order if j != i][:2]
    flagged = [x["id"] for x in faq if x.get("mainline")]
    if len(flagged) >= 4:
        quick = flagged[:10]
    else:
        central = sorted(range(n), key=lambda i: -sum(sim[i]))
        quick = flagged + [faq[i]["id"] for i in central if faq[i]["id"] not in flagged]
        quick = quick[:10]

    # vocab: stem the synonym map for the engine
    syn = {stem(k.lower()): [stem(v.lower()) for v in vs] for k, vs in (data.get("vocab", {}).get("synonyms") or {}).items()}

    pack = {
        "brand": data["brand"],
        "faq": [{k: v for k, v in node.items() if k in ("id", "q", "a", "keywords", "children", "link", "more")} for node in faq],
        "quick": quick,
        "vocab": {
            "synonymsStemmed": syn,
            "zhTerms": data.get("vocab", {}).get("zhTerms") or [],
            "smalltalkExtra": data.get("vocab", {}).get("smalltalkExtra") or [],
        },
        "flow": data.get("flow"),
        "toolbox": data.get("toolbox") or ["calculator", "json", "timestamp", "units", "textstats", "aeo"],
    }

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("%%BRAND_NAME%%", data["brand"]["name"])
    html = html.replace("%%ACCENT%%", data["brand"].get("accent", "#0D9AFF"))
    html = html.replace("%%PACK_JSON%%", json.dumps(pack, ensure_ascii=False).replace("</", "<\\/"))
    html = html.replace("%%UI_SCRIPT%%", UI.read_text(encoding="utf-8"))

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slugify(data['brand']['name'])}-chatbox.html"
    out_path.write_text(html, encoding="utf-8")

    print(json.dumps({
        "skill": "Eureka-Static-Intelligence", "status": "ok",
        "result": {"chatbox": str(out_path), "nodes": n, "quick": quick,
                   "auto_keywords": sum(1 for x in faq if x.get("keywords")),
                   "size_kb": round(out_path.stat().st_size / 1024, 1)},
        "warnings": [],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
