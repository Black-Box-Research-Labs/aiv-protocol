"""
tests/conftest.py

Shared test fixtures and utilities.
"""

import pytest


# ============================================================================
# Valid Packet Fixtures
# ============================================================================

@pytest.fixture
def valid_minimal_packet():
    """Minimal valid packet meeting all requirements."""
    return """
# AIV Verification Packet (v2.1)

## 0. Intent Alignment (Mandatory)
- **Class E Evidence:** [Task #123](https://github.com/owner/repo/blob/abc123def456/docs/spec.md)
- **Verifier Check:** This PR implements the feature described in the linked spec.

## 1. Claim: Implements new API endpoint
- **Evidence Class:** A (Execution)
- **Evidence Artifact:** [CI Run](https://github.com/owner/repo/actions/runs/12345)
- **Reproduction:** CI Automation

---
_This packet certifies that all claims are supported by the linked, reproducible evidence._
"""


@pytest.fixture
def valid_full_packet():
    """Comprehensive packet with all evidence classes."""
    return """
# AIV Verification Packet (v2.1)

## 0. Intent Alignment (Mandatory)
- **Class E Evidence:** [Issue #42](https://github.com/owner/repo/blob/a1b2c3d/docs/requirements.md#feature-x)
- **Verifier Check:** Fixes the bug described in Issue #42 where login fails for SSO users.

## 1. Claim: Fixed SSO authentication flow
- **Evidence Class:** A (Execution)
- **Evidence Artifact:** [CI Run #9876](https://github.com/owner/repo/actions/runs/9876543)
- **Reproduction:** CI Automation

## 2. Claim: Added regression test for SSO edge case
- **Evidence Class:** B (Referential)
- **Evidence Artifact:** [test_sso.py:45-67](https://github.com/owner/repo/blob/a1b2c3d/tests/test_sso.py#L45-L67)
- **Reproduction:** N/A (Static Code)

## 3. Claim: No existing tests were modified or deleted
- **Evidence Class:** F (Conservation)
- **Evidence Artifact:** [Test diff](https://github.com/owner/repo/pull/123/files#diff-tests)
- **Reproduction:** See CI artifact
- **Justification:** Only additions; all existing assertions preserved.

---
_This packet certifies that all claims are supported by the linked, reproducible evidence._
"""


# ============================================================================
# Invalid Packet Fixtures
# ============================================================================

@pytest.fixture
def invalid_missing_header():
    """Packet without required header."""
    return """
## 0. Intent Alignment
- **Class E Evidence:** [Link](https://example.com)
"""


@pytest.fixture
def invalid_mutable_link():
    """Packet with mutable (non-SHA) link."""
    return """
# AIV Verification Packet (v2.1)

## 0. Intent Alignment (Mandatory)
- **Class E Evidence:** [Spec](https://github.com/owner/repo/blob/main/docs/spec.md)
- **Verifier Check:** This PR implements the spec.

## 1. Claim: Did something useful here
- **Evidence Class:** A
- **Evidence Artifact:** [Link](https://github.com/owner/repo/actions/runs/99999)
- **Reproduction:** N/A
"""


@pytest.fixture
def invalid_manual_reproduction():
    """Packet with Zero-Touch violation."""
    return """
# AIV Verification Packet (v2.1)

## 0. Intent Alignment (Mandatory)
- **Class E Evidence:** [Task](https://github.com/owner/repo/blob/abc123def/docs/task.md)
- **Verifier Check:** Implements the task described in the linked document.

## 1. Claim: Feature works correctly now
- **Evidence Class:** A
- **Evidence Artifact:** Screenshot attached
- **Reproduction:** git clone repo && cd repo && npm install && npm run dev && open browser and click login
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
