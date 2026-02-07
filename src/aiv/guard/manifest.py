"""
aiv/guard/manifest.py

Evidence artifact manifest validators for AIV Guard.
Validates class_a_execution.json, class_c_negative.json,
test_integrity_semantic.json, and durable_storage_oci.json.
"""

from __future__ import annotations

import re
from typing import Any


def _is_non_empty_str(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _is_int(v: Any) -> bool:
    return isinstance(v, int)


def validate_class_a_manifest(
    manifest: dict[str, Any],
    pr_head_sha: str,
    repo: str,
) -> list[str]:
    """
    Validate class_a_execution.json manifest.
    Returns list of error strings (empty = pass).
    """
    errors: list[str] = []

    if manifest.get("schema_version") != "1.0.0":
        errors.append("class_a_execution.json.schema_version must be 1.0.0")

    head = manifest.get("head_sha", "")
    if not _is_non_empty_str(head):
        errors.append("class_a_execution.json.head_sha must be non-empty")
    elif pr_head_sha and head.lower() != pr_head_sha.lower():
        errors.append(f"class_a_execution.json.head_sha mismatch (manifest={head}, pr={pr_head_sha})")

    run = manifest.get("run")
    if not isinstance(run, dict):
        errors.append("class_a_execution.json.run must be an object")
    else:
        if repo and run.get("repository") != repo:
            got_repo = run.get("repository")
            errors.append(f"class_a_execution.json.run.repository mismatch (got={got_repo}, expected={repo})")
        if not _is_non_empty_str(run.get("run_id", "")):
            errors.append("class_a_execution.json.run.run_id must be non-empty")

    env = manifest.get("execution_environment")
    if not isinstance(env, dict):
        errors.append("class_a_execution.json.execution_environment must be an object")
    else:
        os_info = env.get("os")
        if (
            not isinstance(os_info, dict)
            or not _is_non_empty_str(os_info.get("name", ""))
            or not _is_non_empty_str(os_info.get("release", ""))
        ):
            errors.append("class_a_execution.json.execution_environment.os must include name and release")
        # Accept either Node (node+npm) or Python (python) runtime identifiers
        has_node = _is_non_empty_str(env.get("node", ""))
        has_python = _is_non_empty_str(env.get("python", ""))
        if not has_node and not has_python:
            errors.append(
                "class_a_execution.json.execution_environment must include a runtime "
                "(python or node)"
            )

    tr = manifest.get("test_results")
    if not isinstance(tr, dict):
        errors.append("class_a_execution.json.test_results must be an object")
    else:
        for k in ("pass", "fail", "skip"):
            if not _is_int(tr.get(k)):
                errors.append(f"class_a_execution.json.test_results.{k} must be an integer")

    tl = manifest.get("test_list")
    if not isinstance(tl, list) or len(tl) == 0:
        errors.append("class_a_execution.json.test_list must be a non-empty array")

    checks = manifest.get("executed_checks")
    if not isinstance(checks, list) or len(checks) == 0:
        errors.append("class_a_execution.json.executed_checks must be a non-empty array")

    return errors


def validate_class_c_manifest(
    manifest: dict[str, Any],
    pr_head_sha: str,
) -> list[str]:
    """
    Validate class_c_negative.json manifest.
    Returns list of error strings (empty = pass).
    """
    errors: list[str] = []

    if manifest.get("schema_version") != "1.0.0":
        errors.append("class_c_negative.json.schema_version must be 1.0.0")

    head = manifest.get("head_sha", "")
    if not _is_non_empty_str(head):
        errors.append("class_c_negative.json.head_sha must be non-empty")
    elif pr_head_sha and head.lower() != pr_head_sha.lower():
        errors.append(f"class_c_negative.json.head_sha mismatch (manifest={head}, pr={pr_head_sha})")

    sm = manifest.get("search_method")
    if not isinstance(sm, dict):
        errors.append("class_c_negative.json.search_method must be an object")
    else:
        if not _is_non_empty_str(sm.get("tool", "")):
            errors.append("class_c_negative.json.search_method.tool must be non-empty")
        if sm.get("deterministic") is not True:
            errors.append("class_c_negative.json.search_method.deterministic must be true")

    scope = manifest.get("search_scope")
    if not isinstance(scope, list) or len(scope) == 0:
        errors.append("class_c_negative.json.search_scope must be a non-empty array")

    patterns = manifest.get("patterns")
    if not isinstance(patterns, list) or len(patterns) == 0:
        errors.append("class_c_negative.json.patterns must be a non-empty array")

    if manifest.get("search_results_artifact") != "negative_evidence.txt":
        errors.append("class_c_negative.json.search_results_artifact must equal negative_evidence.txt")

    ti = manifest.get("test_integrity")
    if not isinstance(ti, dict) or ti.get("machine_readable") is not True:
        errors.append("class_c_negative.json.test_integrity.machine_readable must be true")
    elif isinstance(ti, dict):
        ref = ti.get("required_evidence_files")
        if not isinstance(ref, list) or len(ref) == 0:
            errors.append("class_c_negative.json.test_integrity.required_evidence_files must be a non-empty array")
        if ti.get("semantic_report_artifact") != "test_integrity_semantic.json":
            errors.append(
                "class_c_negative.json.test_integrity.semantic_report_artifact must equal test_integrity_semantic.json"
            )
        method = ti.get("method")
        if not _is_non_empty_str(method) or "semantic" not in str(method).lower():
            errors.append("class_c_negative.json.test_integrity.method must indicate semantic analysis")

    return errors


def validate_semantic_manifest(
    manifest: dict[str, Any],
    pr_head_sha: str,
    pr_base_sha: str,
) -> list[str]:
    """
    Validate test_integrity_semantic.json manifest.
    Returns list of error strings (empty = pass).
    """
    errors: list[str] = []

    if manifest.get("schema_version") != "1.0.0":
        errors.append("test_integrity_semantic.json.schema_version must be 1.0.0")

    head = manifest.get("head_sha", "")
    if not _is_non_empty_str(head):
        errors.append("test_integrity_semantic.json.head_sha must be non-empty")
    elif pr_head_sha and head.lower() != pr_head_sha.lower():
        errors.append(f"test_integrity_semantic.json.head_sha mismatch (report={head}, pr={pr_head_sha})")

    report_base = manifest.get("base_sha", "")
    if _is_non_empty_str(pr_base_sha) and _is_non_empty_str(report_base):
        if pr_base_sha.lower() != report_base.lower():
            errors.append(f"test_integrity_semantic.json.base_sha mismatch (report={report_base}, pr={pr_base_sha})")

    if manifest.get("overall_result") != "PASS":
        errors.append("test_integrity_semantic.json.overall_result must be PASS")

    return errors


def validate_durable_manifest(
    manifest: dict[str, Any],
    pr_head_sha: str,
) -> list[str]:
    """
    Validate durable_storage_oci.json manifest.
    Returns list of error strings (empty = pass).
    """
    errors: list[str] = []

    if manifest.get("schema_version") != "1.0.0":
        errors.append("durable_storage_oci.json.schema_version must be 1.0.0")

    head = manifest.get("head_sha", "")
    if not _is_non_empty_str(head):
        errors.append("durable_storage_oci.json.head_sha must be non-empty")
    elif pr_head_sha and head.lower() != pr_head_sha.lower():
        errors.append(f"durable_storage_oci.json.head_sha mismatch (metadata={head}, pr={pr_head_sha})")

    if manifest.get("backend") != "ghcr_oci":
        errors.append("durable_storage_oci.json.backend must be ghcr_oci")

    if manifest.get("export_result") != "SUCCESS":
        errors.append("durable_storage_oci.json.export_result must be SUCCESS")

    digest = manifest.get("digest", "")
    if not _is_non_empty_str(digest):
        errors.append("durable_storage_oci.json.digest must be non-empty")
    elif not re.fullmatch(r"sha256:[0-9a-f]{64}", digest.strip().lower()):
        errors.append("durable_storage_oci.json.digest must match sha256:<64 hex>")

    oci_ref = manifest.get("oci_ref_digest", "")
    if not _is_non_empty_str(oci_ref):
        errors.append("durable_storage_oci.json.oci_ref_digest must be non-empty")
    elif _is_non_empty_str(digest) and digest not in oci_ref:
        errors.append("durable_storage_oci.json.oci_ref_digest must include digest")

    tar_sha = manifest.get("tar_sha256", "")
    if not _is_non_empty_str(tar_sha):
        errors.append("durable_storage_oci.json.tar_sha256 must be non-empty")

    return errors
