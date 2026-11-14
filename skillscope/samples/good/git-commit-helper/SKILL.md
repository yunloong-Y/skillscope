---
name: git-commit-helper
description: "Use when the user asks to write or review a Conventional Commit message. Turns a staged diff into one scoped, single-purpose commit line."
version: 1.0.0
allowed-tools: Bash,Read
---

# Git Commit Helper

Read the staged diff, then produce exactly one commit message.

## Rules

- One logical change per commit. Split mixed diffs instead of describing them together.
- Format: `type(scope): description`, lowercase scope, no trailing period.
- Never commit generated files, local caches, or credential files.

## Example

```bash
git diff --staged
# -> feat(chat): keep draft text when the socket reconnects
```

No account, API key or network access is required to try this.
