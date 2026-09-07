# Git workflow

1. Run `git status --short` before editing; this repository is already dirty.
2. Preserve unrelated changes and use narrowly scoped patches.
3. Verify the change in proportion to its risk, then inspect its final diff.
4. Stage only explicit owned paths. Never use broad staging in this worktree.
5. Use a cohesive Conventional Commit only when the user asks to commit.
6. Push only when explicitly authorized or when the user has established that
   automatic pushes are authorized for this repository. Never force-push.

The configured remote is `origin` for `https://github.com/suwjee/TradingBot.git`.
Remote configuration is not authorization to publish by itself.
