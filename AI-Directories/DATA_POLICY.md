# Data and generated-output policy

- `market-data/raw/` is the raw candle inventory. Do not edit a source dataset
  to make an algorithm test pass.
- Candle records require time/open/high/low/close integrity, ascending time,
  and `Asia/Tehran` rendering for local timestamps.
- `tmp/` and `primary-cache/` are disposable working data, not durable AI
  knowledge or normative examples.
- Generated calculations, test output, reports, screenshots, and Graphify
  artifacts are evidence with provenance; they do not replace source, specs,
  and tests.
- Never commit credentials, tokens, private keys, or raw data excluded by
  `.gitignore`.
- Durable examples must include the exact inputs, date/time/timezone, expected
  outputs, and the code/spec version that produced them.
