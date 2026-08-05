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



# ═══ Loose-text ingestion: txt / md / docx → standard input JSON ═════════════
# Merchants hand over whatever they have; the skill does the structuring.
# Deterministic parsing, four strategies raced by yield:
#   A. explicit markers   Q:/问： … A:/答：
#   B. markdown headers   ## question \n answer…
#   C. numbered items     1. question \n answer…
#   D. question-mark blocks   any ?-ending line, following lines = answer
# Optional header directives (before the first question):
#   Brand/品牌: … · Tagline/副标题: … · Accent/主色: #hex · Welcome/欢迎: …
#   Anchor/按钮: label | https://url · Tag/标签: … · Langs/语言: zh,en
# Optional vocab section:  [vocab] / 词汇表:  then lines  term = english words
# Mark a question mainline with a leading * or ★.

CJK_RE = re.compile(r"[一-鿿]")


def _docx_text(path: Path) -> str:
    import zipfile
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    xml = re.sub(r"</w:p>", "\n", xml)
    return re.sub(r"<[^>]+>", "", xml)


def _lang_of(text: str) -> str:
    cjk = len(CJK_RE.findall(text))
    return "zh" if cjk > max(2, len(text) * 0.2) else "en"


def _bi(text: str) -> dict:
    lang = _lang_of(text)
    other = "en" if lang == "zh" else "zh"
    return {lang: text.strip(), other: text.strip()}  # mirror so the index always has .en


HEAD_KEYS = {
    "brand": "name", "品牌": "name", "名称": "name", "name": "name",
    "tagline": "tagline", "副标题": "tagline",
    "accent": "accent", "主色": "accent", "颜色": "accent",
    "welcome": "welcome", "欢迎": "welcome", "欢迎语": "welcome",
    "anchor": "anchor", "按钮": "anchor", "锚点": "anchor",
    "tag": "tag", "标签": "tag",
    "langs": "langs", "语言": "langs",
}


DEFAULT_ACCENT = "#0D9AFF"
COLOR_NAMES = {
    # 中文常用色名 + 英文 CSS 色名（常见子集），商户随手写也能出正确品牌色
    "红": "#D93025", "红色": "#D93025", "大红": "#D93025", "orange红": "#D93025",
    "橙": "#E8710A", "橙色": "#E8710A", "橘色": "#E8710A", "橙红": "#E85D2F",
    "黄": "#F0A800", "黄色": "#F0A800", "金色": "#C9A227", "金": "#C9A227",
    "绿": "#188038", "绿色": "#188038", "墨绿": "#0B5C43", "青色": "#00897B",
    "蓝": "#1A73E8", "蓝色": "#1A73E8", "深蓝": "#174EA6", "天蓝": "#0D9AFF",
    "紫": "#7B1FA2", "紫色": "#7B1FA2", "粉": "#D81B60", "粉色": "#D81B60", "粉红": "#D81B60",
    "棕": "#795548", "棕色": "#795548", "咖啡色": "#6D4C41", "黑": "#202124", "黑色": "#202124",
    "red": "#D93025", "orange": "#E8710A", "yellow": "#F0A800", "gold": "#C9A227",
    "green": "#188038", "teal": "#00897B", "blue": "#1A73E8", "navy": "#174EA6",
    "purple": "#7B1FA2", "pink": "#D81B60", "brown": "#795548", "black": "#202124",
    "crimson": "#DC143C", "coral": "#FF7F50", "tomato": "#FF6347", "salmon": "#FA8072",
}

def norm_accent(raw, warnings):
    """Normalize a merchant-supplied accent into a valid #RRGGBB, or fall back.
    Accepts: #RRGGBB, #RGB, hex without '#', zh/en color names, rgb(r,g,b)."""
    if not raw:
        return DEFAULT_ACCENT
    v = str(raw).strip().strip('"').strip("'")
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", v)
    if m:
        return "#" + m.group(1).upper()
    m = re.fullmatch(r"#?([0-9a-fA-F]{3})", v)
    if m:
        return "#" + "".join(c * 2 for c in m.group(1)).upper()
    m = re.fullmatch(r"rgb\s*\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", v, re.I)
    if m:
        r, g, b = (min(int(x), 255) for x in m.groups())
        return f"#{r:02X}{g:02X}{b:02X}"
    named = COLOR_NAMES.get(v.lower()) or COLOR_NAMES.get(v)
    if named:
        return named
    warnings.append(f"accent '{raw}' not recognized — using default {DEFAULT_ACCENT}")
    return DEFAULT_ACCENT


def parse_loose(text: str, fallback_name: str) -> dict:
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    brand: dict = {}
    vocab_zh: list = []
    vocab_syn: dict = {}
    warnings: list = []

    # ── header directives ──
    body_start = 0
    for i, ln in enumerate(lines):
        m = re.match(r"^\s*([A-Za-z\u4e00-\u9fff]{2,8})\s*[:：]\s*(.+)$", ln)
        if m and HEAD_KEYS.get(m.group(1).strip().lower()) and not re.match(r"^\s*(q|问|a|答)\d*\s*[:：.]", ln, re.I):
            key = HEAD_KEYS[m.group(1).strip().lower()]
            val = m.group(2).strip()
            if key == "anchor":
                parts = [x.strip() for x in re.split(r"[|｜]", val, 1)]
                brand["anchor"] = {"label": _bi(parts[0]), "action": "link" if len(parts) > 1 else "faq",
                                   "target": parts[1] if len(parts) > 1 else ""}
            elif key == "langs":
                brand["langs"] = [x.strip() for x in re.split(r"[,，\s]+", val) if x.strip() in ("zh", "en")]
            elif key in ("tagline", "welcome"):
                brand[key] = _bi(val)
            else:
                brand[key] = val
            body_start = i + 1
        elif ln.strip():
            break

    # ── vocab section (anywhere) ──
    body_lines = []
    in_vocab = False
    for ln in lines[body_start:]:
        if re.match(r"^\s*(\[vocab\]|词汇表|vocabulary)\s*[:：]?\s*$", ln, re.I):
            in_vocab = True
            continue
        if in_vocab:
            m = re.match(r"^\s*(.+?)\s*[=＝]\s*(.+)$", ln)
            if m:
                a, b = m.group(1).strip(), m.group(2).strip()
                if CJK_RE.search(a):
                    vocab_zh.append([re.escape(a) if "|" not in a else a, b])
                else:
                    vocab_syn[a.lower()] = [x.strip() for x in re.split(r"[,，\s]+", b) if x.strip()]
                continue
            if ln.strip():
                in_vocab = False
        if not in_vocab:
            body_lines.append(ln)
    body = "\n".join(body_lines)

    # ── strategy A: explicit Q/A markers ──
    def strat_markers():
        # True-bilingual aware: 问：=zh / Q:=en, 答：=zh / A:=en. A second-language
        # question marker arriving BEFORE any answer joins the same entry, so
        # merchants can write paired 问/Q + 答/A blocks for real bilingual packs.
        entries, cur = [], None

        def close():
            nonlocal cur
            if cur and (cur["q"]["zh"] or cur["q"]["en"]) and (cur["a"]["zh"] or cur["a"]["en"]):
                cur.pop("mode", None)
                entries.append(cur)
            cur = None

        for ln in body.split("\n"):
            mq = re.match(r"^\s*([*★]?)\s*(q\d*|问\d*)\s*[:：.、)]\s*(.*)$", ln, re.I)
            ma = re.match(r"^\s*(a\d*|答\d*)\s*[:：.、)]\s*(.*)$", ln, re.I)
            if mq:
                lang = "en" if mq.group(2)[0].lower() == "q" else "zh"
                if cur and (cur["a"]["zh"] or cur["a"]["en"]):
                    close()
                if cur is None:
                    cur = {"q": {"zh": "", "en": ""}, "a": {"zh": "", "en": ""}, "star": False, "mode": None}
                cur["star"] = cur["star"] or bool(mq.group(1))
                cur["q"][lang] = (cur["q"][lang] + " " + mq.group(3).strip()).strip()
                cur["mode"] = ("q", lang)
            elif ma and cur is not None:
                lang = "en" if ma.group(1)[0].lower() == "a" else "zh"
                cur["a"][lang] = (cur["a"][lang] + " " + ma.group(2).strip()).strip()
                cur["mode"] = ("a", lang)
            elif cur is not None and cur.get("mode") and ln.strip():
                k, lang = cur["mode"]
                cur[k][lang] = (cur[k][lang] + "\n" + ln.strip()).strip()
        close()
        return entries

    # ── strategy A2: verbose labeled bilingual exports ──
    # "Question (ZH) / 问题（中文）: …" / "Answer (EN) …: …" + Tags/标签 + [FAQ-201] Section
    def strat_labeled():
        QRE = re.compile(r"^\s*([*★]?)\s*(?:question|问题)\s*[（(]\s*(zh|en|中文|英文|english|chinese)\s*[）)][^:：]*[:：]\s*(.*)$", re.I)
        ARE = re.compile(r"^\s*(?:answer|回答|答案)\s*[（(]\s*(zh|en|中文|英文|english|chinese)\s*[）)][^:：]*[:：]\s*(.*)$", re.I)
        TRE = re.compile(r"^\s*(?:tags?|标签)\s*[/／]?[^:：]*[:：]\s*(.*)$", re.I)
        SRE = re.compile(r"^\s*(?:\[[^\]]+\]\s*)?(?:section|分类)\s*[/／]?[^:：]*[:：]", re.I)
        IDRE = re.compile(r"\[((?:faq|FAQ)[-_]?\w+)\]")

        def L(x):
            return "zh" if x.lower() in ("zh", "中文", "chinese") else "en"

        entries, cur = [], None

        def close():
            nonlocal cur
            if cur and (cur["q"]["zh"] or cur["q"]["en"]) and (cur["a"]["zh"] or cur["a"]["en"]):
                cur.pop("mode", None)
                entries.append(cur)
            cur = None

        for ln in body.split("\n"):
            mq, ma, mt = QRE.match(ln), ARE.match(ln), TRE.match(ln)
            if mq:
                lang = L(mq.group(2))
                if cur and (cur["a"]["zh"] or cur["a"]["en"]):
                    close()
                if cur is None:
                    cur = {"q": {"zh": "", "en": ""}, "a": {"zh": "", "en": ""}, "star": False, "kw": [], "nid": None, "mode": None}
                cur["star"] = cur["star"] or bool(mq.group(1))
                cur["q"][lang] = (cur["q"][lang] + " " + mq.group(3).strip()).strip()
                cur["mode"] = ("q", lang)
            elif ma and cur is not None:
                lang = L(ma.group(1))
                cur["a"][lang] = (cur["a"][lang] + " " + ma.group(2).strip()).strip()
                cur["mode"] = ("a", lang)
            elif mt and cur is not None:
                cur["kw"] = [t.strip() for t in re.split(r"[,，;；]", mt.group(1)) if t.strip()][:10]
                cur["mode"] = None
            elif SRE.match(ln) and cur is not None:
                m = IDRE.search(ln)
                if m:
                    cur["nid"] = m.group(1).lower().replace("_", "-")
                cur["mode"] = None
            elif cur is not None and cur.get("mode") and ln.strip():
                k, lang = cur["mode"]
                cur[k][lang] = (cur[k][lang] + "\n" + ln.strip()).strip()
        close()
        return entries

    # ── strategy B: markdown headers ──
    def strat_md():
        pairs, q, a = [], None, []
        for ln in body.split("\n"):
            m = re.match(r"^#{1,3}\s+(.+)$", ln)
            if m:
                if q and a:
                    pairs.append((q, "\n".join(a)))
                q, a = m.group(1).strip(), []
            elif q is not None and ln.strip():
                a.append(ln.strip())
        if q and a:
            pairs.append((q, "\n".join(a)))
        return pairs

    # ── strategy C: numbered items ──
    def strat_num():
        pairs, q, a = [], None, []
        for ln in body.split("\n"):
            m = re.match(r"^\s*[*★]?\s*\d+\s*[.、)]\s*(.+)$", ln)
            if m:
                if q and a:
                    pairs.append((q, "\n".join(a)))
                star = "*" if re.match(r"^\s*[*★]", ln) else ""
                q, a = star + m.group(1).strip(), []
            elif q is not None and ln.strip():
                a.append(ln.strip())
        if q and a:
            pairs.append((q, "\n".join(a)))
        return pairs

    # ── strategy D: question-mark blocks ──
    def strat_qmark():
        pairs, q, a = [], None, []
        for ln in body.split("\n"):
            if re.search(r"[?？]\s*$", ln.strip()) and len(ln.strip()) < 80:
                if q and a:
                    pairs.append((q, "\n".join(a)))
                q, a = ln.strip(), []
            elif q is not None and ln.strip():
                a.append(ln.strip())
        if q and a:
            pairs.append((q, "\n".join(a)))
        return pairs

    candidates = {"labeled": strat_labeled(), "markers": strat_markers(), "markdown": strat_md(),
                  "numbered": strat_num(), "qmark": strat_qmark()}
    # explicitness hierarchy: an explicit format that yields enough pairs beats
    # a sloppier one with a higher raw count (qmark double-counts bilingual files)
    strategy = next((k for k in ("labeled", "markers", "markdown", "numbered", "qmark") if len(candidates[k]) >= 5), None)
    if strategy is None:
        strategy, _ = max(candidates.items(), key=lambda kv: len(kv[1]))
    pairs = candidates[strategy]
    if len(pairs) < 5:
        raise SystemExit(f"Could not detect enough Q&A pairs (best strategy '{strategy}' found {len(pairs)}). "
                         "Format tips: 'Q:/A:' or '问：/答：' markers, '## question' headers, numbered items, "
                         "or question lines ending with ?/？")

    faq = []
    langs_seen = []
    for item in pairs:
        if isinstance(item, dict):  # bilingual-aware markers strategy
            qd, ad = item["q"], item["a"]
            entry = {"q": {"zh": qd["zh"] or qd["en"], "en": qd["en"] or qd["zh"]},
                     "a": {"zh": ad["zh"] or ad["en"], "en": ad["en"] or ad["zh"]}}
            if item.get("star"):
                entry["mainline"] = True
            if item.get("kw"):
                entry["keywords"] = item["kw"]
            if item.get("nid"):
                entry["id"] = item["nid"]
            for l in ("zh", "en"):
                if qd[l] and l not in langs_seen:
                    langs_seen.append(l)
        else:
            qtext, atext = item
            mainline = qtext.startswith("*") or qtext.startswith("★")
            qtext = qtext.lstrip("*★ ").strip()
            entry = {"q": _bi(qtext), "a": _bi(atext)}
            if mainline:
                entry["mainline"] = True
            lang = _lang_of(qtext)
            if lang not in langs_seen:
                langs_seen.append(lang)
        faq.append(entry)

    name = brand.get("name")
    if not name:
        segs = [x for x in re.split(r"[_\-\s]+", fallback_name) if x]
        name = segs[0] if segs else "Chatbox"
        warnings.append(f"brand name derived from filename → '{name}' — add a 品牌:/Brand: header line for full control")
    langs = brand.get("langs") or langs_seen or ["en"]
    default_welcome = {"zh": f"你好！我是{name}智能助手——常见问题都可以问我。需要什么帮助？",
                       "en": f"Hi! I am the {name} assistant — ask me anything. How can I help?"}
    anchor = brand.get("anchor")
    if not anchor or not anchor.get("target"):
        anchor = {"label": {"zh": "热门问题 ↗", "en": "Top question ↗"}, "action": "faq", "target": ""}
    result = {
        "brand": {
            "name": name,
            **({"tagline": brand["tagline"]} if brand.get("tagline") else {}),
            "accent": norm_accent(brand.get("accent"), warnings),
            **({"tag": brand["tag"]} if brand.get("tag") else {}),
            "langs": langs,
            "welcome": brand.get("welcome", default_welcome),
            "anchor": anchor,
        },
        "faq": faq,
        "vocab": {"synonyms": vocab_syn, "zhTerms": vocab_zh, "smalltalkExtra": []},
        "flow": None,
        "toolbox": ["calculator", "json", "timestamp", "units", "textstats", "aeo"],
    }
    return result, strategy, warnings


def ingest(src: Path) -> Path:
    """txt/md/docx → <stem>.generated.json alongside the source; returns json path."""
    ext = src.suffix.lower()
    if ext == ".json":
        return src
    if ext == ".docx":
        text = _docx_text(src)
    elif ext in (".txt", ".md", ".markdown"):
        text = src.read_text(encoding="utf-8", errors="replace")
    elif ext == ".doc":
        raise SystemExit("Legacy .doc is a binary format — please Save As .docx or .txt and rerun.")
    else:
        raise SystemExit(f"Unsupported input type: {ext} (accepted: .json .txt .md .docx)")
    data, strategy, warns = parse_loose(text, src.stem)
    out = src.with_suffix(".generated.json")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ingest] strategy={strategy} · {len(data['faq'])} Q&A pairs · brand='{data['brand']['name']}' → {out}")
    for w in warns:
        print(f"[ingest][warn] {w}")
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = ingest(Path(sys.argv[1]))
    out_dir = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path("out")
    data = json.loads(src.read_text(encoding="utf-8"))

    faq = data["faq"]
    n = len(faq)
    assert n >= 5, "Need at least 5 FAQ entries"
    size_warns = ([f"only {n} FAQ entries — the experience gets solid at 30+, rich at 100"] if n < 10 else [])

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

    # interest clusters (generalized persona layer): greedy similarity grouping.
    # The engine votes over the visitor's recent trail and biases the branch
    # chip toward the dominant cluster — deterministic, frozen at compile time.
    CLUSTER_T = 0.18
    cluster_of = [-1] * n
    next_c = 0
    for i in range(n):
        best_j, best_s = -1, CLUSTER_T
        for j in range(i):
            if sim[i][j] > best_s:
                best_j, best_s = j, sim[i][j]
        if best_j >= 0:
            cluster_of[i] = cluster_of[best_j]
        else:
            cluster_of[i] = next_c
            next_c += 1
    for i, node in enumerate(faq):
        node["cluster"] = cluster_of[i]
    flagged = [x["id"] for x in faq if x.get("mainline")]
    if len(flagged) >= 4:
        quick = flagged[:10]
    else:
        central = sorted(range(n), key=lambda i: -sum(sim[i]))
        quick = flagged + [faq[i]["id"] for i in central if faq[i]["id"] not in flagged]
        quick = quick[:10]
    # default/faq anchors with no target would dead-click — aim at the top quick question
    anc = data['brand'].get('anchor')
    if anc and anc.get('action') == 'faq' and not anc.get('target'):
        anc['target'] = quick[0] if quick else faq[0]['id']

    # vocab: stem the synonym map for the engine
    syn = {stem(k.lower()): [stem(v.lower()) for v in vs] for k, vs in (data.get("vocab", {}).get("synonyms") or {}).items()}

    # zhTerms reverse-enrichment: every FAQ entry matching a vocab pattern
    # gains the pattern's zh alternatives AND its en words as keywords —
    # this is how "好吃/退订/小孩" style colloquial variants find their node
    # even in a pure-Chinese pack. Merchants write alternatives with |.
    # Conservative enrichment: alts need >=2 chars (single CJK chars are far
    # too broad as keywords); English words are injected only for pure-zh
    # packs (where q.en mirrors q.zh) — bilingual packs already carry real
    # English in the index and extra en keywords just distort the balance.
    mirrored = sum(1 for x in faq if x["q"].get("en") == x["q"].get("zh"))
    pure_zh_pack = mirrored > len(faq) * 0.7
    for term_pat, en_words in (data.get("vocab", {}).get("zhTerms") or []):
        try:
            pat = re.compile(term_pat)
        except re.error:
            continue
        alts = [a for a in re.sub(r"[\\^$()\[\]?*+]", "", term_pat).split("|") if len(a) >= 2]
        q_hits = [node for node in faq if pat.search(node["q"].get("zh", "") + node["q"].get("en", ""))]
        a_hits = [node for node in faq if pat.search(node["a"].get("zh", ""))]
        # question matches outrank answer matches — a term casually mentioned
        # in another node's answer must not steal the keyword
        hits = q_hits if q_hits else a_hits
        if not hits or len(hits) > max(3, n // 3):
            continue  # matches nothing or is ubiquitous — no discriminative value
        for node in hits:
            extra = list(alts)
            if pure_zh_pack:
                extra += [w for w in en_words.split() if len(w) > 2]
            node["keywords"] = list(dict.fromkeys((node.get("keywords") or []) + extra))[:14]

    if data["brand"].get("anchor", {}).get("action") == "faq" and not data["brand"]["anchor"].get("target"):
        data["brand"]["anchor"]["target"] = quick[0]
    pack = {
        "brand": data["brand"],
        "faq": [{k: v for k, v in node.items() if k in ("id", "q", "a", "keywords", "children", "link", "more", "cluster")} for node in faq],
        "quick": quick,
        "vocab": {
            "synonymsStemmed": syn,
            "zhTerms": data.get("vocab", {}).get("zhTerms") or [],
            "smalltalkExtra": data.get("vocab", {}).get("smalltalkExtra") or [],
        },
        "flow": data.get("flow"),
        "toolbox": data.get("toolbox") or ["calculator", "json", "timestamp", "units", "textstats", "aeo"],
    }

    compile_warns: list = list(size_warns)
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("%%BRAND_NAME%%", data["brand"]["name"])
    html = html.replace("%%ACCENT%%", norm_accent(data["brand"].get("accent"), compile_warns))
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
        "warnings": compile_warns,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
