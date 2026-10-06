"""Generate the requested twenty-section report from persisted audit evidence."""
from pathlib import Path
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
import json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def load(p):return json.loads((OUT/p).read_text(encoding='utf-8'))
def link(p,label=None):
    path=OUT/p
    target=path.as_posix()
    return f'[{label or p}]({"<"+target+">" if " " in target else target})'
def src(p,label=None):
    target=(ROOT/p).as_posix()
    return f'[{label or p}]({"<"+target+">" if " " in target else target})'
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+
                     ['| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows])
summary=load('audit-summary.json'); findings=load('findings.json'); raw=load('raw-registry.json')
confirmed=[f for f in findings if f['CONFIDENCE']=='CONFIRMED']
high=[f for f in findings if f['CONFIDENCE']=='HIGH-CONFIDENCE']
sections=[]
def section(n,title,body):sections.append(f'## {n}. {title}\n\n{body.strip()}\n')
def details(items):
    text=[]
    for f in items:
        text.append(f"### {f['BUG ID']} — {f['TITLE']}\n")
        for key,value in f.items():
            if key=='AFFECTED MODULE(S)':value='; '.join(src(p) for p in value)
            elif isinstance(value,list):value='; '.join(value)
            text.append(f'**{key}:** {value}\n')
    return '\n'.join(text)

section(1,'Executive Summary',f'''
**Audit result: eight confirmed defects in active calculation, CLI, index or provenance contracts; two additional LOW scoped helper/unsupported-API defects; three HIGH-CONFIDENCE candidates.** Five of the eight active-path findings are HIGH, three are MEDIUM. No CRITICAL finding is established at the demonstrated downstream scope. The ten confirmed items are deliberately separated by category; a reproduced helper discrepancy is not reported as a proven erroneous trade.

The strongest final-output evidence is **SE-01**: four unique final-visible E rows select the wrong eligible physical Order when strict stop events tie, two per direction. **RX-01** omits an eligible canonical Reaction; **BL-01** consumes post-confirmation prices through two strike paths and demonstrably changes Blue/A calculation provenance. **RX-02** attaches an exact Reset to the wrong main bucket on supported sparse input. **BR-01** crashes a parser-accepted optional-module configuration on real RAW. The other three active-contract defects concern restored Order indexing, converted S direction and exact numeric JSON ingress.

The supplied XAUUSD Order_B causal diagnosis is **not confirmed under Current Source**. The target Order exists and invalid S ownership windows persist, but restoring the omitted A to eligibility does not make it accepted: native accepted Red E ownership independently rejects it. This was tested individually and in batch over two complete datasets, both directions and all three observed feedback passes. Extended merged history also preserves the target physical Order and E anchor; that is output continuity, not a second full eligibility refutation.

All eight requested phases were performed. Twelve packaged Python files, **12,735 lines and 395 AST definition nodes**, were fully inspected collectively; both complete Reference prose documents were covered. Eleven relevant chart/server files, **1,865 lines and 200 function nodes**, were fully reviewed. Fifteen original RAW files contain **2,615,072 supplied rows** (overlap included), and all were executed at 30 seconds in both directions. The full matrix contains **42 successful two-direction calculations / 84 direction calculations** across originals, extra 5/60-second runs, repeats and finest-history unions. Selected invariant checks produce **504 PASS results and no recorded failure**; these checks are bounded and coexist with the confirmed defects.

Production Source, `engine.zip`, both References and original RAW were not changed. All **51 protected byte hashes** are unchanged; all twelve package/live Source files match; pre-existing Git status and HEAD are unchanged outside the owned audit directory. No fix, commit, deployment or new trading rule is included.

Scope limits remain explicit: live HTTP/server/browser execution was NOT RUN; no complete corrected-engine counterfactual was implemented; exact normative decisions for the specification conflicts remain unresolved. Exhaustive correctness over every possible market history is INCOMPLETE. A finite audit cannot honestly promise that every possible bug has been found.
''')

module_rows=[]
for m in summary['modules']:
    metadata=m['metadata']
    values=[v for k,v in metadata.items() if k.endswith('_VERSION') and 'IMPLEMENTATION' not in k]
    impl=[v for k,v in metadata.items() if 'IMPLEMENTATION_VERSION' in k]
    modified=[v for k,v in metadata.items() if 'LAST_MODIFIED' in k]
    module_rows.append([src('engine/'+m['path'].replace('\\','/')),', '.join(values) or 'unversioned',', '.join(impl) or 'same / absent',', '.join(modified) or 'absent',m['lines']])
raw_rows=[]
for idx,r in enumerate(raw):
    raw_rows.append([idx,src(str(Path(r['path']).relative_to(ROOT)).replace('\\','/'),Path(r['path']).name),r['nominalSeconds'],r['rows'],r['firstLocal'],r['lastLocal']])
section(2,'Project Snapshot',f'''
Snapshot began **2026-10-05** and completed **2026-10-06**, Asia/Tehran. Market examples use full local datetimes with `+03:30`. Artificial source probes are labeled and do not define production timestamps.

Authority follows the user's explicit rule: approved user/project instruction → Current packaged production Source → Current synchronized Reference prose → maintained docs → RAW facts → regression evidence → historical material → memory. `engine/engine.zip` is authoritative for this audit. Its SHA-256 is `{summary['engineZipSha256']}`. Extraction inventories **14 actual files: 12 Python files and 2 References**; directories and every archive member are in {link('package-inventory.json')}. All twelve actual Python files are byte-identical to their live counterparts. The preserved HEAD is `{summary['integrity']['gitDeltaOutsideOwnedAudit']['headBefore']}`; the original worktree/index includes pre-existing unresolved/deleted states.

{table(['Current module','Module version','Implementation version','Last-modified metadata','Lines'],module_rows)}

Current References are the packaged Bullish and Bearish **V5.4.24 Source_Synchronized** files, each 13,609 lines with 726 prose lines before embedded Source. Their exact paths/hashes are in {link('reference-inventory.json')}. Embedded-code verification requires a distinction: **only the empty root is byte-exact**. Eleven nonempty embeds use CRLF versus actual LF; all twelve existing embeds are newline-normalized and AST-equal. Each Reference embeds a thirteenth file, `bridge/__init__.py`, absent from current package/live Source. Exact byte-sync and complete manifest assertions therefore FAIL, while semantic alignment of the twelve existing embeds PASS. No alternate embedded module was executed.

Repository-root `TradingBot_AI_Operating_Protocol.md` and `AGENTS.md` were unavailable in filesystem/index searches. The user pasted AGENTS instructions and the global AGENTS file were available; missing authority was recorded rather than invented. Some root/chart owner README files are also absent. Existing references retain older ZIP inventory and historical test claims; the current unit result is **81 passed, 2 xfailed**, not the carried 91 claim.

Runtime: Windows / PowerShell, Python **{summary['python']}**, Node **24.19.0**, orjson **{summary['dependencies']['orjson']}**, pytest **{summary['dependencies']['pytest']}**, tzdata **{summary['dependencies']['tzdata']}**. Decimal decisions use normalized exact strings downstream; the numeric JSON parser exception is NUM-JSON-01. All audit Python executions use `-B`, and pytest caching is disabled. Current main timeframe is an explicit integer number of seconds; the matrix uses 5, 30 and 60 seconds. Normal engine paths, all behavior flags, both direction streams and Bridge Output are supplied in the main matrix. Exact CLI arguments are preserved per manifest.

**Every original RAW input is inventoried below.** Index identifiers in findings resolve to these immutable exact paths. Gaps are preserved; duplicates/decreasing timestamps and malformed OHLC were checked. Rows include overlap and should not be called unique market events.

{table(['Index','Immutable input','Nominal lower seconds','Rows','Actual first local','Actual last local'],raw_rows)}

{link('raw-registry.json')} records SHA-256, metadata, intervals, first/last rows and step distributions. One epoch-style 1-second filename understates its actual endpoint; actual rows reach 2026-09-15 23:19:44+03:30. Coverage is determined from rows, not filenames. The two XAU 1-second files overlap with an identical peer prefix. All same-granularity peer comparisons found zero conflicting rows.

Two additional audit-only derived inputs preserve original rows with explicit precedence/provenance: USOIL **458,231 rows**, XAUUSD **962,880 rows**, extending the available continuous history through October 3. XAU uses 1-second rows throughout their physical interval and 5-second rows outside it; no candle was invented and no original was rewritten. Their hashes/input list/method are in {link('finest-union-registry.json')}; each ran at30/60s in both directions. Cross-granularity compatibility is reported separately in section11.
''')

architecture=(OUT/'ARCHITECTURE.md').read_text(encoding='utf-8')
flow=architecture[architecture.index('```mermaid'):architecture.index('Authority gaps:')]
section(3,'Architecture / Dependency Map',f'''
{flow}

The bridge always constructs both canonical directional Reaction streams needed for physical opposite Order identity. Public/internal classification and presentation are later stages. Accepted lifecycle cause rebuilding and Order_B reset-leg feedback are semantic stages, not serializer corrections. Feedback permits at most eight identity-stable passes; both deeply observed RAW traces converged after three. Frozen dataclasses hold behavior geometry, while detector-owned maps/sets carry accepted causes, source/index and reset boundaries.

Ownership closure and every Python import/definition bound are in {link('source-map.json')}; {link('ARCHITECTURE.md')} is the pre-analysis map. The chart transport owns source selection, content/source fingerprinting and request execution; the Python engine owns trading state. Complete-source HTTP requests use original RAW; selected-range requests deliberately start a cold calculation from selected inclusive chart buckets under Reference L47. CLI display bounds are applied after complete supplied-input calculation.
''')

coverage_rows=[
['Engine Python','READ_FULL','All12 files;12,735 lines;395 AST class/function/closure nodes','Parent bridge/Order + Reaction/Blue/A + S/E + lifecycle partition'],
['Both current References','READ_FULL / VERIFIED_DUPLICATE','Both726-line prose spans; identical mirrored portions verified, every differing line reviewed','Embedded12 Source texts/ASTs verified, not a second rule authority'],
['Chart calculation boundary','READ_FULL','11files;1,865lines;200functionnodes','Complete Vite orchestration and directly relevant transport/cache/state callees'],
['Relevant engine tests','READ_FULL / executed','StopAll dominance; Order lifecycle contracts; HPZR reporter unit tests; RAW Order_B verifier','Existing expected failures preserved'],
['Relevant chart tests','READ_FULL / executed','Four boundary unit files fully read; all chart unit files executed','78passed; no live endpoint/browser certification'],
['Project files / manifests / historical anchors','INVENTORIED / targeted READ_FULL','Initial project-file inventory1176 entries; source/version metadata, package, current config and referenced regression evidence','Historical source copies under verification/archive are supporting evidence'],
['Frontend rendering, unrelated ingestion/release tools and all archives','INVENTORIED / NOT_READ outside semantic closure','Imports and paths routed; no claim of complete code review for unrelated UI/release modules','No effect inferred without a current engine dependency'],
]
matrix_rows=[[k,v['runs'],v['timeframes'],str(v['executionCounts']),v['totalWallSeconds']] for k,v in summary['matrices'].items()]
coverage={'study':coverage_rows,'rawMatrix':summary['matrices'],'sourceDefinitionIndex':'source-map.json',
          'ownerCoverage':['reaction-audit/coverage.json','s-e-audit/coverage.json','lifecycle-audit/REPORT.md','boundary-audit/coverage.json'],
          'limits':['No live HTTP/browser run','No complete corrected-engine counterfactual','Archives and unrelated application modules not all READ_FULL','Universal market correctness INCOMPLETE']}
(OUT/'coverage-ledger.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
section(4,'Audit Coverage',f'''
Study statuses and verification statuses are different claims. `READ_FULL` means complete inspection, `VERIFIED_DUPLICATE` means identical already-read text, `INVENTORIED` means listed/routed, and `NOT_READ` means no complete inspection. Execution uses only PASS / FAIL / NOT RUN / INCOMPLETE.

{table(['Area','Study coverage','Concrete scope','Limit / owner'],coverage_rows)}

{table(['Recorded matrix','Two-direction runs','Main seconds','Execution counts','Observed total wall seconds'],matrix_rows)}

The thirty base matrix calculations comprise15 original30s +8 original60s +3 original5s +4 merged30/60s. Twelve additional calculations are three repetitions on each of four30s inputs, giving eight comparisons against a prior run. All stable fields, including dictionary/list order, Decimal strings, visibility, event/source times and provenance, were retained; only top-level observational `timings` was removed. Stable bytes and parsed objects both compare equal.

Deep lifecycle observation used complete idx8 andidx14 RAW, both directions and all observed feedback passes, plus a separate same-output E tie trace onidx8. The hooks call original functions and return original objects unchanged. Traced stable outputs equal the uninstrumented payloads. Hooks existed only in isolated diagnostic processes and were removed when those processes ended; production files were never instrumented. Standalone diagnostic scripts/evidence remain for reproducibility.

Tests: engine units **81passed,2xfailed**; chart units **78passed**; forced expected-failure run **2failed,37deselected**; package-authoritative focused contracts **79passed,2xfailed**. Reaction differential checks include2,000 lower-index assertions and1,500 valid synthetic reflected histories/3,000 directional Reaction→Blue→A executions. Whole-runtime reflection checks **16 PASS** stage/direction comparisons on a1,200-main/7,200-lower synthetic history, deliberately without Dojis. Projection probes cover exact event/equality/horizon/source identity and immutability; boundary probes cover500 sparse inputs/2,500 range assertions and queue/cache/source guard behavior.

All filenames and commands are preserved in {link('coverage-ledger.json')}, manifests and logs. Full algorithm correctness, every possible post-fix downstream consequence, live HTTP/browser execution and historical before/after Source differential are not claimed. The requested audit phases are complete as performed work; these evidence limits remain INCOMPLETE or NOT RUN in section20.
''')

section(5,'Confirmed Bugs',f'''
Confirmed means the stated incorrect behavior was reproduced and the owning divergence established. Severity applies to that demonstrated scope. The first eight findings are active calculation, CLI, index or provenance defects; the final two LOW findings are explicitly narrower engineering/API defects. Synthetic cases prove general supported input transitions but do not establish real-market prevalence. Every requested bug field is below; machine-readable equivalent: {link('findings.json')}.

{table(['ID','Severity','Category','Strongest demonstrated scope'],[[f['BUG ID'],f['SEVERITY'],f['CATEGORY'],f['TITLE']] for f in confirmed])}

{details(confirmed)}
''')
section(6,'High-Confidence Defects',f'''
These are not included in the confirmed market/calculation defect count. Source-level helper outcomes are reproducible, but full accepted-output reachability or decisive normative semantics remain unresolved. They must pass that further gate before a behavioral fix is approved.

{details(high)}
''')

section(7,'Suspected Issues Requiring More Evidence',f'''
{table(['ID / risk','Current evidence','Why not confirmed','Required next evidence'],[
['SE-04 stale initial S ownership','Initial detector/windows reused after invalid-S reconciliation; explicit-invalid owner windows remain','All revived A stay independently rejected on2 complete RAWs,2directions,3passes each','A restored by exact owner invalidation must also pass accepted lifecycle and change an accepted output'],
['LC-05 older surviving dominant E lost by S visibility','Latest-source pruning1089-1108 differs from consumed continuation910-948; mirrored helper changes with newer lower E','No accepted RAW S final counterexample; independent owner survival interpretation unresolved','Native same-owner lineage and RAW final visibility with older higher owner alive past newer decision'],
['S overlapping-window iteration order','S640-679 early False differs if supplied overlapping windows are permuted','Native append order is deterministic; arbitrary permutation does not prove supported state','Naturally reachable overlaps with independently defined ownership result'],
['Broader E equal-stop candidates','52 rows across21 saved calculations have later final-ledger identities sharing stop','Final membership alone does not prove same native route eligibility; separate from four SE-01 confirmed rows','Same-argument native query trace and final physical join'],
])}

No incomplete-cache-key or direction-specific comparator bug was demonstrated outside the recorded defects. A theoretical hazard or unused optimization was not upgraded merely because it looks suspicious. Detailed excluded/refuted hypotheses appear in the subsystem reports. The original stale-S diagnosis remains a suspected structural class with demonstrated current-anchor causal refutation, not a confirmed wrong Order_B.
''')

section(8,'Source ↔ Algorithm Reference Mismatches',f'''
Current Source is the executable higher authority under the user's order. A prose mismatch alone does not authorize a fix. Findings RX-01/BL-01/RX-02/SE-01 also have contradictory shared Source contracts/comparators or inconsistent native state, and independently reproduced transitions. The ambiguous cases below remain SPECIFICATION CONFLICT.

{table(['Rule','Documented / Source locations','Verdict','Impact / authority disposition'],[
['Decimal / GREEN Doji / strict equality','ReferencesglobalL53-58;core_utils;DirectionPolicy','Implemented downstream; ingress NUM-JSON-01','Price lexeme loss is before correct Decimal decisions'],
['Initial/normal Reaction reuse','§4.4L80;Reaction2148-2195 vs2308/2349/2387','Mismatch RX-01','Initial branch omits shared confirmed-state transition'],
['Reset owning main/timeframe','§4.6L88;Reaction121-124/278-283','Mismatch RX-02','Sparse occupancy is accepted transport, not timeframe metadata'],
['Blue Break strike cap','§5.2L106/row617;Blue103-188','Mismatch BL-01','Two paths use post-confirmation evidence'],
['A confirmed source cap / inherited Blue rules','§6.1-6.5;A167-199,322-758','Implemented at reviewed closure','Bounded mirror and RAW geometry evidence; not universal proof'],
['S post-A-stop versus source-start shared Order','§7.1L144 vs§7.6L177;S1376-1381','SPECIFICATION CONFLICT SE-03','Type3 frozen source can predate Astop; reconciliation can move decision before Astop. Both synthetic directions. Decide whether retrospective Order stop is permitted'],
['S adopted opposite Order direction','§7.6/schema§13.2/mirrorrow558;S1393-1417','Mismatch SE-02','Order geometry adopted without its direction'],
['E exact-stop consumption tie','§8.2L187/row620;E391-418;Order830-856','Mismatch SE-01','Creation ordering is distinct from consumption ordering'],
['Order canonical identity / strict first crossing','§9/§10/§11;Reaction registry/Order/B verifier','Implemented in tested outputs','RAW checks do not independently prove every anchor eligibility rule'],
['Complete historical A causes versus invalid creation rights','§11.5 vs§11.6;LC509-514;Order1779-1806/1472-1483','SPECIFICATION CONFLICT LC-02','Accepted primary source is filtered but rejected A cause can re-enter E rebuild. Decide accepted historical cause versus calculation-rejected cause; no final-market corruption established'],
['Order_B next-A expiry formation time','§10.5;Order403 trigger_event_time versus later Reaction confirmation','SPECIFICATION CONFLICT / terminology ambiguity','Does next A formation mean trigger or confirmed creation? Material eligibility endpoint; no wrong final RAW demonstrated'],
['Exact StopAll owner/count/direct-parent exception','§12.1-12.5;LC29-39/323-475','Implemented in reviewed tests and anchors','S/E family/number ownership and retrospective direct-parent guard controls pass'],
['Newest stopped A boundary','§12.6L303;LC714-725 vs1266-1284','Partial; HIGH-CONFIDENCE LC-04','Final visibility comparator lacks stop recency; market output unproven'],
['Invalid live head veto','SourceLC821-823;generic§11/12.6','Partial; HIGH-CONFIDENCE LC-03','Unstopped prefix omitted; normative interval needs confirmation'],
['Geometry earliest exact confirmation','SourceReaction1917-24;§9.1L211','HIGH-CONFIDENCE RX-H01','Canonical membership may prevent accepted Order effect'],
['Full calculation / selected cold range / display','L47/49/60/§13;Bridge/transport','Implemented in reviewed closure','Complete original path, selected buckets and CLI presentation have distinct authority'],
['Exact-source reconstruction / manifest','§1/§14/§16;reference-byte-analysis.json','FAIL strict bytes/manifest;PASS normalized12existing','Line-ending drift and absent13th bridge initializer; no semantic difference among existing12'],
])}

For LC-02, both-direction native rebuild probes prove the rejected cause is restored: accepted primary A source00:00:00 and excluded A source00:00:30 coexist in the complete cause set, and the latter becomes a parent-stop creation cause at00:01:05. Section11.5 could mean presentation history; section11.6 removes invalid parents' creation rights. Without an explicit accepted-versus-rejected distinction, neither a general prune nor general retention fix is justified.

For SE-03, the independent chronology probe has S source00:00:00, Astop00:00:35, originaldecision00:01:50, recorded physical Orderstop00:00:15. Shared reconciliation accepts15 from source-start and therefore predates35. Section7.6 explicitly states the implemented predicate while7.1 requires the A gate. This is an unresolved rule conflict rather than permission to add a comparator.

Rule-by-rule detailed enforcement tables cover remaining recursive E, reset, equality, priority, historical retention, projection and provenance clauses in {link('reaction-audit/REPORT.md')}, {link('s-e-audit/REPORT.md')}, {link('lifecycle-audit/REPORT.md')} and {link('lifecycle-audit/BRIDGE_REPORT.md')}. Historical 5.4.23/earlier differential claims were not silently relabeled as fresh tests.
''')

section(9,'Bullish ↔ Bearish Mirror Problems',f'''
**No standalone one-direction-only production defect was established.** Confirmed directional findings reproduce both sides; exact mirroring alone can preserve the same wrong rule.

{table(['Primitive / object','Mirror enforcement reviewed','Verification'],[
['Prices / extremes / crossings','Low↔High;min↔max;<↔>;exact Decimal reflection;strict equality retained','2,000 lower-index differential checks and directional focused boundaries PASS'],
['Reaction/Reset/Blue/A','Directional First role and source extrema; physical indexes/time invariant','1,500 valid no-Doji histories;3,000 directional prefix-stage executions PASS'],
['S/E/Order/StopAll','Opposite physical direction; geometry reflected; family/priority/count/identity invariant','Full runtime1200main/7200lower history:16 stage/direction comparisons PASS'],
['Provenance / visibility / ordering','Do not mirror IDs, cause meaning, priority, source time, sorting or numbering','Paired source probes and RAW both-direction matrices; SE-01 confirmed2finalrows per direction'],
['Doji','Public candle color remainsGREEN in both market directions','Reviewed Source/Reference invariant; no-Doji fuzz deliberately does not prove all Doji candidate behavior'],
])}

Reflection uses a constant-minus-price transformation only in synthetic diagnostic input, with high/low swapped; this is not a production rule or RAW rewrite. Candidate core reflection occurs before public cross-direction metadata is attached; arbitrary calls with populated metadata are not evidence of a live mirror bug. The16 runtime checks retain stable invariant fields and normalize reflected price values as Decimal; repeated raw stable-byte comparisons separately prove representation/order determinism on tested inputs. Broader Doji-inclusive full-runtime reflection and every edge history remain INCOMPLETE.
''')

section(10,'Lifecycle / State Integrity Findings',f'''
The complete lifecycle state path was audited: exact-owner repeated S/E count, armed state, strict stop, donor selection, hard reset, accepted cause rebuild, Order_B feedback, visibility and lineage restoration. The current StopAll owner counts exact family/number, replaces only according to priority, uses latest repeated strict level, and allows retrospective source only through an exact direct-parent provenance guard. Wrong parent/stop, unarmed count1, unrelated early donor and equality controls pass in both directions.

Confirmed state defects are **OA-INDEX-01** (ledger/index divergence) and **SE-02** (incomplete provenance replacement). **SE-01** is a physical consumption selection defect before E construction. **BR-01** changes lifecycle configuration between feedback and finalization. LC-03/04 are HIGH-CONFIDENCE interval/comparator candidates; LC-02/SE-03 remain specification conflicts.

**Supplied anchor independent reconstruction, Asia/Tehran:** on complete idx8, all-A has Bullish A source2026-09-29 20:15:30, price4144.795, trigger20:09:00, ReactionBreak20:18:00; RAW source extreme occurs20:15:50. Initial Advanced S owns20:14:00..20:26:40.000001 and is later explicitly invalid. Releasing only that invalid ownership makes the A eligible for the next stage, which is the first restored eligibility state. Native accepted-owner splitting then rejects it independently: accepted Red E2 source18:59:00/price4148.43/decision19:17:15 first strictly stops20:14:35, newer than Blue E1 source19:51:30 stop20:14:00. The A lies strictly beyond the Red boundary and is a closed-leg head; no interior exception applies.

The target physical Order First is20:32:00 and confirms20:33:00; its accepted reset-leg provenance uses Eanchor19:51:30, ResetReactionFirst20:20:30, Reset20:22:45, LL4144.795 sourced20:15:30 and firststrictbreak20:26:40. LL can be a market extreme at a calculation-invalid A source without asserting that A is an eligible behavior anchor. Therefore stale windows do not establish a wrong Order_B here.

{table(['Complete RAW / direction','Observed passes','Explicit-invalid windows removed per pass','A revived per pass','Newly accepted A individual / batch'],[
['idx8 XAUUSD Bullish',3,35,13,'0 / 0'],['idx8 XAUUSD Bearish',3,29,6,'0 / 0'],
['idx14 USOIL Bullish',3,46,17,'0 / 0'],['idx14 USOIL Bearish',3,49,16,'0 / 0'],
])}

Each experiment first reproduces original eligibility exactly, removes only explicit-invalid owner windows, then tests both one revived A at a time and all revived A together through the unmodified split. Anonymous window ordering or public-hidden state alone is not sufficient invalidity evidence. The refined diagnosis neither confirms the supplied historical causal claim nor proves that an older revision never had it.

{link('s-e-audit/general-ownership-results.json')} and {link('s-e-audit/trace-analysis.json')} contain this refutation. {link('regression-anchor-outputs.json')} shows extended XAU history beginningAugust25 still has the same physical20:32 Order/E19:51:30 anchor/LL/Reset/strictbreak, with different global indexes/Reaction number/postStopAll context. Full merged-history eligibility instrumentation was not separately repeated; the exact causal release proof applies to the two complete traced inputs above.
''')

decimal=load('raw-decimal-validation.json') if (OUT/'raw-decimal-validation.json').exists() else None
decimal_note='Exact Decimal RAW validation is INCOMPLETE pending its final evidence file.'
compat_table=''
if decimal:
    dc=Counter(i['exactOHLC'] for i in decimal['exactValidation']); lc=Counter(i['numericLexemeValuesPreserved'] for i in decimal['exactValidation'])
    decimal_note=f'Exact Decimal OHLC checks: {dict(dc)}; numeric lexeme value preservation against the production parser: {dict(lc)}. This checks original files, not the synthetic NUM-JSON-01 edge.'
    compat_table=table(['XAU 5s RAW index','Complete5s buckets compared to all five1s rows','Different OHLC buckets'],[[r['rawIndex'],r['completeFiveSecondBucketsCompared'],r['differentOHLCBuckets']] for r in decimal['oneSecondVersusFiveSecond']])
    unique={e['time']:e for row in decimal['oneSecondVersusFiveSecond'] for e in row['examples']}
    differences=[]
    for time,e in sorted(unique.items()):
        fields=[k for k in e['oneSecondAggregate'] if e['oneSecondAggregate'][k]!=e['fiveSecondRAW'][k]]
        differences.append([datetime.fromtimestamp(time,ZoneInfo('Asia/Tehran')).isoformat(sep=' '),
                            ', '.join(fields),'; '.join(k+'='+e['oneSecondAggregate'][k] for k in fields),
                            '; '.join(k+'='+e['fiveSecondRAW'][k] for k in fields)])
    compat_table+='\n\nThere are **three unique mismatching buckets**, repeated in both overlapping 5-second files (idx4/5); these are RAW cross-granularity discrepancies, not malformed OHLC or a Source defect. The requested finer-input precedence resolves their audit chronology.\n\n'+table(['Full local5s bucket','Field','1s aggregate value','5s supplied value'],differences)
section(11,'Chronology / RAW Findings',f'''
**Finest chronology was used for primary exact-event interpretation wherever available.** Original1s files were executed directly; merged XAU history uses1s precedence throughout its coverage. Standalone overlapping5s runs are input-specific stress/regression evidence and are not called the finest global proof for those periods. The confirmed market RX/Blue/Order-tie examples onSeptember16/29 have5s as the finest supplied coverage. The1683-row30s input is coarse smoke evidence only; exact intrabar claims use overlapping finer data.

Fifteen original files have zero duplicate/decreasing timestamps, finite consistent OHLC in the checked representation, with real gaps preserved. Same-timeframe overlaps: USOIL5s642,635 equal peer rows; XAU1s161,376 equal; XAU5s255,154 equal; zero conflicting peer rows. {decimal_note}

**Cross-granularity compatibility:** aggregate comparison is restricted to complete5s intervals having all five exact1s rows. This is distinct from equal-row peer comparison. A difference, if present, is recorded rather than repaired; the user's finer chronology precedence does not authorize inventing missing1s candles or rewriting coarser inputs.

{compat_table}

Full evidence is {link('raw-decimal-validation.json')} and {link('raw-overlap-results.json')}. The merged inputs omit coarse30s in periods covered by finer streams, preserve market gaps and carry all original row values. Their source hashes and actual boundaries are retained. Different providers/representations are never silently labeled peer-equivalent solely because the symbol text matches; compatibility is directly checked.

RX-02 is a correct exact lower event with an incorrect main owner due inferred duration. BL-01 is an incorrect permitted lower interval. RX-H01 is a local exact-event comparator risk. LC-01 is a next-versus-containing index mismatch. Strict source extrema in final E were independently checked using complete boundary main candles, as the active rule requires; retrospective E source does not by itself imply future leakage when its decision and exact parent-stop provenance are valid.

Current StopAll regression outputs preserve Bearish USOIL2026-09-25 08:51:00 with stoppedBehaviorKey S red/count2/gate08:51:00 and sourceprice93.194, and2026-10-02 20:20:00 with E1red/count2/gate19:57:05. They appear in both idx14 and the longerAugust21 merged30s output. These are fresh bounded anchor confirmations; a new5.4.23-versus5.4.24 full differential was NOT RUN.
''')

section(12,'Decimal / Equality / Crossing Findings',f'''
The strict direction primitive is Bullish Low<level / Bearish High>level; equality stays eligible and never creates a strict penetration. Reaction confirmation uses the appropriate opposite edge. Reviewed lower segment queries return first strict crossing and first equal extreme source deterministically. Core source uses Decimal for normalized decisions; negation/mirror preserves exact values rather than context-rounding them.

NUM-JSON-01 is specifically **before** normalization. Exact lexemes Open100.0000000000000002 and Close100.0000000000000001 collapse to equal float100.0. A valid RED becomesGREEN before Reaction sees it. Correct Doji logic and Decimal serialization cannot recover that distinction. The string-price control retainsRED; current-market lexeme checks are reported insection11, avoiding an unsupported claim that every supplied market file is contaminated.

RAW verification independently checks physical Order recorded stops against the opposite-price strict predicate and its earliest occurrence after exact confirmation; checks exact E decision=max(parentstop,Orderstop), complete-boundary Esource earliest extreme, decimal string fields and published Order_B LL/strict-break/confirmation chronology. The twelve recorded check names per case are in {link('raw-invariants.json')}. The diagnostic key `validCreatingCause` checks that a cause set is nonempty; it does **not** independently certify every cause owner's validity. The Order_B provenance checker verifies published LL/first-cross/confirmation fields, not every anchor eligibility rule. The2,000 lower-index differential tests include equality and earliest extreme ties. A PASS on these selected invariants does not verify RXinitial reuse, Blue strike cutoff or E consumption tie selection, which have separate failing evidence.

Unresolved SE-03 chronology and LC-02 cause semantics do not become numerical fixes. Equality is not a substitute for missing authority.
''')

section(13,'Determinism / Cache / Recalculation Findings',f'''
**All eight repeat comparisons PASS** for both parsed objects and full stable bytes, across four30s originals repeated three times. Only top-leveltimings was removed. Decisions, prices/Decimal strings, indexes, source/event times, selected parents, cause ordering, status, visibility and serialized order remain in the equality check. Direction-only controls equal the corresponding both-direction output; optional projection leaves legacy arrays equal. These prove tested fresh-process determinism, not every long-lived embedded reuse scenario.

Run-scoped confirmation/reset/physical gate keys include relevant direction, main/identity/bounds/geometry and exact event state at reviewed call sites. Canonical audit revision and sequence reset publication invalidate carried/context queries; existing same-size ledger cause-change and reset-map contracts pass. **OA-INDEX-01** is a missing index population operation, not a demonstrated incomplete key. Provisional S windows persist across feedback and remain suspected until accepted output differs.

Process-global _SEQUENCE_TIME_INDEXES, _REFLECTED_VIEWS and _LOWER_TIMEFRAME_INDEXES hold strong input references without eviction. Source identity checks protect against id reuse. Current CLI exits after each request, so no wrong-input cache hit was established; an embedded long-lived host could retain many datasets. _geometry_after_reset_cache is read but never populated: ineffective optimization, not a confirmed trading bug.

Chart durable results key current Source fingerprint, RAW content/hash, timeframe, range, direction and flags. Queue duplicate jobs share a promise; shutdown/abort handling and progress observer isolation pass isolated probes. Scratch source/hash changes invalidate results. Historical /api/info report browsing does not claim a fresh current trading calculation. No additional stale chart cache bug was demonstrated; live endpoint/child interaction remains NOT RUN.
''')

section(14,'Serialization / Visibility Findings',f'''
Final legacy selections and optional Bridge Output use the same finalized object lists; full internal ledgers supply historical metadata and identity, not replacement behavior selection. Projection verifies a recorded exact strict event and returnsnull if unproved, outside horizon or ambiguous. It does not scan to an alternate later price crossing to make an event pass. Physical Order uses(FirstIndex,BreakIndex), exact parent causes use type/family/source/event, and same-index wrong-time parent lookup is rejected. Bounded semantic objects/ledgers remain immutable after projection.

**SE-02** projects a null physical direction because S reconciliation omitted it upstream; a serializer patch would hide the owner defect. **LC-01** is confirmed only against a helper docstring, with real occurrences masked by independent invalidA. **LC-04** is a HIGH-CONFIDENCE duplicated boundary comparator. **LC-05** is suspected loss of older surviving owner context. **BR-01** diverges before projection and crashes at final consistency validation.

One requested presentation-range configuration compares full calculated objects with a one-hour inset and passes exact source-time selection. Selected-range HTTP input intentionally starts from its own selected supplied rows under the current explicit Reference contract; it is not assumed equivalent to complete-history calculation. Historical context needed for full calculation is retained by the complete-source route and the extended matrices.

Projection comments saying no new parent-stop search overstate the implementation: pure authoritative cached/segment queries may occur to retrieve already-defined chronology. They do not change event selection or trading state in the reviewed closure. No wrong-output defect was proved from that wording. Source metadata/caches are distinct from semantic input mutation.
''')

section(15,'Regression Coverage Gaps',f'''
Existing PASS suites did not discover the new RX/Blue/sparse/E tie/configuration/converted-S/numeric ingress failures. HPZR unit tests test the regression reporter's first-diff formatting, not the full trading algorithm. Two strict expected failures already pin restored Order indexing; default green unit exit does not make them repaired.

{table(['Gap','Current evidence','Required extension'],[
['Transition coverage','Initial confirmation differs from later transitions; two Break strike paths bypass cutoff','Contract tests over every state-machine entry route, earliest divergence before output'],
['Physical selection boundaries','E consumption tie differs from creation ranking; same event/different First fixtures absent','Native eligible-pool assertions and exact final E Order/provenance'],
['Context ingress / configuration','Sparse accepted transport and optional lifecycle default not coherently exercised','Explicit timeframe propagation; effective configuration parity through feedback/final'],
['Coupled state / complete replacement','Expected-failed ledger index and converted S direction omissions','Ledger/index equivalence and complete physical Order adoption fields'],
['Semantic/runtime limits','Unresolved live interval/cause/formation meanings; no live app test or corrected full-engine oracle','Resolve authority, then parent-chain market repros and live endpoint smoke'],
])}

No production test or fixture was altered. Standalone diagnostic probes document failures and controls under the owned audit directory; they are not yet approved permanent regression additions. The user requested audit first, so tests that presume a new semantic rule are described, not installed into the production suite.
''')

section(16,'Performance / Architecture Risks',f'''
Observed wall times are evidence of this environment, not controlled performance benchmarks. All15 original30s runs took829.17seconds total; the largest original USOIL452,814-row input took335.74seconds. Four merged30/60s runs took577.50seconds total; mergedUSOIL30s took267.28seconds. Different history shapes and recursive object counts preclude deriving a speedup from row count alone. No profiler, memory soak or before/after optimized benchmark was run.

Independent resource/architecture risks are strong-reference process caches without eviction in embedded use; repeated cause/index rebuilding across feedback; duplicated lifecycle/visibility comparators; mutable anonymous S ownership windows; near-identical physical Order adoption paths; broad bridge orchestration/projection ownership in2957lines; version versus implementation-version metadata drift. These are maintenance/performance concerns except where specific reproductions establish correctness defects above.

Feedback convergence is based on accepted reset-leg identity, with an eight-pass cap; observed histories converged. Equality of that set alone is not a formal proof that every other semantic field has reached a fixed point. No native nonconvergence or order-changing cache effect was demonstrated. Production latency expectations were not available in owner docs, so the observed time is not classified a performance SLA bug.
''')

section(17,'Root-Cause Summary',f'''
{table(['Underlying class','Findings','Earliest owner','General consequence'],[
['Incomplete state transition / duplicated adoption','RX-01;SE-02','Reaction initial branch;S reconciliation','Missing canonical continuation or physical provenance field'],
['Incorrect time boundary / context metadata','BL-01 two paths;RX-02;LC-01 scoped','Blue strike owner;Reaction timeframe;visibility index','Post-confirmation evidence or incorrect containing bucket'],
['Comparator reused at wrong semantic stage','SE-01;LC-04/RX-H01 candidates','Physical consumption/E reduction;final visibility;bounded geometry','Required eligible candidate can be discarded before final comparator'],
['Coupled state/configuration updated incompletely','OA-INDEX-01;BR-01;LC-03 candidate','Order ledger/index restoration;effective bridge config;open interval','Missing query result or feedback/final divergence'],
['Authority / representation drift','NUM-JSON-01;API-LEGACY-01;Reference drift/spec conflicts','Ingress decoder;legacy API;owner docs','Exact information lost, import failure or unresolved intended behavior'],
])}

State correctness is not repaired by hiding a JSON row. Source-versus-Reference synchronization, RAW quality, test strength and performance are separate categories. No independent algorithm design flaw is definitively approved here: the normative ambiguities remain specification conflicts, while reproduced inconsistent owner transitions are Source implementation findings.
''')

section(18,'Recommended Fix Order',f'''
**Recommendation only; no fix has been implemented or authorized by this report.** Fix approval must follow review of this completed audit, as the user instructed.

1. Correct **SE-01** at physical E consumption adjudication, preserving creation order separately; repair **OA-INDEX-01** through atomic canonical ledger/index registration. These have final E evidence or explicit failed contracts.
2. Correct **BL-01**, **RX-01** and **RX-02** in their owning state/time-window layers; protect exact confirmation and explicit timeframe throughout all entry paths. Compare first divergence across full stages, not just final counts.
3. Correct **BR-01** after choosing/documenting one effective optional lifecycle default. Carry the same effective state through feedback and finalization; retain the consistency assertion.
4. Correct **SE-02** through complete physical Order adoption; choose exact ingress representation for **NUM-JSON-01** and validate the input contract before changing decoders.
5. Resolve **LC-02/SE-03/Order_B formation** conflicts and validate **LC-03/LC-04/RX-H01/LC-05** with accepted market chains before behavioral changes. Handle **LC-01/API-LEGACY-01** as scoped follow-up debt once public contract is settled.

General correction rules must be independent of symbol, timestamp, price fingerprint, filename, fixture or generated output. Rejected versus historical accepted causes must be distinguished explicitly; generic pruning of all hidden owners would invent a rule. A later fix phase must preserve the dirty worktree and make changes reviewable in isolated owned paths.
''')

section(19,'Regression Plan for Later Fix Phase',f'''
1. Pin this unchanged ZIP/Source hash and immutable RAW registry as the baseline. Add each approved defect's both-direction minimal contract plus its controls; require earliest state divergence, complete identity/provenance and correct strict-equality behavior.
2. For each correction, execute the relevant parent/dependency closure from RAW through canonical Reaction/Blue/A/S/E/lifecycle/Order. Compare stage-by-stage against the pinned baseline; classify every changed field and first divergence, including internal calculation objects consumed downstream.
3. Run all15 original30s inputs and both finest merged histories at30/60s; preserve finest lower chronology and full preceding history. Repeat targeted5s inputs. Add naturally reachable cases for unsettled lifecycle intervals/cause semantics only after authority decisions are explicit.
4. Run exact byte/object determinism and full structural/runtime mirror comparisons including Doji/edge controls, restored indexes, direction switches, timeframe changes, reset/StopAll and configuration toggles. Require expected-failed contracts to pass normally after their approved fix.
5. Exercise the live production HTTP/pipe/Python path and presentation ranges with unchanged original RAW. Retain precise matrix statuses, final hash/Git preservation, current synchronized Reference bytes/manifests and no unintended trade/visibility differences before considering deployment.

The supplied XAU anchor must remain a causal regression test: check actual accepted A eligibility under current dominant owner before declaring its20:32 Order invalid. A test that merely asserts the historical proposed conclusion would encode an unverified rule. Existing USOIL exact-owner/direct-parent anchors must preserve count, owner key, gate event and donor identity.
''')

checks=[
['Authoritative ZIP extraction/inventory','PASS','14actualfiles;12Python+2References;everymember inventoried'],
['Package/live Current Source equality','PASS','All12byteequal;full metadata and AST index'],
['Complete Current engine semantic source reading','PASS','12,735lines/395definitionnodes across12files, owner partition'],
['Relevant chart calculation boundary reading','PASS','11files/1,865lines/200functionnodes'],
['Both complete Reference prose coverage','PASS','726prose lines each;mirroredduplicatesverified'],
['Reference strict byte sync/full manifest assertion','FAIL','11nonemptyCRLF-vsLF;missing13thbridge initializer'],
['Existing12 Reference embeds normalized text/AST','PASS','No semantic code difference after newline normalization'],
['Requested missing project protocol/rootAGENTS','INCOMPLETE','Files unavailable;user/global rules applied;no invented authority'],
['All original RAW chronology/OHLC','PASS','15inputs;2,615,072suppliedrows;no duplicate/decreasing times;exact checksection11'],
['Same-granularity RAW overlaps','PASS','Zero conflicting peer rows;exact source registry'],
['Cross-granularity RAW OHLC equality','FAIL','Three unique5s buckets differ from complete1s aggregates;finer precedence used, originals preserved'],
['Original30s both-directions execution','PASS','15 successful CLI calculations; normal explicit module paths'],
['Additional60s/5s originals','PASS','8 at60s; 3 at5s; both directions'],
['Full finest merged histories','PASS','2 derived inputs at30/60s; 4 CLI calculations; both directions'],
['Selected RAW invariants','PASS','42 cases / 504 checks; no failures; specified scope only'],
['Fresh-process stable deterministic output','PASS','8 byte+object comparisons across4 inputs ×3 runs; only timings removed'],
['Whole-runtime reflected stage outputs','PASS','16 stage/direction checks; 1,200 main /7,200 lower; no-Doji synthetic history'],
['Focused lower-index/synthetic mirror checks','PASS','2,000 differential checks; 1,500 histories /3,000 prefix-stage executions'],
['CLI individual direction/projection/range controls','PASS','Individual direction equals both output; legacy unchanged; inset source objects match'],
['Optional lifecycle omission configuration','FAIL','Valid idx6 command exits1; BR-01'],
['Engine ordinary unit suite','PASS','81 passed,2 xfailed; expected failures are not counted as correct behavior'],
['Restored Order desired index contract','FAIL','2 failed under --runxfail; 37 deselected; OA-INDEX-01'],
['Unsupported legacy pipeline import','FAIL','Isolated package import raises missing run_blue_line; API-LEGACY-01; normal Bridge path succeeds'],
['Chart ordinary unit suite','PASS','78 passed; isolated unit transport evidence'],
['Source defect-focused correctness controls','FAIL','Confirmed transitions diverge; successful probe execution is not algorithm PASS'],
['E tie native eligibility/final-output reproduction','FAIL','4 final-visible E rows select wrong Order; 20 unique physical branch conflicts'],
['Observation hook semantic neutrality','PASS','Complete idx8/14 and tie trace stable payloads equal original executions'],
['Supplied stale-S causal diagnosis','FAIL','Current accepted E independently rejects all revived A; proposed wrong-Order causal claim not reproduced'],
['General invalid-S ownership release experiments','PASS','2 datasets ×2 directions ×3 passes; original eligibility reconstruction matches; zero accepted restorations'],
['Known USOIL StopAll anchor outputs','PASS','September25 S red/count2/direct parent and October2 E1 red/count2 gates in target and merged history'],
['Live HTTP/server/browser / production child session','NOT RUN','Source+isolatedunit review only;no live endpoint claim'],
['Complete post-fix engine counterfactual','NOT RUN','No fix phase authorized; bounded Blue/A oracle only'],
['Historical previous-Source full differential','NOT RUN','Historical Reference claims not rerun or relabeled'],
['Full Doji-inclusive runtime mirror domain','INCOMPLETE','Explicit Doji invariant read; no-Doji runtime fuzz is bounded'],
['All high-confidence/suspected accepted-output proofs','INCOMPLETE','Specific normative/reachability gates described'],
['Specification conflict resolution','INCOMPLETE','LC-02/SE-03/Order_B formation remain undecided'],
['Formal all-input algorithm correctness','INCOMPLETE','Finite RAW/tests cannot prove every history; confirmed failures remain'],
['Performance/memory benchmark/soak','NOT RUN','Observed wall times only; no profiling or SLA claim'],
['Protected original file preservation','PASS','51 hashes unchanged; 12 package/live Source files unchanged'],
['Pre-existing Git/index/HEAD preservation','PASS','No status delta outside owned audit; HEAD unchanged'],
['Chart byte before/after proof','INCOMPLETE','No initial chart hash baseline; current coverage hashes and owned mutations recorded'],
]
if decimal:
    check_status='PASS' if all(i['numericLexemeValuesPreserved']=='PASS' and i['exactOHLC']=='PASS' for i in decimal['exactValidation']) else 'FAIL'
    checks.insert(10,['Current market exact Decimal/lexeme validation',check_status,'All15 originals compared exactparseagainstproduction numericparse;syntheticedge remainsNUM-JSON-01'])
assert all(r[1] in ('PASS','FAIL','NOT RUN','INCOMPLETE') for r in checks)
(OUT/'verification-matrix.json').write_text(json.dumps([dict(zip(('check','status','evidence'),r)) for r in checks],indent=2),encoding='utf-8')
section(20,'Verification Matrix',f'''
PASS always names a concrete executed or read/integrity scope. FAIL names an observed incorrect result or failed authority assertion. NOT RUN is never inferred from elapsed time; INCOMPLETE names a remaining proof/authority limit. Successful process completion is separated from algorithm correctness. Probe commands that reproduce a defect can exit0 while their correctness assertion is FAIL in this matrix.

{table(['Major check','Status','Exactly what was established'],checks)}

Machine-readable matrix: {link('verification-matrix.json')}. Summary: {link('audit-summary.json')}. Protected state: {link('integrity-final.json')}. Findings: {link('findings.json')}. Coverage: {link('coverage-ledger.json')}. Exact commands, stdout, stderr, stable compressed payloads, input hashes and wall times remain in each matrix directory. All writes are confined to this owned audit directory.

**Next review action (under2minutes): open section5 and review SE-01's four final-visible RAW cases before authorizing any fix phase.**
''')
assert len(sections)==20
report='# TradingBot forensic audit — Current authoritative engine\n\n'+\
       'Evidence date:2026-10-05–2026-10-06 · Asia/Tehran · READ-ONLY SOURCE / IMMUTABLE RAW · No fixes implemented.\n\n'+\
       '\n'.join(sections)
(OUT/'AUDIT_REPORT.md').write_text(report,encoding='utf-8')
print(json.dumps({'report':str(OUT/'AUDIT_REPORT.md'),'sections':len(sections),'words':len(report.split()),
                  'confirmed':len(confirmed),'highConfidence':len(high),'verificationChecks':len(checks)},indent=2))
