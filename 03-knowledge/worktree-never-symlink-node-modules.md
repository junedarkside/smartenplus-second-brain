---
name: worktree-never-symlink-node-modules
description: When building a git worktree for verification, give it its own npm ci — never symlink the main repo's node_modules. Main node_modules was found empty mid-build 2026-09-30, cause unknown.
type: knowledge-atom
date: 2026-09-30
parent: 06-systems
---

# Worktrees: Own `node_modules`, Never a Symlink

## Summary
To verify a branch with a production build without disturbing the running dev server, a scratch `git worktree` is used. Symlinking the main repo's `node_modules` into it saves an install but couples the two trees: anything that cleans or rewrites `node_modules` from the worktree hits the main repo.

## What happened (#439)
During a `next build` in a worktree whose `node_modules` was a symlink, the **main** repo's `node_modules` ended up empty (build crashed with `Cannot find module './impl'` inside `next`). No install was running, it isn't git-tracked, and the same setup had built fine minutes earlier — root cause never confirmed. The running dev server kept working from memory only. Restored with `npm ci`.

## Rule
```bash
git worktree add --detach <scratch>/wt <commit>
cp .env.local <scratch>/wt/
(cd <scratch>/wt && npm ci)      # ~30-40s, fully isolated
```
If a symlink is ever used, remove it with `unlink` (never `rm -r`). Run `next start -p 3001` from the worktree so dev on :3000 is untouched.

## Related
- [[nextjs-dev-stale-module-cache]]
