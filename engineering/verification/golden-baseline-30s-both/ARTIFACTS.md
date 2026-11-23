# Full artifact inventory, checksums and storage

The following items are **currently stored in persistent ChatGPT Library**, NOT uploaded as binary ZIPs in GitHub. These filenames/paths refer to **Library inside the connected ChatGPT account**, not filesystem paths or accessible GitHub URLs. Download and retain independent backups to reproduce all results.

| Archive | Bytes | SHA-256 | Library folder |
|---|---:|---|---|
| TradingBot_GitHubMain_Baseline_30s_Both_01d54ecf_20261123_v1.zip | 7601951 | `080175abbd7a3895596230b40783062901deb38c0cc8dd3b97fc058ef21cbb88` | `/TradingBot/Baselines/2026-11-23/` |
| TradingBot_Engine_V8.1_30S_BOTH_VERIFICATION_20261123.zip | 15482107 | `2b31ab07ec697f5e8528fe153199f641d0f6954389a0c3669e12fe29a3c18b05` | `/TradingBot/Versions/V8.1-2026-11-23/` |
| TradingBot_Engine_V8.2_30S_BOTH_VERIFICATION_20261123.zip | 28534432 | `973f82486f78c95b988cb81fe9c36517764c5f247c35653794ef9e5057f6ea5a` | `/TradingBot/Versions/V8.2-2026-11-23/` |
| TradingBot_V8.2_SYNTHETIC_RAW_1M_5S_seed20261123.zip | 12476929 | `753aab83ef3bdcbaeffb15cd3957ab4ce4f00894a68797371d048d7d173ce702` | `/TradingBot/Versions/V8.2-2026-11-23/` |

Also preserved in Library:
- `/TradingBot/Baselines/2026-11-23/complete_comparison.csv`, `input_manifest.json`, `summary.json`, `README.md`.
- `/TradingBot/Versions/V8.1-2026-11-23/` audit, release status, input checksums, source ZIP and verification ZIP.
- `/TradingBot/Versions/V8.2-2026-11-23/` audit, performance matrix, synthetic manifest, source and verification ZIP, delta diff, charts and synthetic input archive.
- V7 comparison ZIP: `TradingBot_V7_Comparison_30s_Both_01d54ecf_20261123_v1.zip` in baseline folder. Its checksum is **not independently pinned in this file**; verify the package's `SHA256SUMS.txt` on retrieval.

## Golden ZIP details

The 7 per-file `runs/github_baseline/*.json` original native outputs and matching `*.stable.json` are contained in the golden ZIP; each baseline input also has `*.metrics.json` and log. The freeze ZIP additionally contains original pinned executable source and baseline verification scripts.

The repository `inputs.json` stores the SHA256 of each stable result. To verify whole ZIP independently:

```sh
sha256sum TradingBot_GitHubMain_Baseline_30s_Both_01d54ecf_20261123_v1.zip
# Expected: 080175abbd7a3895596230b40783062901deb38c0cc8dd3b97fc058ef21cbb88
```

**Warning:** until the full Golden ZIP and seven RAWs are downloaded, someone with only this GitHub directory cannot independently rerun complete zero-difference verification. The repository contains the detailed recorded metrics and hashes, not 7 complete binary result snapshots.
