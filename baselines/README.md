# Frozen refactor inputs

- Original correctness oracle: `01d54ecf0149ebd15de92798be18810b6e2eb791`. Never substitute current `main` or `refactor` HEAD.
- Historical pre-isolation refactor snapshot: `eef50eb2cedb06ba4c77bb82c6ac3b312ef1e7ba`. Contains previous Chart work and earlier Engine tests; read-only, not a new Golden oracle.
- V8.1: `V8.1.patch` contains only the refactor delta across three modules. `manifest.json` pins all fifteen runtime module SHA256 values for each source and patch SHA256. Local reconstruction applied to the frozen Original and verified 15/15 module bytes against the archived V8.1 source.

Reproduce in an **isolated checkout**, never this branch's tracked tree:

```sh
python tooling/verify_baseline.py --manifest baselines/manifest.json --engine /path/to/frozen/engine --variant original
git -C /path/to/frozen apply --check /absolute/path/to/workspace/baselines/V8.1.patch
git -C /path/to/frozen apply /absolute/path/to/workspace/baselines/V8.1.patch
python tooling/verify_baseline.py --manifest baselines/manifest.json --engine /path/to/frozen/engine --variant v81
```

No RAW bodies or complete product source are included. Frozen case manifests in the V9 workspace pin RAW and stable output digests. Obtain actual files from their authorized source, validate hashes and preserve originals.
