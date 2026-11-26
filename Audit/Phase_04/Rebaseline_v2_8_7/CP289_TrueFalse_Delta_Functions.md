# CP289 — engine/pipeline/true_false.py current declaration delta

Pinned main: c99b4c957e932d9ee70c492ca03ce80711447fc1. Blob: ebf9999d925d1ff5cb41d8be3d42e213c5840d6e. Scope: changed and added named declarations from CP287 structural delta; current source supersedes historical function descriptions for these scopes. The unaffected portions of historical TB/TF contracts remain navigation evidence, not proof of complete runtime equivalence. Native exceptions propagate unless an owning path explicitly catches them. No production execution.

## TFD01 — BasicRepeat

Current lines 34–38; changed; old lines 33–36.

Mutable slotted record: latest dict reference, repair_count, verdict_count, base_count; all required. Counter domains differ and are not interchangeable.

## TFD02 — _crossed_verdict

Current lines 47–55; added; new declaration.

Input references rank->ordered pairs, rank, normalized Decimal price. Visit keys in descending order. Only smaller ranks qualify. Lower-bound price using pair first element, if insertion index nonzero return verdict at index-1; else try next smaller rank. Return null if none. This finds most recent surviving strictly crossed reference at greatest qualifying rank, not a parent-source lookup. No mutations. Comparison/search errors propagate.

## TFD03 — _basic_verdicts

Current lines 58–128; changed; old lines 45–94.

Initialize empty repeats and references, started false; resolve direction policy even if event list empty. On any non-S/E event clear references, set started false and zero verdict_count/base_count in all retained repeats, not repair_count. S sets started true; ignore other basic rows before S. Derive rank and source time, collect lower repeat ranks in insertion order; Decimal(row.price), copy-negate if low-direction. Engulf=any lower base_count>=2, display_restart=any lower verdict_count>=2. S or engulf -> T; otherwise use crossed verdict, invert T/F when present, else F for odd number and T for even. Write verdict. For rank history pop tail while tail price>=current price then append pair. Remove lower repeat entries; repair prior latest only if F and repair_count=1. Same-rank previous: start repair/verdict counts 1; on same verdict add prior repair count; if not display_restart add prior verdict count, mark both previous and current repeated when >=2. If same verdict F, remove previous repair if default -1 or value comparison is >= current source time (only if predicate true), then call repair on current. Base count increments from any previous same-rank entry irrespective of verdict, else 1. Store new BasicRepeat. Nested repair callback unchanged: if present and REPAIR absent invoke with native price, write non-null result. No final sweep, no implicit rollback or return value. Supersedes TF04.

## TFD04 — apply_true_false

Current lines 162–188; changed; old lines 128–156.

Pick primaryLows if exact bullish else primaryHighs. Visit primary, StopAll, E, S; missing collection empty. Clear all three annotation keys from every visited row; if calculationValid is not exact false first per sourceTime wins. Sort winners by sourceTime; initialize each verdict null. For primary flush pending StopAll verdicts and clear buffer, assign T/F/F to numbers1/2/3. StopAll rows append to buffer. Then invoke Basic verdicts on entire ordered event stream (including primary and StopAll boundaries), not old basic-only buffer; finally evaluate remaining StopAll. Returns no value. Row mutations and callback failures not rolled back. Supersedes TF07; TF01/02 repair, TF03 rank, TF05 nested repair and TF06 StopAll logic unchanged.
