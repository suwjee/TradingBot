# TradingBot release operations

`git.bat` is the interactive Git Manager. `Invoke-TradingBotRelease.ps1` is the scripted release command. Both derive the project root from their own locations, so they work from the current checkout without a hard-coded drive path.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\git\Invoke-TradingBotRelease.ps1
```

Run this validation command before publishing:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\git\Invoke-TradingBotRelease.ps1 -DryRun -CommitMessage "Validate release" -ReleaseTag "your-valid-unused-tag" -VerboseReport
```

`-DryRun` is a real, non-publishing validation. It does not stage the active index, create a permanent branch or tag, push, or create a GitHub Release. Missing message or tag values are prompted once; parameters support non-interactive use.

## Content policy

`main` is inclusion-first. Legitimate tests, maintained documentation, meaningful engineering evidence, meaningful Graphify reports/manifests/inventories, and classified `BaseLine` reference data remain eligible. The policy classifies files by producer, consumer, and enduring value rather than directory name.

Only narrowly proven disposable material is excluded: dependencies restored from manifests, build products, interpreter caches, temporary files, local secrets, and machine-local chart state. `apps/chart/state` is never copied to production; the launcher creates required directories at runtime without deploying current local contents.

`production` is dependency-derived and default-deny. The workflow resolves runtime closure from the exact committed main SHA, then replaces only a temporary worktree snapshot with those selected paths. It checks policy, sensitive markers, PowerShell and JavaScript syntax, Python AST and bridge help, `npm ci`, and the chart build.

## Branch and authentication safety

The workflow reuses existing Git and GitHub CLI authentication without reading or storing credentials. It independently checks Git push authorization with a non-mutating dry-run.

`origin/production` is required. When local `production` is absent, the candidate starts from freshly fetched `origin/production` in a detached temporary worktree. Only after validation does the workflow advance local `production` with an expected-old-value guard and configure its `origin/production` upstream. Publication always uses explicit refspecs.

If local `production` has independent commits, the validated runtime snapshot gains a second parent that preserves that local history. Its tree remains the exact dependency-derived runtime file set. Promotion checks both parent histories and the unchanged local ref before advancing `production`; an operation without a new snapshot still requires a fast-forward production target.

Publication first uses one `git push --atomic` for `main`, `production`, and the annotated tag. If atomic push is unsupported, fallback is allowed only after every target remote ref is proven unchanged. The fallback verifies each ref immediately and stops with explicit partial-failure reporting; it never hides a partial result.

## Traceability and Recovery

Changed production content receives `TradingBot-Main-Source: <main SHA>` in its commit trailer. When the production tree is unchanged, no empty commit is made; the annotated tag and GitHub Release metadata carry that source SHA. The annotated tag always points to the exact production release commit.

If validation fails, inspect the reported policy, closure, or tool check and correct it before retrying. If publication reports partial failure, do not retry blindly: compare the reported remote `main`, `production`, and tag OIDs, reconcile the remote state deliberately, then rerun with a new unused tag only when appropriate. Temporary worktree cleanup is reported separately.

No publication occurs during implementation validation or `-DryRun`.

## Interactive Git Manager

Run `scripts\git\git.bat` from any working directory. It resolves this checkout from the batch file's own location. Menu option 4 previews the exact candidate paths without committing or publishing. The manager stops if local `main` is behind or diverged from remote `main`; it does not stash or merge user changes. A failed menu operation returns a nonzero process exit code after exit.

The `main` policy keeps historical Graphify reports and generated `graph.html` files as engineering evidence. Rebuildable `graphify-out/cache` and Vite `.vite` caches are excluded. Both automatic SonarQube Cloud analysis (`.sonarcloud.properties`) and CI scanner analysis (`sonar-project.properties`) analyze maintained source while excluding historical Engine copies, archives, verification evidence, and local chart state. Test sources are excluded only from duplication measurement. Git retains eligible evidence in `main`; `production` excludes the engineering tree. Check the remote Sonar quality gate after an authorized push.
