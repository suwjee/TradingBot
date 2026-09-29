@{
  Main = @{
    IncludedPathPatterns = @(
      'apps/chart/state/data/raw/BaseLine/**'
    )
    ExcludedPathPatterns = @(
      'apps/chart/node_modules/**',
      'apps/chart/dist/**',
      'apps/chart/state/cache/**',
      'apps/chart/state/secret/**',
      'apps/chart/state/tmp/**',
      'apps/chart/state/data/raw/**',
      'engineering/archive/repository-graphify/cache/**',
      'engineering/archive/repository-graphify/**/cache/**',
      'engineering/archive/repository-graphify/**/last_query_stamp',
      'engineering/archive/docs/validation-temp/**',
      'engineering/verification/**/runtime-server.*',
      '**/__pycache__/**',
      '**/*.pyc',
      '**/.pytest_cache/**',
      '**/.mypy_cache/**',
      '**/.ruff_cache/**',
      '**/*.egg-info/**',
      '**/.coverage',
      '**/coverage/**',
      '**/htmlcov/**',
      '**/.benchmarks/**',
      '**/.cache/**',
      '**/*.tmp',
      '**/*.temp',
      '**/*.bak',
      '**/*.pid',
      '**/.venv/**',
      '**/venv/**',
      '**/env/**',
      '**/.env',
      '**/.env.*',
      '**/.idea/**',
      '**/.vscode/**',
      '**/.DS_Store',
      '**/Thumbs.db',
      '**/Desktop.ini',
      '**/.worktrees/**',
      '**/.superpowers/**'
    )
    MeaningfulRoots = @(
      'apps/chart/tests/',
      'engine/tests/',
      'engineering/',
      'apps/chart/state/data/raw/BaseLine/'
    )
  }
  Sensitive = @{
    PathPatterns = @(
      '**/apps/chart/state/secret/**',
      '**/*.pem',
      '**/*.key',
      '**/id_rsa',
      '**/.env',
      '**/.env.*'
    )
    ContentPatterns = @(
      '-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
      '\bgh[pousr]_[A-Za-z0-9_]{20,}\b',
      '\bgithub_pat_[A-Za-z0-9_]{20,}\b',
      '\bAKIA[0-9A-Z]{16}\b'
    )
    MaximumScanBytes = 1048576
  }
  Production = @{
    MandatoryPaths = @(
      'scripts/launch.bat',
      'scripts/start.ps1',
      'apps/chart/package.json',
      'apps/chart/package-lock.json',
      'apps/chart/vite.config.js',
      'apps/chart/index.html',
      'apps/chart/review.html',
      'apps/chart/scripts/dev-server.mjs',
      'engine/__init__.py',
      'engine/pipeline/__init__.py',
      'engine/bridge/trading_pipeline.py',
      'engine/pipeline/reaction_engine.py',
      'engine/pipeline/blue_line_detector.py',
      'engine/pipeline/a_zone_detector.py',
      'engine/pipeline/s_zone_detector.py',
      'engine/pipeline/e_zone_detector.py',
      'engine/pipeline/lifecycle_engine.py'
    )
    RuntimeRoots = @(
      'apps/chart/src/',
      'apps/chart/server/',
      'apps/chart/scripts/',
      'engine/bridge/',
      'engine/pipeline/'
    )
    ExcludedPathPatterns = @(
      'apps/chart/state/**',
      'apps/chart/tests/**',
      'engine/tests/**',
      'apps/chart/node_modules/**',
      'apps/chart/dist/**',
      'engineering/**',
      'scripts/git/**',
      'docs/**',
      'engine/bridge/__init__.py',
      'apps/chart/server/raw-integrity.js',
      '**/__pycache__/**',
      '**/*.pyc'
    )
  }
}
