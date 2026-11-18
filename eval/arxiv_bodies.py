#!/usr/bin/env python3
"""ticfinder construction rates in arXiv cs.AR paper bodies (TF-005 pilot).

  fetch        walk a seeded shuffle of each window's TF-004 primary ids,
               download the v1 LaTeX source from export.arxiv.org/e-print,
               and keep the first 200 papers per window with usable
               source. Archives are cached under private/arxiv/source/,
               the expanded main file under private/arxiv/expanded/, and
               the sample and per-paper records under private/arxiv/bodies/.
               A rerun fetches only what is missing.
  selftest     expected-output rows for the LaTeX masker and the section
               classifier, written from synthetic LaTeX only.
  mask-report  masked shares, skip counts, dash counts, and random masked
               sentences per window printed to the console for a residue
               spot-check. Prints text; writes nothing.
  analyse      phase 2: ticfinder over the masked bodies and the same
               papers' abstracts, per-section rates, and the report.

Windows, primary category and dating are TF-004's (eval/arxiv_rates.py).
The sample is drawn from the TF-004 month manifests; no new metadata is
fetched. Source is requested as <id>v1, so the body is the version the v1
date refers to. A later revision of a pre-window paper could hold post-2022
text; v1 cannot.

Nothing this script writes outside private/ holds paper text, titles or
ids.
"""

import argparse
import gzip
import io
import json
import random
import re
import sys
import tarfile
import time
import urllib.error
import urllib.request
import zlib
from collections import Counter
from pathlib import PurePosixPath

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import arxiv_rates as AR  # noqa: E402

CACHE = AR.CACHE
SRC = CACHE / "source"
EXP = CACHE / "expanded"
BODY = CACHE / "bodies"
SAMPLE_FILE = BODY / "sample.json"
RECORDS = BODY / "papers.jsonl"

EPRINT = "https://export.arxiv.org/e-print/"
WANT = 200              # usable papers per window
BODY_SEED = 20261118    # shuffle seed, used as f"{BODY_SEED}-bodies-{window}"
MIN_WORDS = 300         # under this after masking: "too little text"
MAX_MEMBER = 20 << 20   # skip archive members larger than this


# ---------------------------------------------------------------- fetch

class FetchError(SystemExit):
    pass


def eprint_get(pid):
    """Return the v1 source bytes, or None when arXiv has no source (404).

    Any other HTTP error or a network failure stops the run.
    """
    wait = AR.DELAY - (time.monotonic() - AR._last_request[0])
    if wait > 0:
        time.sleep(wait)
    url = EPRINT + pid + "v1"
    req = urllib.request.Request(url, headers={"User-Agent": AR.USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return None
        raise FetchError(f"e-print returned HTTP {e.code} (Retry-After: "
                         f"{e.headers.get('Retry-After')}); stopping "
                         "(rate limit or outage). Cached archives are kept; "
                         "rerun later.")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise FetchError(f"e-print unreachable ({e}); stopping. Cached "
                         "archives are kept; rerun later.")
    finally:
        AR._last_request[0] = time.monotonic()


def cached_source(pid, fetched):
    """(bytes or None, fetched_now). Caches 404s as a .none marker."""
    base = SRC / (pid.replace("/", "_") + "v1")
    none = base.with_name(base.name + ".none")
    if base.exists():
        return base.read_bytes(), False
    if none.exists():
        return None, False
    data = eprint_get(pid)
    fetched.append(pid)
    if data is None:
        none.write_text("404\n")
    else:
        tmp = base.with_name(base.name + ".part")
        tmp.write_bytes(data)
        tmp.replace(base)
    return data, True


def _decode(b):
    try:
        return b.decode("utf-8"), False
    except UnicodeDecodeError:
        return b.decode("latin-1"), True


TEXT_SUFFIX = {".tex", ".ltx", ".latex", ".bbl", ".txt", ""}


def unpack(data):
    """Return (files, None) with files {posix name: bytes}, or (None, reason).

    Reasons: "no source", "PDF only", "unpack error", "other format".
    Tar members are read in memory; nothing is extracted to disk.
    """
    if not data:
        return None, "no source"
    if data[:4] == b"%PDF":
        return None, "PDF only"
    if data[:2] == b"\x1f\x8b":
        try:
            data = gzip.decompress(data)
        except (OSError, EOFError, zlib.error):
            return None, "unpack error"
        if data[:4] == b"%PDF":
            return None, "PDF only"
    if len(data) > 262 and data[257:262] == b"ustar" or data[:5] == b"PK\x03\x04":
        if data[:5] == b"PK\x03\x04":
            return None, "other format"
        try:
            files = {}
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as tar:
                for m in tar.getmembers():
                    if not m.isfile() or m.size > MAX_MEMBER:
                        continue
                    name = str(PurePosixPath(m.name.lstrip("./")))
                    if PurePosixPath(name).suffix.lower() not in TEXT_SUFFIX:
                        continue
                    f = tar.extractfile(m)
                    if f is not None:
                        files[name] = f.read()
            return files, None
        except (tarfile.TarError, OSError, EOFError, zlib.error):
            return None, "unpack error"
    head = data[:4096]
    if head.startswith(b"%!PS"):
        return None, "other format"
    if b"<html" in head.lower() or b"<!doctype html" in head.lower():
        return None, "no source"
    return {"main.tex": data}, None


def strip_comments(text):
    """Text with TeX comments removed (for searching, not for masking)."""
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


_INPUT = re.compile(
    r"\\(input|include|subfile)(?![A-Za-z])\s*(?:\{([^{}]+)\}|([^\s{}\\%]+))"
    r"|\\(import|subimport|inputfrom|subinputfrom)\*?\s*\{([^{}]*)\}\s*"
    r"\{([^{}]+)\}")


def _in_comment(text, pos):
    ls = text.rfind("\n", 0, pos) + 1
    return re.search(r"(?<!\\)%", text[ls:pos]) is not None


def expand(name, files, texts, stats, depth=0, seen=()):
    """Expand \\input and \\include recursively. Unresolved ones stay."""
    text = texts[name]
    base = PurePosixPath(name).parent
    out, last = [], 0
    for m in _INPUT.finditer(text):
        if _in_comment(text, m.start()):
            continue
        if m.group(1):
            arg = (m.group(2) or m.group(3)).strip()
            cand = [base / arg, PurePosixPath(arg)]
        else:
            d, f = m.group(5).strip(), m.group(6).strip()
            cand = [base / d / f, PurePosixPath(d) / f]
        hit = None
        for c in cand:
            for s in ("", ".tex"):
                k = str(PurePosixPath(str(c) + s))
                k = re.sub(r"^(\./)+", "", k)
                if k in texts and k not in seen and k != name:
                    hit = k
                    break
            if hit:
                break
        if hit is None or depth >= 12:
            stats["unresolved"] += 1
            continue
        out.append(text[last:m.start()])
        out.append(expand(hit, files, texts, stats, depth + 1,
                          seen + (name,)))
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def find_main(files):
    """Return (main name, expanded text, info) or (None, None, info)."""
    texts, latin1 = {}, 0
    for k, b in files.items():
        if PurePosixPath(k).suffix.lower() in (".tex", ".ltx", ".latex", ""):
            texts[k], l1 = _decode(b)
            latin1 += l1
    cands = []
    for k, t in texts.items():
        s = strip_comments(t)
        if (re.search(r"\\document(class|style)\b", s)
                and re.search(r"\\begin\s*\{document\}", s)):
            cands.append(k)
    info = {"candidates": len(cands), "latin1_files": latin1,
            "tie_rule": None, "unresolved": 0}
    if not cands:
        return None, None, info
    expanded = {}
    for k in cands:
        st = Counter()
        expanded[k] = (expand(k, files, texts, st), st["unresolved"])
    # Tie rule: the candidate with the longest expanded text, then the
    # first name in sort order. A main file that \input's another
    # candidate is longer than it, so it wins.
    best = sorted(cands, key=lambda k: (-len(expanded[k][0]), k))[0]
    if len(cands) > 1:
        info["tie_rule"] = "longest expanded text"
    info["unresolved"] = expanded[best][1]
    return best, expanded[best][0], info


# ------------------------------------------------------------ masking

# Each rule blanks in place (non-space characters become spaces), so
# offsets in the masked text are offsets in the expanded source. The one
# substitution is TeX "---", which becomes U+2014 and two spaces.

ESCAPES = set("%&_#${}")
VERB_ENVS = ["verbatim", "Verbatim", "lstlisting", "minted", "comment",
             "alltt", "filecontents", "BVerbatim", "spverbatim"]
FLOAT_ENVS = ["figure", "table", "algorithm", "algorithmic", "algorithm2e",
              "tikzpicture", "tabular", "tabularx", "tabulary", "longtable",
              "wrapfigure", "wraptable", "subfigure", "subtable",
              "sidewaysfigure", "sidewaystable", "pgfpicture", "picture",
              "circuitikz", "forest", "axis", "IEEEkeywords", "keywords",
              "CCSXML", "thebibliography", "lstlisting", "tcolorbox",
              "algorithmic", "algorithmicx", "listing", "figwindow"]
MATH_ENVS = ["equation", "align", "gather", "multline", "eqnarray",
             "flalign", "alignat", "displaymath", "math", "split", "dmath",
             "dgroup", "IEEEeqnarray", "subequations", "cases", "array",
             "matrix", "pmatrix", "bmatrix"]
ACK_ENVS = ["acks", "acknowledgments", "acknowledgements",
            "acknowledgment", "acknowledgement"]
# commands whose arguments are blanked with them: name -> brace args
DROP = {
    "label": 1, "url": 1, "href": 1, "footnote": 1, "footnotetext": 1,
    "thanks": 1, "includegraphics": 1, "vspace": 1, "hspace": 1,
    "setlength": 2, "addtolength": 2, "setcounter": 2,
    "addtocounter": 2, "newcommand": 2, "renewcommand": 2,
    "providecommand": 2, "newenvironment": 3, "renewenvironment": 3,
    "DeclareMathOperator": 2, "definecolor": 3, "color": 1,
    "textcolor": 1, "colorbox": 1, "pagestyle": 1, "thispagestyle": 1,
    "bibliographystyle": 1, "input": 1, "include": 1, "graphicspath": 1,
    "usepackage": 1, "documentclass": 1, "title": 1, "author": 1,
    "affiliation": 1, "institution": 1, "email": 1, "orcid": 1, "date": 1,
    "keywords": 1, "ccsdesc": 1, "IEEEauthorblockN": 1,
    "IEEEauthorblockA": 1, "resizebox": 2, "scalebox": 1, "raisebox": 1,
    "rule": 2, "todo": 1, "ding": 1, "fontsize": 2, "hyphenation": 1,
    "newtheorem": 2, "setcopyright": 1, "copyrightyear": 1,
    "settopmatter": 1, "hypersetup": 1, "captionsetup": 1, "caption": 1,
    "subcaption": 1, "subfloat": 1, "lstset": 1, "lstinputlisting": 1,
    "bibitem": 1, "nocite": 1, "addbibresource": 1, "newacronym": 3,
    "newglossaryentry": 2, "tikzset": 1, "pgfplotsset": 1, "usetikzlibrary": 1,
    "multicolumn": 2, "multirow": 2, "cline": 1, "cmidrule": 1,
    "markboth": 2, "titlenote": 1, "additionalaffiliation": 1,
    "authornote": 1, "received": 1, "IEEEpubid": 1, "pdfinfo": 1,
    "special": 1, "linespread": 1, "enlargethispage": 1, "pagenumbering": 1,
    "affil": 1, "address": 1, "titlerunning": 1, "authorrunning": 1,
    "shorttitle": 1, "shortauthors": 1, "SetKwInOut": 2, "SetKw": 2,
    "SetKwFunction": 2, "crefname": 3, "Crefname": 3, "theoremstyle": 1,
    "bibliography": 1, "printbibliography": 0, "section": 1,
    "subsection": 1, "subsubsection": 1, "paragraph": 1, "subparagraph": 1,
    "chapter": 1, "part": 1,
    # settings: key=value arguments, never prose
    "setlist": 1, "setitemize": 1, "setenumerate": 1, "sisetup": 1,
    "geometry": 1, "newgeometry": 1, "titlespacing": 1, "titleformat": 2,
    "setcitestyle": 1, "newcolumntype": 2, "setstretch": 1,
    "AtBeginDocument": 1, "bibpunct": 1, "algrenewcommand": 2,
    "algnewcommand": 2, "renewrobustcmd": 2, "DeclareRobustCommand": 2,
}
DROP_RE = re.compile(r"\\(?:cite[A-Za-z]*|[Rr]ef[A-Za-z]*|[A-Za-z]*[Rr]ef|"
                     r"acm[A-Z][A-Za-z]*)"
                     r"(?![A-Za-z])")
ENV_ARGS = {"minipage": 1, "multicols": 1, "wrapfigure": 2, "tabular": 1,
            "tabularx": 2, "adjustbox": 1, "list": 2, "tcolorbox": 0}
STRUCTURAL = {"preamble", "after end", "back matter", "comment",
              "abstract", "acknowledgements"}
HEADINGS = r"(?:section|subsection|subsubsection|paragraph|subparagraph|" \
           r"chapter|part)"


class Masker:
    def __init__(self, text):
        self.text = text
        self.out = list(text)
        w = list(text)
        self.esc = set()
        i, n = 0, len(text)
        while i < n:
            if text[i] == "\\" and i + 1 < n:
                if text[i + 1] in ESCAPES:
                    self.out[i] = " "
                    w[i] = w[i + 1] = "\0"
                    self.esc.add(i + 1)
                    i += 2
                    continue
                i += 2
                continue
            i += 1
        self.w = w
        self.cat = Counter()

    def ws(self):
        return "".join(self.w)

    def blank(self, lo, hi, cat):
        out, w, text = self.out, self.w, self.text
        for i in range(max(lo, 0), min(hi, len(text))):
            if not text[i].isspace():
                if out[i] != " ":
                    self.cat[cat] += 1
                out[i] = " "
                w[i] = " "

    # --- helpers on the work string
    def brace(self, s, i, limit=200000):
        """s[i] == '{'. Index after its matching '}', or None."""
        depth, j, end = 0, i, min(len(s), i + limit)
        while j < end:
            c = s[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return j + 1
            j += 1
        return None

    def bracket(self, s, i):
        """s[i] == '['. Index after its matching ']' within 500 chars."""
        depth, j, end = 0, i, min(len(s), i + 500)
        while j < end:
            c = s[j]
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    return j + 1
            elif c == "\n" and s[j + 1:j + 2] == "\n":
                return None
            j += 1
        return None

    def args(self, s, j, nbrace):
        """Consume optional [..] (adjacent) and up to nbrace {..} groups."""
        got = 0
        while j < len(s):
            k = j
            while k < len(s) and s[k] in " \t":
                k += 1
            if k < len(s) and s[k] == "\n":
                k += 1
                while k < len(s) and s[k] in " \t":
                    k += 1
            if k < len(s) and s[k] == "[" and k == j:
                e = self.bracket(s, k)
                if e is None:
                    break
                j = e
                continue
            if k < len(s) and s[k] == "{" and got < nbrace:
                e = self.brace(s, k)
                if e is None:
                    break
                j, got = e, got + 1
                continue
            if k < len(s) and s[k] == "*" and k == j:
                j += 1
                continue
            break
        return j

    def env_regions(self, names):
        """(lo, hi) of outermost \\begin{name}...\\end{name}, starred too."""
        s = self.ws()
        alt = "|".join(re.escape(n) for n in sorted(set(names), key=len,
                                                    reverse=True))
        pat = re.compile(r"\\(begin|end)\s*\{(" + alt + r")\*?\}")
        regions, i = [], 0
        while True:
            m = pat.search(s, i)
            if not m:
                break
            if m.group(1) == "end":
                i = m.end()
                continue
            name, depth, j = m.group(2), 1, m.end()
            inner = re.compile(r"\\(begin|end)\s*\{" + re.escape(name)
                               + r"\*?\}")
            hi = len(s)
            while True:
                n2 = inner.search(s, j)
                if not n2:
                    break
                depth += 1 if n2.group(1) == "begin" else -1
                j = n2.end()
                if depth == 0:
                    hi = j
                    break
            regions.append((m.start(), hi))
            i = hi
        return regions

    # --- the rules, in order
    def run(self):
        text = self.text
        # verbatim-like environments and \verb before comments, since a
        # % inside them is not a comment
        for lo, hi in self.env_regions(VERB_ENVS):
            self.blank(lo, hi, "floats and code")
        s = self.ws()
        for m in re.finditer(r"\\verb\*?([^A-Za-z\s*])[^\n]*?\1", s):
            self.blank(m.start(), m.end(), "floats and code")
        # comments
        s = self.ws()
        for m in re.finditer(r"%[^\n]*", s):
            self.blank(m.start(), m.end(), "comment")
        s = self.ws()
        # preamble and anything after \end{document}
        m = re.search(r"\\begin\s*\{document\}", s)
        body_lo = 0
        if m:
            self.blank(0, m.end(), "preamble")
            body_lo = m.end()
        s = self.ws()
        m = re.search(r"\\end\s*\{document\}", s[body_lo:])
        body_hi = len(text)
        if m:
            body_hi = body_lo + m.start()
            self.blank(body_hi, len(text), "after end")
        s = self.ws()
        # back matter: bibliography and appendices, to the end
        m = re.search(r"\\begin\s*\{thebibliography\}|\\bibliography\s*\{|"
                      r"\\printbibliography|\\appendix(?![A-Za-z])|"
                      r"\\begin\s*\{appendix|\\begin\s*\{appendices\}",
                      s[body_lo:])
        cut = body_hi
        if m:
            cut = body_lo + m.start()
        # sections are recorded here, before headings are blanked
        self.sections = self.find_sections(s, body_lo, body_hi)
        self.body = (body_lo, cut)
        if cut < body_hi:
            self.blank(cut, body_hi, "back matter")
        # acknowledgements
        for lo, hi in self.env_regions(ACK_ENVS):
            self.blank(lo, hi, "acknowledgements")
        s = self.ws()
        for m in re.finditer(r"\\(?:" + HEADINGS + r")\*?\s*\{\s*"
                             r"acknowledge?ments?\s*\}|\\acknowledge?ments?"
                             r"(?![A-Za-z])", s, re.I):
            nxt = re.compile(r"\\(?:section|chapter)\*?\s*[\[{]")
            n2 = nxt.search(s, m.end())
            self.blank(m.start(), n2.start() if n2 else cut,
                       "acknowledgements")
        # abstract
        for lo, hi in self.env_regions(["abstract"]):
            self.blank(lo, hi, "abstract")
        s = self.ws()
        for m in re.finditer(r"\\abstract\s*\{", s):
            e = self.brace(s, m.end() - 1)
            if e:
                self.blank(m.start(), e, "abstract")
        # floats, code and tables
        for lo, hi in self.env_regions(FLOAT_ENVS):
            self.blank(lo, hi, "floats and code")
        # math environments
        for lo, hi in self.env_regions(MATH_ENVS):
            self.blank(lo, hi, "math")
        self.inline_math()
        # captions anywhere, headings, and commands blanked with their
        # arguments
        s = self.ws()
        self.ieee_parstart(s)
        s = self.ws()
        for m in re.finditer(r"\\([A-Za-z@]+)\*?", s):
            name = m.group(1)
            if s[m.start()] != "\\":
                continue        # already blanked by an earlier match
            if name in DROP:
                n = DROP[name]
            elif DROP_RE.match(s, m.start()):
                n = 4 if name.startswith("acm") else 1
            elif name == "def":
                e = re.match(r"\\def\s*\\[A-Za-z@]+[^{\n]*", s[m.start():])
                j = m.start() + e.end() if e else m.end()
                if j < len(s) and s[j] == "{":
                    hi = self.brace(s, j)
                    if hi:
                        self.blank(m.start(), hi, "commands")
                        s = self.ws()
                continue
            elif name in ("begin", "end"):
                e = re.match(r"\\(?:begin|end)\s*\{([^{}]*)\}", s[m.start():])
                if not e:
                    continue
                j = m.start() + e.end()
                env = e.group(1).rstrip("*")
                if name == "begin":
                    j = self.args(s, j, ENV_ARGS.get(env, 0))
                self.blank(m.start(), j, "commands")
                s = self.ws()
                continue
            elif name in ("kern", "mkern", "hskip", "vskip", "mskip"):
                e = re.match(r"\\[a-z]+\s*-?[\d.]+\s*(?:pt|em|mm|ex|cm|in|bp|"
                             r"mu)(?:\s*(?:plus|minus)\s*-?[\d.]+\s*"
                             r"(?:pt|em|mm|ex|cm|in|bp|mu|fil+))*",
                             s[m.start():])
                j = m.start() + e.end() if e else m.end()
                self.blank(m.start(), j, "commands")
                s = self.ws()
                continue
            elif re.match(r"\s*\{[A-Za-z]+:[^\s{}]*\}", s[m.end():]):
                # an unknown macro whose argument is a label key
                # (\Fig{fig:arch}) is a reference macro
                j = self.args(s, m.end(), 1)
                self.blank(m.start(), j, "references")
                s = self.ws()
                continue
            elif name == "item":
                j = self.args(s, m.end(), 0)
                self.blank(m.start(), j, "commands")
                s = self.ws()
                continue
            else:
                continue
            j = self.args(s, m.end(), n)
            cat = ("headings" if re.fullmatch(HEADINGS, name)
                   else "floats and code" if name in ("caption",
                                                      "subcaption",
                                                      "subfloat")
                   else "references" if DROP_RE.match(s, m.start())
                   or name in ("label", "url", "href")
                   else "footnotes" if name in ("footnote", "footnotetext",
                                                "thanks")
                   else "commands")
            self.blank(m.start(), j, cat)
            s = self.ws()
        # dashes, counted on the text that is left
        s = self.ws()
        kept = "".join(self.out)
        self.dashes = {
            "tex_emdash": len(re.findall(r"(?<!-)---(?!-)", s)),
            "spaced_endash": len(re.findall(r"(?<=\s)--(?=\s)", s)),
            "unicode_emdash": kept.count("\u2014"),
            "unicode_endash": kept.count("\u2013"),
        }
        for m in re.finditer(r"(?<!-)---(?!-)", s):
            i = m.start()
            self.out[i] = "\u2014"
            self.out[i + 1] = self.out[i + 2] = " "
            self.w[i] = "\u2014"
            self.w[i + 1] = self.w[i + 2] = " "
        self.join_letters()
        # generic commands: the name and an adjacent [..]; the argument
        # text stays (\emph{x} keeps x, and so do unknown user macros)
        s = self.ws()
        for m in re.finditer(r"\\[A-Za-z@]+\*?|\\[^A-Za-z@\0]", s):
            if self.w[m.start()] != "\\":
                continue
            j = m.end()
            if j < len(s) and s[j] == "[" and m.group(0)[1:2].isalpha():
                e = self.bracket("".join(self.w), j)
                j = e or j
            self.blank(m.start(), j, "commands")
        s = self.ws()
        for i, c in enumerate(s):
            if c in "{}&":
                self.blank(i, i + 1, "commands")
            elif c == "~":
                self.out[i] = self.w[i] = " "
        return "".join(self.out)

    def inline_math(self):
        s = self.ws()
        for m in re.finditer(r"\\\[.*?\\\]|\\\(.*?\\\)", s, re.S):
            self.blank(m.start(), m.end(), "math")
        s = self.ws()
        i, n = 0, len(s)
        while True:
            i = s.find("$", i)
            if i < 0:
                break
            if s.startswith("$$", i):
                j = s.find("$$", i + 2)
                if j < 0:
                    self.blank(i, i + 2, "math")
                    i += 2
                    continue
                self.blank(i, j + 2, "math")
                i = j + 2
                continue
            j = s.find("$", i + 1)
            para = re.search(r"\n[ \t]*\n", s[i:j]) if j > 0 else None
            if j < 0 or para:
                self.blank(i, i + 1, "math")       # stray $
                i += 1
                continue
            self.blank(i, j + 1, "math")
            i = j + 1
        _ = n

    def join_letters(self):
        """\\textbf{S}ystem and {\\bf S}ystem: the argument is written
        right-aligned against the following letter, so the word is not
        split by the blanked closing brace. The command is blanked; offsets
        outside it hold, and the argument moves by at most its brace.
        """
        s = self.ws()
        for m in re.finditer(r"\\[A-Za-z]+\s*\{([A-Za-z]{1,3})\}(?=[a-z])"
                             r"|\{\\[A-Za-z]+\s+([A-Za-z]{1,3})\}(?=[a-z])",
                             s):
            if s[m.start()] not in "\\{":
                continue
            word = m.group(1) or m.group(2)
            self.blank(m.start(), m.end(), "commands")
            at = m.end() - len(word)
            self.cat["commands"] -= len(word)     # written back, not lost
            for k, ch in enumerate(word):
                self.out[at + k] = ch
                self.w[at + k] = ch

    def ieee_parstart(self, s):
        """\\IEEEPARstart{T}{he} -> "The" written at the command's start.

        The two arguments are joined so the first word is not split; the
        rest of the command is blanked. Offsets outside the command hold.
        """
        for m in re.finditer(r"\\IEEEPARstart\s*\{([^{}]*)\}\s*\{([^{}]*)\}",
                             s):
            word = m.group(1) + m.group(2)
            self.blank(m.start(), m.end(), "commands")
            self.cat["commands"] -= len(word)     # written back, not lost
            for k, ch in enumerate(word):
                self.out[m.start() + k] = ch
                self.w[m.start() + k] = ch

    def find_sections(self, s, lo, hi):
        """[(start, heading text, class)] for each \\section in [lo, hi)."""
        out = []
        for m in re.finditer(r"\\section\*?\s*(?:\[[^\]]*\])?\s*\{", s[:hi]):
            if m.start() < lo:
                continue
            e = self.brace(s, m.end() - 1)
            if not e:
                continue
            out.append((m.start(), clean_heading(s[m.end():e - 1])))
        return out


def clean_heading(h):
    h = re.sub(r"\\[A-Za-z@]+\*?", " ", h)
    h = re.sub(r"[{}\\$~]", " ", h)
    return " ".join(h.split())


SECTION_RULE = (
    "A section runs from its \\section heading to the next one. The first "
    "section, or any heading containing \"introduction\", is introduction. "
    "Otherwise a heading containing \"conclusion\", \"summary\" or \"future "
    "work\" is conclusion, and one containing \"related work\", "
    "\"background\" or \"prior work\" is related. Everything else is body. "
    "Matching ignores case. Text between \\begin{document} and the first "
    "\\section (after the title, abstract and keywords are masked) counts "
    "as introduction, since an unheaded opening is the introduction; a "
    "paper with no \\section is all introduction.")


def classify_heading(h, first):
    s = h.lower()
    if first or "introduction" in s:
        return "introduction"
    if any(k in s for k in ("conclusion", "summary", "future work")):
        return "conclusion"
    if any(k in s for k in ("related work", "background", "prior work")):
        return "related"
    return "body"


def section_spans(sections, lo, hi):
    """[(start, end, class)] covering [lo, hi)."""
    spans = []
    starts = [p for p, _ in sections]
    first = starts[0] if starts else hi
    if first > lo:
        spans.append((lo, first, "introduction"))
    for k, (p, h) in enumerate(sections):
        end = starts[k + 1] if k + 1 < len(starts) else hi
        spans.append((p, end, classify_heading(h, k == 0)))
    return spans


def mask_tex(text):
    """(masked text, info). len(masked) == len(text)."""
    mk = Masker(text)
    masked = mk.run()
    assert len(masked) == len(text)
    nonws = sum(1 for c in text if not c.isspace())
    blanked = sum(mk.cat.values())
    structural = sum(v for k, v in mk.cat.items() if k in STRUCTURAL)
    lo, hi = mk.body
    spans = section_spans(mk.sections, lo, len(text))
    return masked, {
        "nonws": nonws, "blanked": blanked, "structural": structural,
        "by_category": dict(mk.cat), "dashes": mk.dashes,
        "sections": spans, "n_headings": len(mk.sections),
        "body": [lo, hi],
    }


# ------------------------------------------------------------ selftest

D = "\\documentclass{article}\\usepackage{x}\n\\begin{document}\n"
E = "\n\\end{document}\n"
MASK_ROWS = [
    # (name, input, expected masked text with whitespace collapsed)
    ("plain text kept", "We build a cache.", "We build a cache."),
    ("preamble and end", D + "Body text." + E + "trailing", "Body text."),
    ("comment", "Keep this. % drop this\nAnd this.", "Keep this. And this."),
    ("escaped percent is not a comment", "A 50\\% gain.", "A 50 % gain."),
    ("inline math", "where $x_i$ is the input.", "where is the input."),
    ("escaped dollar is not math", "It costs \\$5 and $y$ more.",
     "It costs $5 and more."),
    ("display math", "Then \\[ a = b \\] holds and $$c$$ too.",
     "Then holds and too."),
    ("paren math", "so \\(n^2\\) grows", "so grows"),
    ("equation env", "Let\n\\begin{equation}\na=b\n\\end{equation}\nhold.",
     "Let hold."),
    ("starred align", "x \\begin{align*} a&=b \\\\ c&=d \\end{align*} y",
     "x y"),
    ("figure with caption", "A.\n\\begin{figure}[t]\\centering"
     "\\includegraphics{f}\\caption{The design.}\\end{figure}\nB.", "A. B."),
    ("nested table", "\\begin{table*}\\begin{tabular}{lc} a & b\\\\"
     "\\end{tabular}\\end{table*}Next.", "Next."),
    ("algorithm", "\\begin{algorithm}\\State x\\end{algorithm} done",
     "done"),
    ("lstlisting keeps no code and no fake comment",
     "Code:\n\\begin{lstlisting}\nint x; % not a comment\n"
     "\\end{lstlisting}\nAfter.", "Code: After."),
    ("verbatim", "\\begin{verbatim}\n$x$ {\n\\end{verbatim}\nok", "ok"),
    ("verb", "Use \\verb|a{b}| here.", "Use here."),
    ("tikz", "\\begin{tikzpicture}\\node{A};\\end{tikzpicture}Text.",
     "Text."),
    ("cite and ref", "As shown~\\cite{a,b} in Fig.~\\ref{fig:x} and "
     "\\citep[p.~3]{c}.", "As shown in Fig. and ."),
    ("cref and label", "See \\Cref{sec:y}.\\label{sec:z}", "See ."),
    ("user ref macro", "In \\figref{fig:arch} we", "In we"),
    ("url and href", "at \\url{http://x.org/a} or \\href{http://y}{the site}.",
     "at or the site ."),
    ("footnote with nesting", "Fast\\footnote{See \\emph{this}.} enough.",
     "Fast enough."),
    ("emph keeps argument", "a \\emph{very} \\textbf{big} \\textit{cache}",
     "a very big cache"),
    ("unknown macro keeps argument", "the \\sysname{} design and "
     "\\mytool{Foo} runs", "the design and Foo runs"),
    ("zero-arg macro blanked", "Our \\name\\ is fast.", "Our is fast."),
    ("item marker", "\\begin{itemize}\n\\item First.\n\\item[(b)] Second."
     "\n\\end{itemize}", "First. Second."),
    ("abstract env", D + "\\title{T}\\maketitle\n\\begin{abstract}Abs."
     "\\end{abstract}\nIntro." + E, "Intro."),
    ("acks env", "Text.\\begin{acks}Thanks to X.\\end{acks}", "Text."),
    ("ack section", "\\section{Results}Good.\\section*{Acknowledgments}"
     "We thank X.\\section{More}Tail.", "Good. Tail."),
    ("bibliography cut", "End.\n\\bibliographystyle{plain}\n"
     "\\bibliography{refs}\nAfter bib.", "End."),
    ("thebibliography cut", "End.\\begin{thebibliography}{9}\\bibitem{a} X."
     "\\end{thebibliography}", "End."),
    ("appendix cut", "Main.\n\\appendix\n\\section{Proofs}Proof text.",
     "Main."),
    ("tex em dash", "fast---and small", "fast\u2014 and small"),
    ("en dash kept", "pages 3--5 and a -- b", "pages 3--5 and a -- b"),
    ("dash in math not converted", "$a---b$ end", "end"),
    ("heading blanked", "\\section{Design}\\label{sec:d}We\n"
     "\\subsection*{Cache}It.", "We It."),
    ("paragraph heading", "\\paragraph{Setup.} We run.", "We run."),
    ("layout commands", "\\vspace{-2mm}\\noindent Text\\\\ next.",
     "Text next."),
    ("accent", "Andr\\'{e} said", "Andr e said"),
    ("tilde and braces", "Fig.~3 {grouped}", "Fig. 3 grouped"),
    ("textcolor keeps text", "\\textcolor{red}{Note} this", "Note this"),
    ("ieee parstart", "\\IEEEPARstart{T}{he} memory wall",
     "The memory wall"),
    ("minipage width", "\\begin{minipage}{0.5\\linewidth}In box."
     "\\end{minipage}", "In box."),
    ("stray dollar stays local", "Price $5\n\nNew para $x$.",
     "Price 5 New para ."),
    ("newcommand in body", "\\newcommand{\\foo}[1]{bar #1}Text.", "Text."),
    ("keywords env", "\\begin{IEEEkeywords}cache, DRAM\\end{IEEEkeywords}"
     "Text.", "Text."),
    ("settings commands", "\\setlist{leftmargin=0.5cm}\\sisetup{x=y}"
     "Text.", "Text."),
    ("acronym letter joins its word", "SPEAR (\\textbf{S}ystem for "
     "\\underline{P}ost) runs", "SPEAR ( System for Post) runs"),
    ("old-style acronym letter", "a {\\bf M}emory unit", "a Memory unit"),
    ("joined letters keep length", "\\textbf{Ab}cd", "Abcd"),
    ("user ref macros, any case", "See \\figRef{a} and \\refEqn{b} and "
     "\\Ref{c}.", "See and and ."),
    ("user macro with a label key", "In \\Fig{fig:arch} and \\Sect{sec:eval}"
     " we", "In and we"),
    ("macro argument with a colon and spaces is kept",
     "\\note{Rule: keep this} now", "Rule: keep this now"),
    ("kern and skip dimensions", "a\\kern-0.5em b\\vskip 2pt c\\hskip1em d",
     "a b c d"),
]

# Lorem ipsum and blindtext words. A source whose kept text holds many of
# them is a template with the real pages included as images.
PLACEHOLDER = re.compile(r"\b(?:lorem|ipsum|consectetuer|adipiscing|aenean|"
                         r"vokalia|consonantia|blindtext)\b", re.I)
PLACEHOLDER_MIN = 20
PLACEHOLDER_ROWS = [
    ("lorem " * 25, True),
    ("Far far away, behind the word mountains, far from the countries "
     "Vokalia and Consonantia " * 12, True),
    ("We place the ipsum lorem example once, then real text. " * 3, False),
]
SECTION_ROWS = [
    # (headings in order, expected classes)
    (["Introduction", "Design", "Related Work", "Conclusion"],
     ["introduction", "body", "related", "conclusion"]),
    (["Motivation", "Background", "Evaluation", "Summary and Future Work"],
     ["introduction", "related", "body", "conclusion"]),
    (["Overview", "1 Introduction", "Prior Work", "Results"],
     ["introduction", "introduction", "related", "body"]),
    (["Introduction", "Conclusions"], ["introduction", "conclusion"]),
    (["Intro", "Future work"], ["introduction", "conclusion"]),
    (["INTRODUCTION", "BACKGROUND AND MOTIVATION", "Discussion"],
     ["introduction", "related", "body"]),
]


def cmd_selftest(args):
    fails = 0
    for name, src, want in MASK_ROWS:
        got, info = mask_tex(src)
        ok = len(got) == len(src) and " ".join(got.split()) == want
        # newlines and offsets: whitespace in the input stays put
        ok = ok and all(got[i] == src[i] for i, c in enumerate(src)
                        if c == "\n")
        if not ok or args.verbose:
            print(f"{'ok ' if ok else 'FAIL'} mask: {name}")
        if not ok:
            print(f"     want {want!r}\n     got  {' '.join(got.split())!r}"
                  f" (len {len(got)} vs {len(src)})")
            fails += 1
    for heads, want in SECTION_ROWS:
        got = [classify_heading(h, k == 0) for k, h in enumerate(heads)]
        ok = got == want
        if not ok or args.verbose:
            print(f"{'ok ' if ok else 'FAIL'} section: {heads}")
        if not ok:
            print(f"     want {want}\n     got  {got}")
            fails += 1
    for src, want in PLACEHOLDER_ROWS:
        got = is_placeholder(src)
        ok = got == want
        if not ok or args.verbose:
            print(f"{'ok ' if ok else 'FAIL'} placeholder: {src[:30]!r}")
        if not ok:
            fails += 1
    # spans from a synthetic paper
    src = (D + "\\title{T}\\maketitle\nOpening.\n\\section{Design}A.\n"
           "\\section{Related Work}B.\n\\section{Conclusion}C.\n"
           "\\bibliography{r}" + E)
    masked, info = mask_tex(src)
    cls = []
    for lo, hi, c in info["sections"]:
        if masked[lo:hi].split():
            cls.append((c, " ".join(masked[lo:hi].split())))
    want = [("introduction", "Opening."), ("introduction", "A."),
            ("related", "B."), ("conclusion", "C.")]
    ok = cls == want
    if not ok or args.verbose:
        print(f"{'ok ' if ok else 'FAIL'} spans: synthetic paper")
    if not ok:
        print(f"     want {want}\n     got  {cls}")
        fails += 1
    n = len(MASK_ROWS) + len(SECTION_ROWS) + len(PLACEHOLDER_ROWS) + 1
    print(f"selftest: {n - fails}/{n} rows pass")
    return 1 if fails else 0


# ---------------------------------------------------------------- fetch

def window_ids(window):
    ids = sorted({pid for m in AR.manifests(window) for pid in m["primary"]})
    random.Random(f"{BODY_SEED}-bodies-{window}").shuffle(ids)
    return ids


def is_placeholder(s):
    return len(PLACEHOLDER.findall(s)) >= PLACEHOLDER_MIN


def words_of(s):
    return len(re.findall(r"[A-Za-z]+", s))


def process(pid, data):
    """Unpack, find the main file, expand, mask. Returns a record."""
    files, why = unpack(data)
    if files is None:
        return {"status": why}
    try:
        main, expanded, info = find_main(files)
    except RecursionError:
        return {"status": "unpack error"}
    if main is None:
        return {"status": "no main file found", **info}
    out = EXP / (pid.replace("/", "_") + ".tex")
    out.write_text(expanded, encoding="utf-8")
    masked, minfo = mask_tex(expanded)
    nw = words_of(masked)
    status = ("placeholder text" if is_placeholder(masked)
              else "too little text" if nw < MIN_WORDS else "ok")
    rec = {"status": status,
           "words_regex": nw, "chars": len(expanded), **info, **minfo}
    return rec


def cmd_fetch(args):
    for d in (SRC, EXP, BODY):
        d.mkdir(parents=True, exist_ok=True)
    sample = {"seed": BODY_SEED, "want": WANT, "windows": {}}
    records = []
    fetched = []
    t0 = time.monotonic()
    try:
        for window in AR.WINDOWS:
            ids = window_ids(window)
            kept, skips, walked = [], Counter(), 0
            for pid in ids:
                if len(kept) >= WANT:
                    break
                walked += 1
                data, new = cached_source(pid, fetched)
                rec = process(pid, data)
                rec.update({"id": pid, "window": window, "order": walked})
                records.append(rec)
                if rec["status"] == "ok":
                    kept.append(pid)
                else:
                    skips[rec["status"]] += 1
                if new and len(fetched) % 25 == 0:
                    print(f"  {window}: walked {walked}, kept {len(kept)}, "
                          f"fetched {len(fetched)} this run, "
                          f"{time.monotonic() - t0:.0f}s", file=sys.stderr)
            sample["windows"][window] = {
                "population": len(ids), "walked": walked, "kept": kept,
                "skips": dict(skips)}
            print(f"{window}: kept {len(kept)} of {walked} walked; skipped "
                  f"{dict(skips)}")
    finally:
        if records:
            RECORDS.write_text("".join(json.dumps(r) + "\n"
                                       for r in records), encoding="utf-8")
        if len(sample["windows"]) == len(AR.WINDOWS):
            SAMPLE_FILE.write_text(json.dumps(sample, indent=1),
                                   encoding="utf-8")
        print(f"fetched {len(fetched)} archives this run", file=sys.stderr)


# --------------------------------------------------------- mask-report

def load_records():
    if not SAMPLE_FILE.exists():
        sys.exit("no sample; run fetch first")
    sample = json.loads(SAMPLE_FILE.read_text())
    recs = {}
    for line in RECORDS.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        recs[(r["window"], r["id"])] = r
    return sample, recs


RESIDUE = {
    "backslash or brace": re.compile(r"[\\{}]"),
    "dollar, caret or underscore": re.compile(r"[$^_]"),
    "length or dimension": re.compile(
        r"(?<![\w.])-?\d*\.?\d+\s?(?:pt|mm|cm|em|ex|bp|in)\b"),
    "label key": re.compile(r"\b(?:fig|tab|sec|eq|alg|lst|app|chap)"
                            r"[:_]\w+", re.I),
    "column spec": re.compile(r"(?<!\w)[lcr|]{3,}(?!\w)"),
    "environment name": re.compile(
        r"\b(?:itemize|enumerate|tabular|figure\*|minipage|center)\b"),
    "dangling bracket option": re.compile(r"^\s*\[[^\]]{0,20}\]"),
}


def sentences(masked, lo, hi):
    flat = " ".join(masked[lo:hi].split())
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'`])", flat)
    return [p for p in parts if len(p.split()) >= 5]


def pct_summary(vals):
    v = sorted(vals)
    if not v:
        return "-"
    med = v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1]
                                             + v[len(v) // 2]) / 2
    return f"min {v[0]:.1f}%, median {med:.1f}%, max {v[-1]:.1f}%"


def cmd_mask_report(args):
    sample, recs = load_records()
    print(f"seed {sample['seed']} (shuffle key \"{sample['seed']}-bodies-"
          "<window>\"), target "
          f"{sample['want']} usable papers per window\n")
    for window, ws in sample["windows"].items():
        rows = [recs[(window, p)] for p in ws["kept"]]
        tot = [100 * r["blanked"] / max(r["nonws"], 1) for r in rows]
        inb = [100 * (r["blanked"] - r["structural"])
               / max(r["nonws"] - r["structural"], 1) for r in rows]
        ties = [recs[(window, p)] for p in ws["kept"]
                if recs[(window, p)]["candidates"] > 1]
        unres = sum(r["unresolved"] for r in rows)
        dash = Counter()
        for r in rows:
            dash.update(r["dashes"])
        cats = Counter()
        for r in rows:
            cats.update(r["by_category"])
        print(f"=== {window}: population {ws['population']}, walked "
              f"{ws['walked']}, kept {len(ws['kept'])}")
        print(f"  skipped: {ws['skips'] or 'none'}")
        print(f"  masked share, all non-space chars: {pct_summary(tot)}; "
              f"over 40%: {sum(1 for x in tot if x > 40)}")
        print(f"  masked share inside the kept body (preamble, comments, "
              f"abstract, acks and back matter excluded): {pct_summary(inb)};"
              f" over 40%: {sum(1 for x in inb if x > 40)}")
        allnw = sum(cats.values()) or 1
        print("  blanked chars by rule: " + ", ".join(
            f"{k} {100 * v / allnw:.1f}%" for k, v in cats.most_common()))
        print(f"  several main-file candidates: {len(ties)} (tie broken by "
              "longest expanded text); unresolved \\input: "
              f"{unres}; latin-1 decoded files: "
              f"{sum(r['latin1_files'] for r in rows)}")
        print(f"  papers with no \\section: "
              f"{sum(1 for r in rows if r['n_headings'] == 0)}")
        cls = Counter()
        for r in rows:
            for lo, hi, c in r["sections"]:
                cls[c] += 1
        print(f"  sections by class: {dict(cls)}")
        print(f"  dashes in kept text: TeX --- {dash['tex_emdash']}, spaced "
              f"-- {dash['spaced_endash']}, Unicode em dash "
              f"{dash['unicode_emdash']}, Unicode en dash "
              f"{dash['unicode_endash']}")
        print(f"  words (regex, kept text): total "
              f"{sum(r['words_regex'] for r in rows):,}, mean "
              f"{sum(r['words_regex'] for r in rows) / len(rows):,.0f}")
        # automatic residue scan over every sentence
        hits, nsent = Counter(), 0
        pool = []
        for p in ws["kept"]:
            src = (EXP / (p.replace("/", "_") + ".tex")).read_text(
                encoding="utf-8")
            masked, info = mask_tex(src)
            lo, hi = info["body"]
            ss = sentences(masked, lo, hi)
            nsent += len(ss)
            for s in ss:
                for k, rx in RESIDUE.items():
                    if rx.search(s):
                        hits[k] += 1
                pool.append(s)
        print(f"  residue scan over {nsent:,} sentences: " + (", ".join(
            f"{k} {v} ({100 * v / nsent:.2f}%)" for k, v in hits.items())
            or "no hits"))
        rng = random.Random(f"{BODY_SEED}-spot-{window}")
        pick = rng.sample(pool, min(args.n, len(pool)))
        if not args.quiet:
            print(f"\n  --- {len(pick)} random masked sentences ({window}); "
                  "console only")
            for i, s in enumerate(pick, 1):
                print(f"  [{window} {i}] {s}")
        print()


def cmd_analyse(args):
    sys.exit("analyse is phase 2 and is not written yet")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="fetch and prepare the source sample")
    s = sub.add_parser("selftest", help="masker and section-classifier rows")
    s.add_argument("-v", "--verbose", action="store_true")
    m = sub.add_parser("mask-report", help="masked shares, skips, and a "
                       "console spot-check of masked sentences")
    m.add_argument("-n", type=int, default=40,
                   help="sentences per window (default 40)")
    m.add_argument("-q", "--quiet", action="store_true",
                   help="figures only, no sentences")
    a = sub.add_parser("analyse", help="phase 2")
    a.add_argument("--draws", type=int, default=2000)
    args = ap.parse_args()
    if args.cmd != "selftest" and not (AR.ROOT / ".gitignore").read_text() \
            .count("private/"):
        sys.exit("private/ is not in .gitignore; refusing to cache there")
    rc = {"fetch": cmd_fetch, "selftest": cmd_selftest,
          "mask-report": cmd_mask_report, "analyse": cmd_analyse}[args.cmd](
        args)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
