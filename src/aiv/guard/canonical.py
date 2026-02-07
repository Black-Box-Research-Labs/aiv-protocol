"""
aiv/guard/canonical.py

Canonical JSON packet validator for AIV Guard.
Validates the structured ``aiv-canonical-json`` block embedded in packets.
"""

from __future__ import annotations

import re
from typing import Any

from .models import (
    GITHUB_BLOB_FULL_SHA,
    HEX_SHA_40_OR_64,
    LINE_ANCHOR,
    MUTABLE_BRANCH_PATTERN,
    GuardContext,
    GuardResult,
)

# Evidence class requirements per risk tier
REQUIRED_CLASSES: dict[str, list[str]] = {
    "R0": ["A", "B"],
    "R1": ["A", "B", "E"],
    "R2": ["A", "B", "C", "E"],
    "R3": ["A", "B", "C", "D", "E", "F"],
}


def _get_path(obj: Any, path: list[str]) -> Any:
    """Safely traverse nested dict by key path."""
    for key in path:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def validate_canonical(
    packet: dict[str, Any],
    ctx: GuardContext,
    result: GuardResult,
    changed_paths: list[str],
) -> bool:
    """
    Validate a canonical JSON packet. Returns True if validation should continue
    (no fatal error), False if a blocking error was found and we should stop.

    Populates ``result`` with findings and rule results.
    """

    # --- Required fields ---
    required_fields = [
        ["aiv_version"],
        ["packet_schema_version"],
        ["identification", "head_sha"],
        ["identification", "pr_id"],
        ["identification", "pr_url"],
        ["identification", "base_sha"],
        ["identification", "created_at"],
        ["identification", "created_by"],
        ["classification", "risk_tier"],
        ["classification", "sod_mode"],
        ["classification", "blast_radius"],
        ["classification", "classification_rationale"],
        ["classification", "classified_by"],
        ["classification", "classified_at"],
        ["claims"],
        ["evidence_items"],
        ["attestations"],
        ["known_limitations"],
    ]

    missing = [".".join(p) for p in required_fields if _get_path(packet, p) is None]

    # CLS-004 is WARN severity (rationale can be missing without blocking)
    cls004_missing = "classification.classification_rationale" in missing
    remaining_missing = [f for f in missing if f != "classification.classification_rationale"]

    if cls004_missing:
        result.add_warn("CLS-004", "classification.classification_rationale must be documented.")

    if remaining_missing:
        result.add_block(
            "CT-001",
            f"Canonical packet missing required fields: {', '.join(remaining_missing)}",
            "Add the missing fields to the aiv-canonical-json block.",
        )
        return False

    # Validate rationale content if present
    rationale = _get_path(packet, ["classification", "classification_rationale"])
    if rationale is not None:
        if not isinstance(rationale, str) or not rationale.strip():
            result.add_warn("CLS-004", "classification.classification_rationale should be a non-empty string.")

    # --- Version checks ---
    if packet.get("aiv_version") != "1.0.0":
        result.add_block("CT-001", f'aiv_version must be "1.0.0" (got: {packet.get("aiv_version")})')
        return False

    if packet.get("packet_schema_version") != "1.0.0":
        got = packet.get("packet_schema_version")
        result.add_block("CT-001", f'packet_schema_version must be "1.0.0" (got: {got})')
        return False

    ident = packet["identification"]

    # --- Identification validation ---
    if not HEX_SHA_40_OR_64.match(ident["head_sha"]):
        result.add_block("CT-005", "identification.head_sha must be a 40- or 64-character hex SHA.")
        return False

    if ident["pr_id"] != ctx.pr_number:
        result.add_block("CT-005", f"identification.pr_id mismatch. Packet: {ident['pr_id']}, PR: {ctx.pr_number}")
        return False

    if not isinstance(ident.get("pr_url"), str) or f"/pull/{ctx.pr_number}" not in ident["pr_url"]:
        result.add_block("CT-005", "identification.pr_url must reference this PR number.")
        return False

    if not HEX_SHA_40_OR_64.match(ident["base_sha"]):
        result.add_block("CT-005", "identification.base_sha must be a 40- or 64-character hex SHA.")
        return False

    if ident["base_sha"].lower() != ctx.base_sha.lower():
        result.add_block("CT-005", f"base_sha mismatch. Packet: {ident['base_sha']}, PR: {ctx.base_sha}")
        return False

    if ident["head_sha"].lower() != ctx.head_sha.lower():
        result.add_block("CT-005", f"head_sha mismatch. Packet: {ident['head_sha']}, PR: {ctx.head_sha}")
        return False

    # --- Classification ---
    cls = packet["classification"]
    risk_tier = cls["risk_tier"]
    if risk_tier not in ("R0", "R1", "R2", "R3"):
        result.add_block("CLS-001", f"risk_tier must be R0/R1/R2/R3 (got: {risk_tier})")
        return False

    result.risk_tier_validated = risk_tier

    sod_mode = cls["sod_mode"]
    if sod_mode not in ("S0", "S1"):
        result.add_block("CLS-003", f"sod_mode must be S0 or S1 (got: {sod_mode})")
        return False

    if risk_tier in ("R2", "R3") and sod_mode != "S1":
        result.add_block("CLS-003", "R2+ requires sod_mode = S1.")
        return False

    # --- Attestations ---
    attestations = packet.get("attestations")
    if not isinstance(attestations, list) or len(attestations) == 0:
        result.add_block("ATT-001", "attestations must be a non-empty array.")
        return False

    att = attestations[0]
    if not _validate_attestation(att, packet, risk_tier, result):
        return False

    # --- Known limitations ---
    kl = packet.get("known_limitations")
    if not isinstance(kl, list) or len(kl) == 0:
        result.add_block("CT-010", "known_limitations must be a non-empty array.")
        return False

    if not all(isinstance(item, str) and item.strip() for item in kl):
        result.add_block("CT-010", "known_limitations entries must be non-empty strings.")
        return False

    # --- Evidence items ---
    evidence_items = packet.get("evidence_items", [])
    if not isinstance(evidence_items, list) or len(evidence_items) == 0:
        result.add_block("CT-001", "evidence_items must be a non-empty array.")
        return False

    claims = packet.get("claims", [])
    if not isinstance(claims, list) or len(claims) == 0:
        result.add_block("CT-001", "claims must be a non-empty array.")
        return False

    claim_ids = {c["id"] for c in claims if isinstance(c, dict) and isinstance(c.get("id"), str)}

    # Validate evidence item references
    for i, item in enumerate(evidence_items):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
            result.add_block("CT-001", f"evidence_items[{i}] is missing a valid id.")
            return False

        refs = item.get("claim_refs", [])
        if not isinstance(refs, list) or len(refs) == 0:
            result.add_block("CT-001", f"evidence_items[{i}] claim_refs must be a non-empty array.")
            return False

        for cref in refs:
            if not isinstance(cref, str) or cref not in claim_ids:
                result.add_block("CT-001", f"evidence_items[{i}] references missing claim: {cref}")
                return False

    evidence_ids = {e["id"] for e in evidence_items if isinstance(e, dict)}

    # Validate claims have evidence refs
    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("id"), str):
            result.add_block("CT-001", "Claim is missing a valid id.")
            return False

        erefs = claim.get("evidence_refs", [])
        if not isinstance(erefs, list) or len(erefs) == 0:
            result.add_block("E-003", f"Claim {claim['id']} must include evidence_refs.")
            return False

        for ref in erefs:
            if ref not in evidence_ids:
                result.add_block("E-003", f"Claim {claim['id']} references missing evidence: {ref}")
                return False

        # Each claim must have Class B evidence
        has_b = any(
            isinstance(ei, dict) and ei.get("id") == ref and ei.get("class") == "B"
            for ref in erefs
            for ei in evidence_items
        )
        if not has_b:
            result.add_block("B-004", f"Claim {claim['id']} must have Class B evidence.")
            return False

    # --- Required evidence classes per tier ---
    required = REQUIRED_CLASSES.get(risk_tier, [])
    for cls_letter in required:
        if not any(e.get("class") == cls_letter for e in evidence_items):
            result.add_block("CT-002", f"Missing required evidence class {cls_letter} for tier {risk_tier}.")
            return False

    # --- Scope inventory validation ---
    if not _validate_scope_inventory(evidence_items, changed_paths, result):
        return False

    # --- Immutability checks on all evidence artifacts ---
    for e in evidence_items:
        if not isinstance(e, dict) or not isinstance(e.get("artifacts"), list):
            continue
        for a in e["artifacts"]:
            if not isinstance(a, dict) or not isinstance(a.get("reference"), str):
                continue
            ref = a["reference"]
            if MUTABLE_BRANCH_PATTERN.search(ref):
                result.add_block(
                    "CT-004",
                    "Evidence artifact references must be immutable (no branch-based blob/tree links).",
                )
                return False

    # --- Class B line anchors for R2+ ---
    if risk_tier in ("R2", "R3"):
        for e in evidence_items:
            if not isinstance(e, dict) or e.get("class") != "B":
                continue
            for a in e.get("artifacts", []):
                if not isinstance(a, dict) or not isinstance(a.get("reference"), str):
                    continue
                ref = a["reference"]
                if GITHUB_BLOB_FULL_SHA.search(ref) and not LINE_ANCHOR.search(ref):
                    result.add_block("B-002", "Class B GitHub permalinks must include line anchors for R2+.")
                    return False

    # --- Class E validation ---
    _validate_class_e(evidence_items, risk_tier, result)

    # --- Class C validation for R2+ ---
    if risk_tier in ("R2", "R3"):
        _validate_class_c(evidence_items, result)

    # --- Falsifiability: claim → test_refs mapping for R2+ ---
    if risk_tier in ("R2", "R3"):
        _validate_claim_test_refs(claims, evidence_items, result)

    return True


def _validate_attestation(att: Any, packet: dict[str, Any], risk_tier: str, result: GuardResult) -> bool:
    """Validate the first attestation entry. Returns False on fatal error."""
    if not isinstance(att, dict):
        result.add_block("ATT-002", "Attestation must be an object.")
        return False

    required_str_fields = ["id", "verifier_id", "verifier_identity_type", "signature_method"]
    for f in required_str_fields:
        if not isinstance(att.get(f), str) or not att[f].strip():
            result.add_block("ATT-002", f"Attestation {f} is required.")
            return False

    ts = att.get("timestamp")
    if not isinstance(ts, str):
        result.add_block("ATT-002", "Attestation timestamp must be valid ISO-8601.")
        return False

    for arr_field in ("evidence_classes_validated", "validation_rules_checked"):
        val = att.get(arr_field)
        if not isinstance(val, list) or len(val) == 0:
            result.add_block("ATT-002", f"Attestation {arr_field} must be a non-empty array.")
            return False

    if not isinstance(att.get("findings"), list):
        result.add_block("ATT-002", "Attestation findings must be present (may be empty).")
        return False

    if att["signature_method"] != "unsigned":
        if not isinstance(att.get("signature"), str) or not att["signature"].strip():
            result.add_block("ATT-002", "Signed attestation requires signature field.")
            return False
        if not isinstance(att.get("signed_fields"), list) or len(att["signed_fields"]) == 0:
            result.add_block("ATT-002", "Signed attestation requires signed_fields array.")
            return False

    # SoD check
    if risk_tier in ("R2", "R3"):
        created_by = _get_path(packet, ["identification", "created_by"])
        if att["verifier_id"] == created_by:
            result.add_block("CLS-003", "R2+ requires verifier_id to differ from created_by (SoD).")
            return False

    # Decision validation
    decision = att.get("decision")
    if decision not in ("COMPLIANT", "CONDITIONAL", "NON-COMPLIANT"):
        result.add_block("CT-008", f"Invalid attestation decision: {decision}")
        return False

    if decision == "NON-COMPLIANT":
        if not isinstance(att.get("blocking_findings"), list) or len(att["blocking_findings"]) == 0:
            result.add_block("ATT-002", "NON-COMPLIANT decisions require blocking_findings.")
            return False
        if not isinstance(att.get("rationale"), str) or not att["rationale"].strip():
            result.add_block("ATT-002", "NON-COMPLIANT decisions require rationale.")
            return False
        result.add_block("G-006", "Attestation decision is NON-COMPLIANT.")
        return False

    if decision == "CONDITIONAL":
        if not _validate_conditional_decision(att, result):
            return False

    return True


def _validate_conditional_decision(att: dict[str, Any], result: GuardResult) -> bool:
    """Validate CONDITIONAL attestation requirements."""
    findings = att.get("findings", [])
    has_block = any(isinstance(f, dict) and f.get("severity") == "BLOCK" for f in findings)
    if has_block:
        result.add_block("ATT-004", "CONDITIONAL decision MUST NOT bypass BLOCK-severity findings.")
        return False

    warn_findings = [
        f
        for f in findings
        if isinstance(f, dict) and f.get("severity") == "WARN" and isinstance(f.get("id"), str) and f["id"].strip()
    ]
    if len(warn_findings) == 0:
        result.add_block("CT-009", "CONDITIONAL decisions must include at least one WARN finding.")
        return False

    conditions = att.get("conditions", [])
    if not isinstance(conditions, list) or len(conditions) == 0:
        result.add_block("CT-009", "CONDITIONAL decision requires non-empty conditions array.")
        return False

    warn_ids = {f["id"] for f in warn_findings}
    for c in conditions:
        if not isinstance(c, dict):
            continue
        fid = c.get("finding_id", "")
        if isinstance(fid, str) and fid.strip() and fid not in warn_ids:
            result.add_block("CT-009", "CONDITIONAL conditions must reference WARN findings only.")
            return False

    for wid in warn_ids:
        if not any(isinstance(c, dict) and c.get("finding_id") == wid for c in conditions):
            result.add_block("CT-009", "Remediation condition required for each WARN finding.")
            return False

    # Validate condition fields
    for c in conditions:
        if not isinstance(c, dict):
            continue
        for req_field in ("finding_id", "remediation_plan", "responsible_party", "remediation_deadline"):
            val = c.get(req_field)
            if not isinstance(val, str) or not val.strip():
                result.add_block("CT-009", f"CONDITIONAL condition must include {req_field}.")
                return False

    return True


def _validate_scope_inventory(
    evidence_items: list[dict[str, Any]],
    changed_paths: list[str],
    result: GuardResult,
) -> bool:
    """Validate scope inventory matches PR diff."""
    scope = _read_scope_inventory(evidence_items, result)
    if scope is None:
        result.add_block("B-003", "Must include Class B scope inventory evidence.")
        return False

    changed_set = set(changed_paths)
    inv_set = {p.strip() for p in scope if isinstance(p, str) and p.strip()}

    missing = [p for p in changed_paths if p not in inv_set]
    extra = [p for p in inv_set if p not in changed_set]

    if missing or extra:
        result.add_block(
            "B-003",
            f"Scope inventory mismatch. Missing: {', '.join(missing[:25])} | Extra: {', '.join(extra[:25])}",
        )
        return False

    return True


def _read_scope_inventory(evidence_items: list[dict[str, Any]], result: GuardResult) -> list[str] | None:
    """Extract scope inventory from Class B evidence items."""
    import base64

    for e in evidence_items:
        if not isinstance(e, dict) or e.get("class") != "B":
            continue
        for a in e.get("artifacts", []):
            if not isinstance(a, dict) or a.get("type") != "scope_inventory":
                continue
            ref = a.get("reference", "")
            if not isinstance(ref, str):
                continue

            if ref.startswith("inline-b64-json:"):
                try:
                    payload = ref[len("inline-b64-json:") :]
                    decoded = base64.b64decode(payload).decode("utf-8")
                    parsed = __import__("json").loads(decoded)
                    return parsed if isinstance(parsed, list) else None
                except Exception:
                    result.add_block("B-003", "scope_inventory inline-b64-json could not be decoded.")
                    return None

            if ref.startswith("inline-json:"):
                try:
                    payload = ref[len("inline-json:") :]
                    parsed = __import__("json").loads(payload)
                    return parsed if isinstance(parsed, list) else None
                except Exception:
                    result.add_block("B-003", "scope_inventory inline-json could not be parsed.")
                    return None

            if ref.startswith("inline-lines:"):
                payload = ref[len("inline-lines:") :]
                return [p.strip() for p in payload.split("\n") if p.strip()]

    return None


def _validate_class_e(evidence_items: list[dict[str, Any]], risk_tier: str, result: GuardResult) -> None:
    """Validate Class E evidence items (requirement references, checklists)."""
    class_e = [e for e in evidence_items if isinstance(e, dict) and e.get("class") == "E"]

    for e in class_e:
        artifacts = e.get("artifacts", [])
        req_ref = next(
            (a for a in artifacts if isinstance(a, dict) and a.get("type") == "requirement_reference"),
            None,
        )
        if not req_ref or not isinstance(req_ref.get("reference"), str) or not req_ref["reference"].strip():
            result.add_block("E-001", f"requirement_reference artifact required for Class E: {e.get('id')}")
            return

        ref = req_ref["reference"].strip()
        is_sha_permalink = bool(GITHUB_BLOB_FULL_SHA.search(ref))

        # Check for mutable URL
        if re.match(r"^https?://", ref, re.IGNORECASE) and not is_sha_permalink:
            if risk_tier == "R3":
                result.add_block("E-001", "Requirement reference must be immutable for R3.")
                return
            result.add_warn(
                "E-001",
                f"Requirement reference appears to be a mutable URL for Class E: {e.get('id')}",
            )

        # Acceptance checklist
        checklist = next(
            (a for a in artifacts if isinstance(a, dict) and a.get("type") == "acceptance_checklist"),
            None,
        )
        if not checklist or not isinstance(checklist.get("reference"), str):
            result.add_warn("E-004", f"Acceptance checklist missing for Class E: {e.get('id')}")


def _validate_class_c(evidence_items: list[dict[str, Any]], result: GuardResult) -> None:
    """Validate Class C evidence items for R2+."""
    class_c = [e for e in evidence_items if isinstance(e, dict) and e.get("class") == "C"]

    # validation_method must be non-empty
    if class_c and not all(
        isinstance(e.get("validation_method"), str) and e["validation_method"].strip() for e in class_c
    ):
        result.add_block("C-002", "Class C validation_method MUST be documented and non-empty.")
        return

    # At least one must indicate semantic analysis
    semantic_re = re.compile(r"\b(ast|coverage|collect|junit|json)\b", re.IGNORECASE)
    if not any(
        isinstance(e.get("validation_method"), str) and semantic_re.search(e["validation_method"]) for e in class_c
    ):
        result.add_block("C-004", "MUST include at least one Class C semantic analysis method.")


def _validate_claim_test_refs(
    claims: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    result: GuardResult,
) -> None:
    """CT-013: R2+ claims with Class A evidence must include test_refs.

    Falsifiability enforcement: a claim is only verifiable if it maps
    to specific, named tests that exercise the claimed behaviour.
    """
    # Build set of Class A evidence IDs
    class_a_ids = {
        e["id"]
        for e in evidence_items
        if isinstance(e, dict) and e.get("class") == "A" and isinstance(e.get("id"), str)
    }

    # Collect known test IDs from Class A test_list arrays
    known_test_ids: set[str] = set()
    for e in evidence_items:
        if not isinstance(e, dict) or e.get("class") != "A":
            continue
        tl = e.get("test_list", [])
        if isinstance(tl, list):
            known_test_ids.update(t for t in tl if isinstance(t, str))

    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("id"), str):
            continue

        erefs = claim.get("evidence_refs", [])
        has_class_a = any(ref in class_a_ids for ref in erefs if isinstance(ref, str))

        if not has_class_a:
            continue

        test_refs = claim.get("test_refs", [])
        if not isinstance(test_refs, list) or len(test_refs) == 0:
            result.add_warn(
                "CT-013",
                f"Claim {claim['id']} uses Class A evidence but provides no test_refs. "
                f"Map this claim to specific test(s) for falsifiability.",
            )
            continue

        if known_test_ids:
            for t_id in test_refs:
                if isinstance(t_id, str) and t_id not in known_test_ids:
                    result.add_warn(
                        "CT-013",
                        f"Claim {claim['id']} references unknown test_id: {t_id}. "
                        f"Ensure test_id matches an entry in the Class A test_list.",
                    )
