"""
tests/conftest.py

Shared test fixtures and utilities.

All packet fixtures use the ACTUAL template format from
.github/aiv-packets/VERIFICATION_PACKET_TEMPLATE.md:
- ## Claim(s) with numbered list items
- ## Evidence with ### Class E/B/A/C subsections
"""

import pytest


# ============================================================================
# Valid Packet Fixtures
# ============================================================================

@pytest.fixture
def valid_minimal_packet():
    """Minimal valid packet meeting all requirements."""
    return """\
# AIV Verification Packet (v2.1)

**Commit:** `abc1234`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

## Claim(s)

1. Implements new API endpoint for user authentication per spec Section 3.2.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Task #123](https://github.com/owner/repo/blob/abc123def456/docs/spec.md)
- **Requirements Verified:**
  1. API endpoint returns 200 for valid credentials
  2. API endpoint returns 401 for invalid credentials

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/auth.py` (45 lines)

### Class A (Execution Evidence)

- [CI Run #12345](https://github.com/owner/repo/actions/runs/12345) — all tests pass

---

## Summary

New API endpoint for user authentication.
"""


@pytest.fixture
def valid_full_packet():
    """Comprehensive packet with multiple claims and evidence classes."""
    return """\
# AIV Verification Packet (v2.1)

**Commit:** `a1b2c3d`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "SSO authentication fix affecting login flow."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:00:00Z"
```

## Claim(s)

1. Implemented SSO authentication flow to handle SAML response edge case.
2. Added regression test for SSO edge case covering the SAML response parsing.
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Issue #42](https://github.com/owner/repo/blob/a1b2c3d/docs/requirements.md#feature-x)
- **Requirements Verified:**
  1. SSO login succeeds for SAML users
  2. Error handling for malformed SAML responses

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/auth/sso.py` (120 lines)
- Modified:
  - `src/auth/login.py` (5 lines changed)

**Claim 1: SSO fix**
- [`sso.py#L45-L67`](https://github.com/owner/repo/blob/a1b2c3d/src/auth/sso.py#L45-L67) — SAML response parser

**Claim 2: Regression test**
- [`test_sso.py#L10-L30`](https://github.com/owner/repo/blob/a1b2c3d/tests/test_sso.py#L10-L30) — new test case

### Class A (Execution Evidence)

- [CI Run #9876](https://github.com/owner/repo/actions/runs/9876543) — 42 passed, 0 failed

### Class C (Negative Evidence)

**Claim 3: No regressions**
- No existing tests modified or deleted.
- Full regression suite passed in CI.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

SSO authentication fix with regression test coverage.
"""


# ============================================================================
# Invalid Packet Fixtures
# ============================================================================

@pytest.fixture
def invalid_missing_header():
    """Packet without required header."""
    return """\
## Claim(s)

1. Some claim that should fail because there is no header.

## Evidence

### Class E (Intent Alignment)

- **Link:** [Link](https://example.com)
"""


@pytest.fixture
def invalid_mutable_link():
    """Packet with mutable (non-SHA) Class E link."""
    return """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Did something useful here that should be verified by the linked spec.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/owner/repo/blob/main/docs/spec.md)
- **Requirements Verified:**
  1. Implements the spec requirements

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/feature.py`

---

## Summary

Feature implementation.
"""


@pytest.fixture
def invalid_manual_reproduction():
    """Packet with Zero-Touch violation in reproduction instructions."""
    return """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Feature works correctly now after fixing the authentication flow.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Task](https://github.com/owner/repo/blob/abc123def/docs/task.md)
- **Requirements Verified:**
  1. Authentication flow works for all user types

### Class A (Execution Evidence)

- **Reproduction:** git clone repo && cd repo && npm install && npm run dev && open browser and click login

---

## Summary

Feature fix.
"""


# ============================================================================
# Diff Fixtures
# ============================================================================

@pytest.fixture
def diff_with_deleted_assertion():
    """Git diff that deletes an assertion."""
    return """\
diff --git a/tests/test_auth.py b/tests/test_auth.py
index abc123..def456 100644
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -10,7 +10,6 @@ def test_login():
     user = login("test@example.com", "password")
     assert user is not None
-    assert user.is_authenticated
     assert user.email == "test@example.com"
"""


@pytest.fixture
def diff_with_skip_decorator():
    """Git diff that adds a skip decorator."""
    return """\
diff --git a/tests/test_payment.py b/tests/test_payment.py
index abc123..def456 100644
--- a/tests/test_payment.py
+++ b/tests/test_payment.py
@@ -5,6 +5,7 @@ import pytest
 from app.payment import process_payment


+@pytest.mark.skip(reason="Flaky test - fix later")
 def test_process_payment_success():
     result = process_payment(100, "USD")
     assert result.success
"""


@pytest.fixture
def diff_clean():
    """Git diff with no anti-cheat violations."""
    return """\
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,6 +10,10 @@ def login(email, password):
     user = find_user(email)
     if not user:
         return None
+
+    # SSO handling
+    if is_sso_user(user):
+        return sso_login(user)

     if verify_password(user, password):
         return user
"""
