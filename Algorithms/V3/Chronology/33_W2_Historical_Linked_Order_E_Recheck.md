# CP348 — historical matrix-linked Order Audit and E review

26 exact IDs directly reviewed; cumulative 92/131 historical linked records. W2 NOT_ACCEPTED.

### CP324-S24 · engine/pipeline/order_audit_engine.py:2520–2544

First-index map last duplicate wins, native matches sorted by confirmation,integer First/Break,one-based ordinal,object. Cache exact stopped-A event including null.

Handoff: First map is not physical identity until Break also matched.

### CP324-S25 · engine/pipeline/order_audit_engine.py:2546–2598

Compute native first eagerly; optional callback at exact gate, reject missing/incomplete geometry, First<gate or confirmation<=A stop. Exact pair remaps to canonical number/object and recomputes confirmation without reapplying threshold; otherwise number0. Compare independent and native by (First,confirmation), strict earlier wins, native tie.

Handoff: No invented public Reaction. Independent geometry callback evaluated per invocation; returned upper bound not independently validated.

### CP325-S03 · engine/pipeline/order_audit_engine.py:77–136

Rank lifetimes priority,number,source time,index, earliest equal ordinal. Activate trigger or decision or source <= each distinct stop; expire only end<event. Owner by object identity at exact stop. Map clamped main and choose greatest rank including event for each main; sorted event/index.

Handoff: Dominant stop is not geometric anchor. Priority callback reevaluated for candle winner; inclusive lifetime boundaries.

### CP325-S11 · engine/pipeline/order_audit_engine.py:442–520

Accepted A excludes exact invalid pair; native trend confirmation via unguarded ordinal−1, S first A stop triple[2]. S/E parent stop pair[1], StopAll explicit stop. Keep open lifetimes, independent anchors all accepted sources with max priority/number/type per exact pair. Truthy finder or native, pass accepted A trigger times.

Handoff: Default intrabar flag here distinct from A formation false flag. No local recomputation of callback results or dominant-neutral anchor replacement.

### CP325-S12 · engine/pipeline/order_audit_engine.py:523–550

Sort 17-field leg signature: stop type/index/event, anchor type/index/time/extreme, reset reaction First/Break, reset index/level/time, boundary/index, strict break, physical First/Break. Retain duplicates.

Handoff: Not full record equality: excludes stop source time, reset confirmation, boundary source time, physical number/confirmation; feedback CP346 uses this exact signature.

### CP325-S16 · engine/pipeline/order_audit_engine.py:809–918

Cache includes start,deadline,bounded/E flags,confirmation_after, null membership. Geometric first then optional threshold. Native lower bound gate First, optional confirmation threshold loop, then blocked same-gate loop with exact E exception strict confirmation>start; no repeated threshold after skips. Compute independent stop/cross even if restart geometry preferred. Prefer restart under deadline condition, else geometry only with independent no crossing and strictly earlier First or absent independent, else independent. Singleton min key still evaluated.

Handoff: No universal confirmation>start gate, no unconditional retry; callback errors propagate.

### CP325-S18 · engine/pipeline/order_audit_engine.py:982–1086

Cache by gate/deadline/flags, shallow list hit. Direct then optional trend parent-stop, B legs First>start merge label into existing tuple or form new crossing. Enforce one parent owner before deadline. Earliest actual cross else range_end, clamp optional continuous deadline; confirmation<=deadline, sort crossing else range_end,First; cache tuple. First_order filters crossed only.

Handoff: B creation independent; no blanket upper cap range_end when actual crossing exists. No parent cause assignment by consumption.

### CP325-S20 · engine/pipeline/order_audit_engine.py:1135–1199

Truthy legs invalidate carried; new physical ledger row canonical stop/cross and index, existing geometry untouched. Full reset-leg cause includes stop/anchor/reset/boundary/physical provenance; native str selected prices. Full dict equality dedup, sort exact stop/reset/break/physical pair, invalidate on unique append.

Handoff: No local acceptance revalidation or rollback. Reset breakout main versus exact confirmation separate.

### CP325-S40 · engine/pipeline/order_audit_engine.py:2206–2288

Retain prior valid parent-stop causes; existing identity updates set, absent restores shallow row+new causes and confirmation index. Rebuild public method copies zones. Ensure snapshots ledger parent sets, rebuild then only absent identities restore after filtering S causes by invalid/accepted E source-time projection; B-only retained, restore index; invalidate carried unconditionally.

Handoff: No merge into superseding present identity in ensure; absence restore no cross recomputation. Invalid S filter exact S label/len>4, not kind check.

### CP325-S41 · engine/pipeline/order_audit_engine.py:2291–2401

Parent cause key type/family/event/source. S entries use truthy a_causes else fallback, optional accepted A source filter; E sort parent tuples by str, exclude A source not accepted, extend B by reference. Merge First range unless required identity; first geometry wins, later distinct causes extend; stop_cross key absence triggers query, explicit null retained.

Handoff: Required bypasses presentation range only, not cause eligibility. No dedup of initial supplied list.

### CP325-S42 · engine/pipeline/order_audit_engine.py:2404–2459

For each parent-stop cause key min (confirmation,First,Break), first tie. Retain non-parent always, parent only selected object, drop rows without causes; retained dict cause list mutated, original native ledger unchanged by this list reduction. Combine S before E, merge then owner reduction.

Handoff: Prepared visibility ledger not native creation audit. Duplicate winning causes remain; B independently retained.

### CP326-S03 · engine/pipeline/e_zone_detector.py:148–174

Live dirty requires exact chronology object and nonnull frontier. Stop key less/start/Decimal level, previous open or dirty-or-later hit shrinks scanned_until to min(old,dirty), resets event. Settled hit only returns if before range_end. Resume max(start,scanned_until), stop if outside; cache hit/open progress at event or end.

Handoff: Shared stop cache keyed strict side not owner type; current and previous progress differ; no main fallback.

### CP326-S04 · engine/pipeline/e_zone_detector.py:176–194

Extreme key direction/start/end. Current hit or previous only end main timestamp<dirty; else lazily build own LowerTimeframeIndex over main and query min/max inclusive via end+1; return integer candle.index,detector time,price.

Handoff: Main extreme distinct from lower exact stop; full candle boundary may include later prices.

### CP326-S05 · engine/pipeline/e_zone_detector.py:196–218

Zone key direction,family,number,parent identity/price,stop,Order ordinal/geometry/confirmation/stop tuple/causes,source tuple with str prices. Requires cross. Current hit; previous only max(parent stop,cross,confirmation)<dirty; else native build.

Handoff: Reuse after selected Order race, not replace it; omitted timestamp/direction consistency is caller contract.

### CP326-S08 · engine/pipeline/e_zone_detector.py:313–392

Validate direction and priority nonnull; copy invalid set, initialize accepted identities/reset mapping; native inputs copy/sort S and opposite resets. Range index converted/accessed, no explicit chained bounds validation. Prepared main extrema only no live and exact same candles object, TF1 fallback lower index; otherwise sparse; live separate. Blocked/audit truthy defaults, B tuple, initialize independent audit.

Handoff: No arbitrary priority function semantics, no index identity equivalence from equal rows. Range validity caller-owned.

### CP326-S09 · engine/pipeline/e_zone_detector.py:394–411

Getter returns actual reset dict alias. Setter copies, sorts keys, clears four existing nonnull caches (order candidates,carried,post-stop,direct parent), in order.

Handoff: In-place alias mutation bypasses setter; no full reset or rollback.

### CP326-S11 · engine/pipeline/e_zone_detector.py:440–504

Optional chronology direction cache holds value/code/sparse triple references; no dict created when absent. Build sparse powers of two, strict directional extreme else earliest index; inclusive query two overlapping blocks, nonpositive length returns left.

Handoff: No local clamp/validation; cached owner sequence coherence required.

### CP326-S12 · engine/pipeline/e_zone_detector.py:507–557

Parent first stop clamps start and uses native or optional live search; lower half-open, direction-specific strict side. Native cross_order inherited, live per-detector cache including null with chronology validation even on hit; live stop maps index and self.times[index].

Handoff: Parent starts decision in public call, opposite order distinct side; times representation must match native candle timestamp under coherent chronology.

### CP326-S13 · engine/pipeline/e_zone_detector.py:559–578

Default native confirmation direction, opposite convenience, First time main int index. Both S and E parent stop start decision_event_time with Decimal price; type label does not change calculation. Public delegate.

Handoff: No source-open parent stop or independent display proof.

### CP326-S21 · engine/pipeline/e_zone_detector.py:915–1005

Restore independent roots only accepted S physical sources not occupied E, candidate direct S number1 and valid cause. Heap source time/index/ordinal, skip newly occupied parent. Disowned-S-only order triggers replacement race with owned source times, enqueue unique full-record roots. Same-parent remove one min(decision,source) object then append root, not all. Else append if exact identity absent, mark occupied. Resolve same source final, publish accepted identities.

Handoff: Consumed S not in accepted input cannot create root; no arbitrary cap, repeated candidate full equality guard.

### CP326-S26 · engine/pipeline/e_zone_detector.py:1132–1173

Group by source index, pending minima time/decision independently for indices>=frontier; all candidates indexed. Restore numbered prefix/active/sequence from checkpoint; accepted set aliases detector. Candidate pair last wins, S pair first wins; known full-record set.

Handoff: Frontier controls initial heap only; no independent validation of checkpoint previous/count.

### CP326-S27 · engine/pipeline/e_zone_detector.py:1175–1218

Index numbered first pair/time wins, sorted unique times, S parent times. Child max decision for every E candidate including below frontier. Enqueue null/known skip; first regeneration shallow copy input; update maps/groups and schedule new different source if absent, same-source group shared; prior scheduled key unchanged.

Handoff: No index/frontier restriction inside enqueue itself; native regeneration can reopen race.

### CP326-S31 · engine/pipeline/e_zone_detector.py:1365–1404

Priority uses first active E parent same source time (not index), family from truthy parent else candidate; select min negative priority,decision,parent stop. Determine stopped families; parent active iff S, source time==sequence_start, or exact active parent pair; otherwise skip.

Handoff: Family priority before chronology; eligibility does not alone imply accepted active parent.

### CP326-S32 · engine/pipeline/e_zone_detector.py:1406–1453

Owner first active E same parent time, explicit nonnull. Red parent or stopped Red dominates; else Blue parent or stopped Blue; number max stopped same family+1 or1. Remove stopped physical identities, append replaced family/number, index and accepted sets. Hard reset source clears active and updates sequence start else append.

Handoff: Preserve physical source and Order provenance on renumbering; historical numbered output persists.

### CP326-S33 · engine/pipeline/e_zone_detector.py:1454–1464

Only regenerated accepted parent queries next stop; if hit flag reopened, race child using current family,number+1 and accepted source times; enqueue only nonnull child source index>current.

Handoff: Original native descendants already pending. Hard reset does not skip regeneration stop query.

### CP326-S35 · engine/pipeline/e_zone_detector.py:1495–1506

Clear accepted source set and audit; register B legs; clear visual starts; discover and snapshot candidates; reconcile, apply consumed S, resolve same-source, rebuild accepted audit and return.

Handoff: No rollback on failure; final audit from accepted chain, not candidate list.

Qualified OA-M02 and CH25. All earlier evidence preserved. No production, runtime or RAW change. F05/R01/R02 remain open.
