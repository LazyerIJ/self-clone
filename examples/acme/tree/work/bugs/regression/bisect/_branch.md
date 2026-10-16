---
kind: branch
title: Bisect to the culprit
state: growing
checked: 2026-10-14
---
## What
Find the commit that broke it before deciding anything.

## Boundary
Split by **where it reproduces**: on the laptop · only in CI.

## Evidence
- `~/.zsh_history` (git bisect run, 31 times)
