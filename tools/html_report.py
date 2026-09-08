"""HTML side-by-side report generator for ticfinder."""
import html
import json
from pathlib import Path

CONF_COLOR = {"high": "#c1440e", "med": "#b8860b", "low": "#6b7280"}

CSS = """
:root{--bg:#fbfaf8;--fg:#1c1a17;--mut:#6b6560;--line:#e3ded6;--card:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#16150f;--fg:#e8e4dc;
--mut:#9a938a;--line:#2f2c26;--card:#1e1c16}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.65 ui-sans-serif,-apple-system,"Segoe UI",sans-serif}
header{padding:18px 24px;border-bottom:1px solid var(--line);
display:flex;gap:24px;align-items:baseline;flex-wrap:wrap;
position:sticky;top:0;background:var(--bg);z-index:10}
h1{font-size:17px;margin:0;font-weight:600}
.meta{color:var(--mut);font-size:13px}
.wrap{display:grid;grid-template-columns:1fr 380px;gap:0;
align-items:start}
@media(max-width:900px){.wrap{grid-template-columns:1fr}}
.src{padding:24px 28px;white-space:pre-wrap;
font:14px/1.75 ui-monospace,"SF Mono",Menlo,monospace;
border-right:1px solid var(--line);min-height:100vh}
.side{padding:18px;position:sticky;top:64px;max-height:calc(100vh - 64px);
overflow:auto}
mark{padding:1px 2px;border-radius:3px;cursor:pointer;
border-bottom:2px solid currentColor;background:transparent;color:inherit}
mark.high{background:rgba(193,68,14,.16);border-color:#c1440e}
mark.med{background:rgba(184,134,11,.16);border-color:#b8860b}
mark.low{background:rgba(107,114,128,.13);border-color:#9ca3af}
mark.on{outline:2px solid var(--fg);outline-offset:1px}
mark.off{background:transparent!important;border-color:transparent!important}
.f{padding:8px 10px;border:1px solid var(--line);border-radius:6px;
margin-bottom:6px;background:var(--card);cursor:pointer;font-size:13px}
.f:hover{border-color:var(--mut)}
.f .cid{font-weight:600;font-size:11px;letter-spacing:.04em}
.f .ln{color:var(--mut);font-size:11px;float:right}
.f .tx{color:var(--mut);margin-top:3px;
font-family:ui-monospace,monospace;font-size:12px}
.leg{margin-bottom:14px}
.leg label{display:flex;align-items:center;gap:7px;padding:3px 0;
font-size:12.5px;cursor:pointer;user-select:none}
.leg .n{margin-left:auto;color:var(--mut);font-variant-numeric:tabular-nums}
.sw{width:9px;height:9px;border-radius:2px;flex:none}
.note{color:var(--mut);font-size:12px;margin:6px 0 12px;line-height:1.5}
"""

JS = """
const marks=[...document.querySelectorAll('mark')];
const cards=[...document.querySelectorAll('.f')];
function sync(){
 const off=new Set([...document.querySelectorAll('.leg input')]
   .filter(i=>!i.checked).map(i=>i.dataset.cid));
 marks.forEach(m=>m.classList.toggle('off',off.has(m.dataset.cid)));
 cards.forEach(c=>c.style.display=off.has(c.dataset.cid)?'none':'');
}
document.querySelectorAll('.leg input').forEach(i=>i.onchange=sync);
function focus(id){
 marks.forEach(m=>m.classList.remove('on'));
 const m=document.querySelector(`mark[data-id="${id}"]`);
 if(m){m.classList.add('on');
  m.scrollIntoView({block:'center',behavior:'smooth'});}
}
cards.forEach(c=>c.onclick=()=>focus(c.dataset.id));
marks.forEach(m=>m.onclick=()=>{
 const c=document.querySelector(`.f[data-id="${m.dataset.id}"]`);
 if(c){cards.forEach(x=>x.style.background='');
  c.style.background='rgba(120,120,120,.14)';
  c.scrollIntoView({block:'center',behavior:'smooth'});}
});
"""


def build(path, raw, findings, stats):
    # Resolve overlaps: keep the highest-confidence span at each point,
    # then longest. Nested marks would break the HTML.
    rank = {"high": 0, "med": 1, "low": 2}
    ordered = sorted(enumerate(findings),
                     key=lambda t: (t[1].start, rank[t[1].confidence],
                                    -(t[1].end - t[1].start)))
    kept, last = [], -1
    for i, f in ordered:
        if f.start < last:
            continue
        kept.append((i, f))
        last = f.end

    out, pos = [], 0
    for i, f in kept:
        out.append(html.escape(raw[pos:f.start]))
        out.append(
            f'<mark class="{f.confidence}" data-cid="{f.construction}" '
            f'data-id="{i}" title="{html.escape(f.construction)}: '
            f'{html.escape(f.note[:200])}">'
            f'{html.escape(raw[f.start:f.end])}</mark>')
        pos = f.end
    out.append(html.escape(raw[pos:]))

    counts, notes, confs = {}, {}, {}
    for f in findings:
        counts[f.construction] = counts.get(f.construction, 0) + 1
        notes.setdefault(f.construction, f.note)
        confs.setdefault(f.construction, f.confidence)

    leg = "".join(
        f'<label><input type="checkbox" checked data-cid="{c}">'
        f'<span class="sw" style="background:{CONF_COLOR[confs[c]]}"></span>'
        f'{c}<span class="n">{n}</span></label>'
        for c, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    cards = "".join(
        f'<div class="f" data-cid="{f.construction}" data-id="{i}">'
        f'<span class="ln">L{f.line}</span>'
        f'<span class="cid" style="color:{CONF_COLOR[f.confidence]}">'
        f'{f.construction}</span>'
        f'<div class="tx">{html.escape(f.text[:110])}</div></div>'
        for i, f in enumerate(findings))

    hidden = len(findings) - len(kept)
    hid = (f' &middot; {hidden} overlapping hidden' if hidden else '')

    return f"""<!doctype html><meta charset="utf-8">
<title>ticfinder &mdash; {html.escape(Path(path).name)}</title>
<style>{CSS}</style>
<header><h1>{html.escape(Path(path).name)}</h1>
<span class="meta">{stats['words']} words &middot; {stats['sentences']}
sentences &middot; {stats['findings']} findings &middot;
{stats['per_1000_words']} per 1k{hid}</span></header>
<div class="wrap"><div class="src">{''.join(out)}</div>
<div class="side"><div class="leg">{leg}</div>
<div class="note">Click a finding to jump to it. Uncheck a construction to
hide it. Everything here is legitimate English &mdash; the flag means look,
not delete.</div>{cards}</div></div>
<script>{JS}</script>"""

