# CP387 — accepted Order_B owners and feedback identity

Pinned source: `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 442–553. Independent local source scope only.

## OA11-A (442–464)

Accepted A list is an ordered filter of input by exact (source_time,int(source_index)) invalid identity membership; no duplicate suppression or extra lifetime gate.

## OA11-B (465–474)

Each retained A obtains reaction_number via int then native ordinal-1 indexing; zero can index last item and invalid indexes can raise. Confirmation delegated to chronology with direction; S first_a_stop receives normalized price, uses returned slot 2 or None.

## OA11-C (475–485)

Traverse supplied S then E, use E parent_stop result slot 1 or None; append StopAll explicit stop_event_time; retain open lifetimes. Dominant post-behavior stops are calculated separately from anchors.

## OA11-D (486–504)

Collect anchor candidates from accepted A, supplied S, E and StopAll in that order; source time and int index form identity, callback priority and int number/default zero form ranking with behavior type. Repeated priority calls require stable callback semantics.

## OA11-E (505–513)

Dict key exact source time and int index; replace only for strictly greater lexicographic priority,number,type. Equal rank keeps first; replacing value does not move insertion position. Anchor winner independent of stop dominance.

## OA11-F (514–522)

Truthy injected finder wins, otherwise native OA06. Supply accepted A trigger_event_time without fallback, ordered anchor tuple, and dominant stops. Return finder result as-is; no local validation of injected result.

## OA12-A (523–529)

OrderMatch tuple type alias declares shape only; no runtime validation or leg ownership action.

## OA12-B (530–553)

Sorted tuple of 17-field leg signatures: stop type/index/event, anchor type/index/time/extreme, int reset reaction First/Break, reset source index/level/time, leg boundary/index, strict-break time, int physical First/Break. Retain multiplicity; native tuple sorting/comparison, no string Decimal normalization. Exclude stop source time, reset confirmation, boundary source time, physical number and confirmation; not complete object identity. Malformed or incomparable data may raise.

## Consumer boundary

Trading pipeline lines 2616–2645 invoke discovery on supplied accepted-state inputs, compare signatures and register the discovered legs on equality. A repeated signature or eight-pass exhaustion raises. This establishes the conditional consumer path, not convergence or full cross-owner acceptance.

## Evidence

339 category rows (61 W1, 278 additional), 5 historical supplements, prior 1270 rows revalidated without overlap or identity errors. Local source review only; validity of accepted S/E/StopAll inputs, A ordinal and chronology, deterministic priority, injected finder equivalence and creator/consumer ownership require independent cross-owner review. Feedback signature equality is not full object or Decimal representation equivalence; downstream fixed-point and serialization obligations remain open. No RAW payload, runtime, ZIP or production changes.
