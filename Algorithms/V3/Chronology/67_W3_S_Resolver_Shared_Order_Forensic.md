# CP382 — S resolver and shared Order reconciliation

Pinned source: `53460e68538ac790ab969084c1c7101e5ca833d7`; B04-08 1225–1423. 604 category rows, 143 W1, 461 additional, 8 supplements; 3213 prior rows revalidated without overlap.

### W3 CP382 — resolver, ownership publication and shared Order reconciliation (S40–S43)

- **S40 (1225–1236)**: Deadline is supplied Order confirmation if match nonnull else range_end. Call Type3 then Type4 before any arbitration; failures propagate even if first route could win.
- **S40 (1237–1246)**: Type3 nonnull wins if Type4 absent or its event<=Type4 event; true timestamp tie Type3. Else Type4, else S12 Order-backed if match, else None; no Order-backed call when order-free wins.
- **S41 (1248–1250)**: Public detect passes bound native resolver to S42, no independent acceptance.
- **S42 (1251–1257)**: Fresh output; clear existing ownership list then order_audit dictionary in place. Audit all sorted A before cycle, including A later excluded; no rollback on partial audit failure.
- **S42 (1258–1267)**: Cycle starts range_start; one-based ordinal for every sorted A before exclusions. S26 ownership first, then source<cycle or source==cycle with nonempty output.
- **S42 (1269–1278)**: Evaluate immediate next sorted A confirmation even if later ineligible. Normalize current price, obtain current S07 confirmation and S10 stop; null skips.
- **S42 (1279–1285)**: Call first physical Order lookup before next confirmation rejection; A stop>=next confirmation skips, equality excluded. Provider and callback effects can occur even for rejected candidate.
- **S42 (1286–1290)**: Append open window before supplied resolver; None leaves open and continues. Exception can leave open and prior audit mutations; no transaction.
- **S42 (1291–1304)**: Append successful S then update cycle from source main, close last window at max(stop,decision_event+1µs). Exclusive end includes decision if representable; overflow can leave partial state. Stable final sort source/decision event, not ownership sort.
- **S43 (1307–1324)**: Accept caller-supplied zones and Order entries; docstring assumes calculation-accepted ledger, local function does not establish that status.
- **S43 (1325–1342)**: Dedup by int First/Break after skipping null reaction. Retain first unless existing stop_cross None and new nonnull, even malformed. Later validity check, insertion position retained. No parent match.
- **S43 (1350–1360)**: For each retained entry read reaction and int First before confirmation isinstance(datetime) gate. Normalize required stop_level even for existing crossing; no exact naive-type restriction.
- **S43 (1361–1374)**: Trust crossing shape tuple len>=3 and datetime third slot, otherwise call mixin. No strict price or first-two slot validation for accepted shape. Reject None or not confirmation<event. Sort stable key event,confirmation,First,Break.
- **S43 (1376–1387)**: For each supplied S, bisect earliest shared crossing >=source_time (main, inclusive); only first examined, require <old decision. No confirmation>=source or parent check; absent winner appends same object.
- **S43 (1389–1394)**: Winner reads retained entry/reaction, int First/Break/top/bottom source before replace. Mutable entry aliases not transactionally snapshotted.
- **S43 (1395–1414)**: Replace immutable S record red, direction and Order identity/provenance incl mode str, normalized box edges and stop price, indexes/main/confirmation times. Does not mutate physical Order entry or rewrite creator.
- **S43 (1415–1423)**: Clear Reset ordinal/time, replace decision index int and supplied main/event slots. Unlisted formation_type/A/source geometry unchanged; fresh output original zone order; ownership windows unchanged.

The native all-A audit and supplied accepted-ledger input have distinct ownership. Dedup preference precedes crossing validation; accepted shape is not local proof of strict price. No external transactional rollback or global W3 closure is asserted.
