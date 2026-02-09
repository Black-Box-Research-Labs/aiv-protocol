---
description: How to commit code changes using the AIV protocol (evidence-based verification)
---

# AIV Commit Workflow

This project uses the AIV Protocol for evidence-based code verification. Every code change must go through `aiv commit`, which collects proof that the change was verified.

## Before You Start

Make sure AIV is initialized: `aiv init`

## Workflow

### 1. Start a tracked change (for multi-file changes)

```bash
aiv begin <change-name> --description "<what this change does>"
```

Example:
```bash
aiv begin auth-fix --description "Handle expired JWT tokens"
```

### 2. Stage your file, then commit with evidence

```bash
git add <file>
aiv commit <file> \
    -m "<conventional commit message>" \
    -t R1 \
    -c "<falsifiable claim about what changed>" \
    -i "<URL to issue/spec/directive>" \
    --requirement "<which requirement the URL satisfies>" \
    -r "<why this risk tier was chosen>" \
    -s "<one-line summary>"
```

**Important rules:**
- `-c` claims must be **falsifiable**: `"TokenValidator rejects expired tokens with 401"` NOT `"Fixed auth bug"`
- `-i` must be a **URL** (https://...), not plain text
- `-t` risk tier: R0 (trivial), R1 (default, low), R2 (medium), R3 (high/critical)
- You can repeat `-c` for multiple claims
- R1+ commits are **blocked** if >50% of claims lack test coverage. Use `--force "justification"` to override.
- `--skip-checks` is only allowed for R0 (formatting, docs, comments)

### 3. Repeat step 2 for each file in the change

### 4. Close the change (generates Layer 2 verification packet)

```bash
aiv close --requirement "<which requirement this change satisfies>"
```

### 5. Push

```bash
git push
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `aiv begin <name>` | Start tracking a multi-file change |
| `aiv commit <file>` | Commit with evidence collection |
| `aiv status` | Show current change progress |
| `aiv close` | Generate verification packet and close change |
| `aiv abandon` | Discard change without packet |
| `aiv quickstart` | Print full workflow reference |
| `aiv audit` | Check all evidence files for quality issues |

## Risk Tier Guide

| Tier | Use When | Evidence |
|------|----------|----------|
| R0 | Docs, comments, formatting | Scope only (--skip-checks allowed) |
| R1 | Bug fixes, minor refactors | Class A (tests) + B (refs) + E (intent) |
| R2 | API changes, config, deps | + Class C (anti-cheat) + F (provenance) |
| R3 | Auth, crypto, payments, PII | + Class D (differential). Blocks on ANY unverified claim. |
