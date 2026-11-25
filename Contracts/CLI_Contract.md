# Trading Bridge CLI

| Option | Type / requirement / default |
|---|---|
| --reaction-engine / --engine | Path required |
| --blue-line-engine / --blue-engine | Path required |
| --a-zone-engine / --a-engine | Path required |
| --s-zone-engine / --s-engine | Path required |
| --e-zone-engine / --e-engine | Path optional |
| --lifecycle-engine / --stopall-engine | Path optional, fallback pipeline/lifecycle_engine.py |
| --blue-lines | enabled/disabled; enabled |
| --a-zones | enabled/disabled; enabled |
| --s-zones | enabled/disabled; enabled |
| --bridge-output | flag, false |
| --pl-ph | enabled/disabled; enabled |
| --data | Path required |
| --timeframe | integer >=1 required |
| --raw-timeframe | integer >=1; default 1 |
| --from-time | integer required |
| --to-time | integer required |
| --direction | bullish/bearish/both required |

Load Reaction/Blue/A/S even if some stages disabled. E only if path supplied; lifecycle always path or fallback; primary only when pl-ph enabled. Strip UTF-8 BOM, parse RAW JSON with Decimal, calculate full history. Empty input rejects. Range is presentation-only. Exact full response schema not certified.
