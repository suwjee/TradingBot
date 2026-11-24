# Historical archive and recovery index

The standalone workspace deliberately contains no complete product source. All prior files are preserved by immutable Git history, not duplicated in the active tree.

- [Pre-isolation index](pre-isolation-index.json): exact prior paths, blob SHA, size and relocated paths from commit eef50eb2cedb06ba4c77bb82c6ac3b312ef1e7ba.
- [Pre-cleanup index](pre-cleanup-index.json): the 118 earlier large/superseded files removed from the active tree.
- Old product/refactor source snapshot: https://github.com/suwjee/TradingBot/tree/eef50eb2cedb06ba4c77bb82c6ac3b312ef1e7ba
- Original correctness oracle: 01d54ecf0149ebd15de92798be18810b6e2eb791.

Use read-only `git show <commit>:<path>` or an isolated checkout; never restore product trees to this branch. Historical source, workflows, old protocols and superseded observer implementations are not current authority. Git history remains reachable; no privacy or storage-size claim.
