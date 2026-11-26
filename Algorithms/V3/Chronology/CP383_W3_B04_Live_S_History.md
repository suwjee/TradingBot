# CP383 — Live S history

Pinned source: `53460e68538ac790ab969084c1c7101e5ca833d7`.


## CP383 — Live S continuation and B04 exact local union (W3)

- **S44 (1424–1430)**: Reaction input signature is a tuple of native first_idx, break_idx, mode, optional intrabar_start, box source indexes and str(box_top/bottom), optional anchor_idx and str(optional anchor_value). Representation and hashability are native; str(None) is retained, no as_tuple normalization, no full object identity.
- **S45 (1433–1446)**: LiveS continuation constructor owns an initially None scope, empty dependency set and empty decision dict, independent of detector; class docstring describes intent, not arbitrary-input proof.
- **S46-A (1448–1456)**: Dependency set comprehends trend then opposite reactions, zero-based enumerate, native break index into candle_times and side, number, S44 signature. Timestamp is Break main open, not confirmation. Native set membership/hash/equality can fail; duplicates collapse.
- **S46-B (1457–1466)**: Adds reset event and int(from_first_idx), reset-blue event and number from first-reset map, and public-blue event alone. Set update collapses duplicate equal entries; no full Blue or A record coverage is asserted.
- **S47-A (1468–1483)**: Settlement begins at decision_event_time; Type3/4 return directly, otherwise native assert order_match, confirmation and lower-bound at max(confirmation,range_start); absence of any lower row at or before decision yields None. This is existence only, not a crossing or range_end test.
- **S47-B (1484–1490)**: Extends through to Order Break main open; calls first trend reaction after Order confirmation even if actual route was Advanced or pre-Order; if aligned extends through to its Break main open and confirmation. No current Reaction identity claim beyond returned tuple.
- **S48-A (1492–1500)**: Dirty admission inclusive zero to len(candles); no exact-integer check. Scope tuple direction/timeframe/start_index/range_start excludes end_index and input identity. Dirty is current main open at index or range_end at len. Current dependencies computed before scope comparison.
- **S48-B (1501–1507)**: Same scope computes earliest timestamp from symmetric difference, default=dirty evaluated eagerly, then min with dirty. Reuses prior decisions dict reference; changed scope selects fresh empty dict. Current decisions always fresh.
- **S49-A (1509–1515)**: Nested resolver builds order key None or (order[0],S44(order[1]),order[2]); A key ordinal,source_index,source_time,str(price),stop,order_key. Previous lookup only; strict previous settlement < dirty reuses exact tuple and S reference and inserts into current. Equality at frontier recomputes.
- **S49-B (1516–1521)**: Miss resolves current detector candidate; nonnull only obtains settlement; stores pair only for nonnull settlement; returns result regardless of cacheability. None is not cached; no current lookup and no in-place S edit.
- **S48-C (1523–1525)**: Always invokes detector._detect(resolve), including native audit/ownership clear/rebuild. Only successful return publishes scope/dependencies/current together, then returns output directly. Failure before publication retains old wrapper fields but detector/external aliases may already mutate; no rollback or shallow copy.
- **S50 (1528–1552)**: Public helper creates fresh SZoneDetector with supplied positional args then calls detect; no continuation cache. Native argument evaluation, constructor and detect failures propagate; output direct.

The nine local registers CP375–383 reconcile exactly to 4,248 canonical rows (962 W1, 3,286 additional) and 71 unique historical supplements. No missing, overlap, or identity mismatch. This is local scope only; cross-owner chronology, dirty frontier, cache freshness and external rollback obligations remain open. CP383-F01 resolved scoped documentation.
