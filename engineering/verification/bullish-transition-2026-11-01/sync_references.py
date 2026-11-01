"""Apply the approved PH3 transition delta and synchronize exact changed Source."""
from __future__ import annotations
import ast
from datetime import datetime
import hashlib
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "engine"

def index_block(relative, source):
    tree = ast.parse(source)
    lines = [f"#### `{relative}`", "- **Module-level symbols/assignments:**"]
    assignments = []
    for node in tree.body:
        if isinstance(node,(ast.Assign,ast.AnnAssign)):
            targets = node.targets if isinstance(node,ast.Assign) else [node.target]
            assignments.extend(f"`{ast.unparse(target)}` (L{node.lineno})" for target in targets)
    lines[-1] += " " + (", ".join(assignments) or "_none_")
    functions = [node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))]
    lines.append("- **Top-level functions:** " + (", ".join(f"`{node.name}({ast.unparse(node.args)})` (L{node.lineno})" for node in functions) or "_none_"))
    lines.append("- **Classes / schemas:**")
    for node in tree.body:
        if not isinstance(node,ast.ClassDef):
            continue
        lines.append(f"  - `{node.name}` (L{node.lineno})")
        fields = [f"`{ast.unparse(child.target)}: {ast.unparse(child.annotation)}`" for child in node.body if isinstance(child,ast.AnnAssign)]
        methods = [f"`{child.name}({ast.unparse(child.args)})` (L{child.lineno})" for child in node.body if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef))]
        lines.append("    - Fields: " + (", ".join(fields) or "_none_"))
        lines.append("    - Methods/properties: " + (", ".join(methods) or "_none_"))
    nested = []
    def visit(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
                name = prefix + child.name
                if prefix and not isinstance(node,ast.ClassDef) and isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    nested.append(f"`{name}` (L{child.lineno})")
                visit(child,name+".")
            else:
                visit(child,prefix)
    visit(tree)
    lines.append("- **Nested implementation functions/closures:** " + (", ".join(nested) or "_none_"))
    return "\n".join(lines)+"\n\n"

def update_teaching(section):
    if "#### PH continuation through PH3" in section:
        return section
    start = section.index("#### PH continuation and unlimited same-cycle numbering")
    end = section.index("#### PL-1, PL-2 and PL-3",start)
    section = section[:start]+"""#### PH continuation through PH3

After confirming PH-1 or PH-2, wait for the first strict `High > PH-n.price`. That main candle opens PH-(n+1). Use the earliest eligible accepted Order_A stop after that gate. The new PH price is the maximum High from the breakout main candle through the selected Order-stop main candle, including both whole candles; earliest equality owns the source. Source and exact later confirmation remain distinct.

The approved sequence stops at PH3. The former unlimited-PH rule is superseded. No PH4 is confirmed or registered as a native PH parent.

#### PH3 stop and bullish regime start

The first authoritative strict `High > confirmed PH3.price` across all independent cycle owners ends the entire bearish regime. Equality does not reverse. The exact selected lower-timeframe event orders this transition against all pending activations and decisions; reversal wins a joint boundary before a later bearish point can commit.

All bearish cycles stop at that transition. Their finalized prefix objects remain historical on the Chart, including stable physical identity and provenance. No later bearish calculation result or active continuation is exposed.

The bridge constructs independent calculation inputs: the bearish prefix ends before the crossing main candle; the bullish suffix includes that complete candle and all subsequent supplied candles. Earlier candles and previous detector/lifecycle/Order state cannot enter the new bullish calculation. Public indexes are translated back to the original supplied-input coordinates. A discovery event must be supported by a freshly calculated historical prefix. A transition beyond the requested presentation horizon cannot replace the current outputs.

Only the first bullish Reaction uses the explicit new-regime bootstrap. The first RED candle from the boundary is eligible without an earlier GREEN; its BoxTop uses the initial GREEN run and FirstRed, or FirstRed alone when the boundary is RED. Its BoxBottom evolves through exact confirmation without applying an earlier-leg/Reset boundary. The new leg-head Low remains available to native Blue calculation. After first confirmation, ordinary same-direction Reset, Blue, A, S, E, StopAll and physical Order rules resume. This does not authorize bullish PH/PL or a future bullish-to-bearish mirror.

""" + section[end:]
    section = section.replace("and 100-candle cap","and 400-candle cap")
    section = section.replace("for 100 subsequent analysis candles","for 400 subsequent analysis candles")
    old = "Without a strict break, display 100 subsequent analysis candles. The latest existing MBL may extend to a later actual break; an older MBL must not extend beyond 100 analysis candles when newer legs exist."
    new = "Display at most 400 subsequent actual analysis candles. An earlier strict break ends the line at that candle. The cap applies equally to the latest and all earlier MBLs; no later break extends a line beyond the cap. At a bearish-to-bullish handoff, historical drawing is bounded by the explicit calculation end."
    assert old in section
    section = section.replace(old,new)
    old = "Filled circles have radius `12px` (diameter `24px`), color `#ec407a`, opacity `100%`"
    new = "Bearish PL circles have default radius `4px` (diameter `8px`), color `#ec407a`, opacity `100%`; an unspecified bullish PH circle retains its existing `12px` fallback, and explicit radius customization remains supported"
    assert old in section
    section = section.replace(old,new)
    marker = "#### Bounded authoritative-RAW acceptance example"
    visual = """#### Bullish transition presentation

Draw a green dashed vertical line across the full plot height at the finalized bullish-start main candle, irrespective of that candle's market color. Render a clean green upward zigzag arrow at the actual 50th calculation candle counting the start as candle 1 (offset 49). The icon is 20 by 20 CSS pixels; its bottom edge is exactly 100 CSS pixels above that candle's High, horizontally centered on that candle. Pan/zoom changes anchors while preserving screen-pixel dimensions and clearance. If the 50th actual candle is absent, retain the boundary line and omit the icon.

The Engine supplies `trendTransitions` on the bullish direction with stable identity, source and exact event time, stopped PH3 provenance, and nullable target-candle time/High. The Chart does not search OHLC for a trend event. Historical paint, hit testing and selection all respect `calculationEndTime`.

The approved full-October USOIL 5s RAW calculated at 30s retains bearish PH1 at `2026-10-07 00:13:30`, PH2 at `03:55:30` and PH3 at `04:47:00`, with PH3 High `90.573`. Its strict stop starts the bullish context at `16:57:30`. FirstRed/BoxTop are `16:57:30`, BoxBottom is `16:59:30` and Break is `17:00:30`. The 50th candle is `17:22:00`. These are bounded acceptance anchors, never production special cases.

"""
    section = section.replace(marker,visual+marker)
    marker = "#### Bounded independent USOIL October 22 acceptance example"
    if marker in section:
        section = section.replace(marker,"""#### Historical later-cycle acceptance examples

The following examples predate the approved global PH3 reversal. They retain historical evidence of local-cycle/ownership behavior; later October cycles and PH4+ are not current full-month acceptance expectations once the October 7 PH3 stops.

#### Historical independent USOIL October 22 example""")
    section = section.replace("#### Bounded USOIL PH number-priority acceptance example","#### Historical USOIL PH number-priority example")
    return section

def main():
    changed = []
    for relative in subprocess.check_output(["git","diff","--name-only","--","engine/bridge","engine/pipeline"],cwd=ROOT,text=True).splitlines():
        if relative.endswith(".py"):
            changed.append(relative.removeprefix("engine/"))
    assert changed
    stamp = datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds")
    for reference in sorted((ENGINE/"algorithms").glob("*Source_Synchronized.md")):
        text = reference.read_text(encoding="utf-8")
        match = re.search(r"(<!-- PRIMARY-STRUCTURES-BEGIN -->\n)(.*?)(<!-- PRIMARY-STRUCTURES-END -->)",text,re.S)
        assert match
        text = text[:match.start(2)]+update_teaching(match[2])+text[match.end(2):]
        text = re.sub(r"(?m)^(\*\*(?:Last Modified|last_modified_at):\*\* `)[^`]+",lambda m:m[1]+stamp,text)
        text = text.replace("MBL display cap is 100 candles and its default label is 9px.","MBL display cap is 400 candles and its default label is 9px; the first strict PH3 stop starts an isolated bullish regime.")
        text = re.sub(r"(?m)^\*\*scope:\*\*.*$", "**scope:** `accepted directional specification and exact Source; bearish primary structures and bullish regime handoff`  ", text)
        text = re.sub(r"(?m)^\*\*Status:\*\*.*$", "**Status:** `ACTIVE SOURCE-SYNCHRONIZED LOCAL EXTENSION — PH3 trend reversal; UNRELEASED`  ", text)
        text = re.sub(r"(?m)^\*\*Production Source Behavioral Change:\*\*.*$", "**Production Source Behavioral Change:** `YES — approved PH3 reversal and first bullish Reaction bootstrap; bullish primary calculation deferred`  ", text)
        text = re.sub(r"(?m)^\*\*Mirror Contract:\*\*.*$", "**Mirror Contract:** Standard upstream geometry retains its directional mirror contract. The approved bullish regime-start bootstrap is an explicit one-direction exception. No bullish PH/PL or later reverse-transition mirror is inferred.", text)
        for relative in changed:
            raw = (ENGINE/relative).read_bytes()
            source = raw.decode("utf-8")
            digest = hashlib.sha256(raw).hexdigest()
            begin,end = f"<!-- EXACT-SOURCE-BEGIN:{relative} -->",f"<!-- EXACT-SOURCE-END:{relative} -->"
            left,right = text.index(begin),text.index(end)
            text = text[:left]+begin+"\n````python\n"+source+"````\n"+end+text[right+len(end):]
            position = text.index(begin)
            start = text.rfind("**SHA-256:**",0,position)
            text = text[:start]+f"**SHA-256:** `{digest}`  \n**Bytes:** `{len(raw)}`  \n**LF count:** `{raw.count(bytes([10]))}`\n\n"+text[position:]
            versions = dict(re.findall(r'(?m)^(\w+VERSION) = "([^"]+)"',source))
            api = next((v for k,v in versions.items() if "IMPLEMENTATION" not in k),"unversioned")
            implementation = next((v for k,v in versions.items() if "IMPLEMENTATION" in k),None)
            version = api+(f" (impl {implementation})" if implementation and implementation!=api else "")
            pattern = r"(\| `"+re.escape(relative)+r"` \| [^|]+ \| )`[^`]+` \| \d+ \| \d+ \| `[0-9a-f]+` \|"
            text,count = re.subn(pattern,lambda m:m[1]+f"`{version}` | {len(source.splitlines())} | {len(raw)} | `{digest}` |",text)
            assert count==1,(reference,relative,count)
            start = text.index(f"#### `{relative}`",text.index("### 13.5"))
            following = text.find("\n#### `",start+1)
            section_end = text.find("\n## ",start+1)
            finish = min(x for x in [following,section_end] if x>=0)
            text = text[:start]+index_block(relative,source)+text[finish+1:]
        reference.write_text(text,encoding="utf-8",newline="\n")
        print(reference.name,"updated",len(changed),"source owners")
if __name__=="__main__":
    main()

