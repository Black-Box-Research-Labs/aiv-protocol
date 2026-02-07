# AIV Verification Packet (v2.1)

## Classification

```yaml
classification:
  risk_tier: R1
  blast_radius: component
  sod_mode: S0
  critical_surfaces: []
  classification_rationale: "Adds optional E021 link vitality checking to LinkValidator. HTTP HEAD requests verify evidence URLs are reachable. Opt-in via --audit-links flag — default validation unchanged."
  classified_by: "cascade-ai"
  classified_at: "2026-02-07T08:00:00Z"
```

## Claim(s)

1. `LinkValidator` sends HTTP HEAD requests to all evidence URLs when `audit_links=True`, reporting E021 BLOCK for 4xx/5xx responses and E021 WARN for network errors.
2. Default behavior (`audit_links=False`) is unchanged — no network calls, no E021 findings.
3. Duplicate URLs are checked exactly once regardless of how many times they appear in the packet.

## Evidence

### Class E (Intent Alignment)

- **Directive:** External critique identified that the link validator checks URL syntax (SHA-pinned format) but never verifies reachability. A typo in a SHA passes all checks but 404s in reality. This closes that gap with an opt-in network check.

### Class B (Referential Evidence)

**Scope Inventory**
- Modified: `src/aiv/lib/validators/links.py` — added `_check_link_vitality()`, `_head_check()` methods and `audit_links` constructor param (~80 new lines).

### Class A (Execution Evidence)

- 6 new unit tests in `tests/unit/test_validators.py::TestLinkVitality`:
  - `test_audit_links_off_skips_network` — default produces no E021
  - `test_audit_links_404_blocks` — HTTP 404 produces E021 BLOCK
  - `test_audit_links_200_passes` — HTTP 200 produces no E021
  - `test_audit_links_network_error_warns` — URLError produces E021 WARN
  - `test_audit_links_403_blocks` — HTTP 403 produces E021 BLOCK
  - `test_audit_links_deduplicates_urls` — same URL checked exactly once
- 436/436 tests pass (430 pre-existing + 6 new).

## Summary

Adds E021 link vitality checking to the validation pipeline — opt-in via `--audit-links` flag on `aiv check`. Turns the link validator from a spell-checker into a fact-checker.
