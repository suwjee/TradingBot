# User working rules

## Communication and evidence

- Default to concise Persian RTL; retain precise English terms where helpful.
- Write all persisted records in English: rules, lessons, examples, documentation,
  implementation notes, code comments, and verification records. This applies
  to new and updated records; user-facing conversation may remain in Persian.
- Report exact local date, time, timezone, input range, source file, and test
  command when discussing candle or pipeline evidence.
- Explain failures by separating data, specification, implementation, and
  expectation causes.

## Rule changes

- Ask for clarification before implementation if eligibility, source windows,
  comparison strictness, event order, reset, or directional mirror is unclear.
- Formalize a confirmed rule before changing source. Update each affected
  specification, module, bridge, tests, and AI documentation together.
- Never hard-code a historical range, source filename, or expected event to
  alter production behavior.

## Testing

- Use the exact user-selected data and range.
- Treat the integrated order as `Reaction -> Blue -> A -> S -> E -> StopAll`.
- Run a Reaction regression when Reaction changes; run bridge/UI validation
  when its input/output contract changes.
- For optimization, require benchmark evidence and byte-equivalent output.
