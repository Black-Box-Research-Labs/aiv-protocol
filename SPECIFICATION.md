# AIV Canonical Specification

**Auditable Verification Standard for AI-Assisted Code Changes**

---

## Document Control

| Field                  | Value                                                                      |
| ---------------------- | -------------------------------------------------------------------------- |
| **Document ID**        | `AIV-SPEC-V1.0.0-CANONICAL`                                                |
| **Title**              | AIV — Auditable Verification Standard for AI-Assisted Code Changes         |
| **Version**            | 1.0.0                                                                      |
| **Status**             | Proposed Standard                                                          |
| **Date**               | 2026-01-07                                                                 |
| **Normative Keywords** | Per RFC 2119: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY                      |
| **Scope**              | PR/MR-based software delivery including AI-authored or AI-assisted changes |
| **Conformance Target** | Engineering teams, CI/CD systems, audit functions, compliance programs     |

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
   - 1.1 Purpose
   - 1.2 Problem Statement
   - 1.3 Scope
   - 1.4 Relationship to Existing Standards
   - 1.5 Conformance Claims
   - 1.6 Conformance Scopes
   - 1.7 Adoption Ladder (Informative)
2. [Normative References](#2-normative-references)
3. [Terms and Definitions](#3-terms-and-definitions)
4. [Threat Model](#4-threat-model)
5. [Risk Classification](#5-risk-classification)
6. [Evidence Requirements](#6-evidence-requirements)
   - 6.1 Evidence Class Summary
   - 6.2 Class A — Execution Evidence
   - 6.3 Class B — Referential Evidence
   - 6.4 Class C — Negative Evidence
   - 6.5 Class D — Differential Evidence
   - 6.6 Class E — Intent Evidence
   - 6.7 Class F — Provenance Evidence
   - **6.8 Class G — Cognitive Evidence (Optional)**
   - 6.9 Evidence Item Structure
   - 6.10 Evidence Retention
7. [Verification Process](#7-verification-process)
8. [Compliance Levels](#8-compliance-levels)
9. [Gating Rules](#9-gating-rules)
10. [Exception Protocol](#10-exception-protocol)
11. [Evidence Integrity Controls](#11-evidence-integrity-controls)
12. [Security Considerations](#12-security-considerations)
13. [Privacy Considerations](#13-privacy-considerations)
14. [Conformance Testing](#14-conformance-testing)
15. [Governance and Versioning](#15-governance-and-versioning)

**Appendices**

- [Appendix A — Auditor Checklist](#appendix-a--auditor-checklist)
- [Appendix B — Packet Schema](#appendix-b--packet-schema)
- [Appendix C — Validation Rules](#appendix-c--validation-rules)
- [Appendix D — Finding Severity Taxonomy](#appendix-d--finding-severity-taxonomy)
- [Appendix E — Immutability Mechanisms](#appendix-e--immutability-mechanisms)
- [Appendix F — Profiles and Extensions](#appendix-f--profiles-and-extensions)

---

## 1. Purpose and Scope

### 1.1 Purpose

This standard defines minimum verifiable evidence requirements for code changes that include AI-authored or AI-assisted content.

**AIV is not meant to make all code safer. It is meant to make high-velocity AI code auditable at scale.**

Organizations shipping AI-generated code without conforming to this standard lack auditable assurance that changes were verified prior to deployment. **Non-conformance represents unquantified risk exposure.**

**Critical Distinction:** AIV does not claim to prove correctness. It claims to prove:

- **What** was verified
- **By whom** (accountable identity)
- **When** (immutable timestamp)
- **Against what evidence** (auditable artifacts)

This aligns AIV with established accountability models in financial auditing, aviation safety cases, and medical device validation—fields that survive precisely because they separate _correctness_ from _accountability_.

### 1.2 Problem Statement

AI-assisted development increases code production throughput beyond what humans can reliably comprehend line-by-line. Organizations increasingly ship changes validated by proxy signals (tests, CI checks) rather than verified understanding. This creates systemic risk:

- **Orphan Code:** Logic exists in repositories but in no human's mental model
- **Debug Inability:** Engineers cannot troubleshoot code they did not understand when approving
- **Verification Theater:** Green CI badges provide false assurance without semantic comprehension
- **Cognitive Debt:** Accumulated unverified changes compound into systemic fragility

AIV addresses these risks through two complementary mechanisms:

| Problem Domain          | AIV Solution                                        | Evidence Classes   |
| ----------------------- | --------------------------------------------------- | ------------------ |
| **Auditability**        | Prove verification occurred with immutable evidence | Classes A–F        |
| **Cognitive Integrity** | Prove human understanding, not just human approval  | Class G (Optional) |

**Classes A–F** solve the _auditability problem_: replacing "someone reviewed it" with "here is the immutable evidence of what was verified." This is sufficient for compliance, audit trails, and accountability.

**Class G** solves the _cognitive problem_: ensuring that verification involves actual understanding, not rubber-stamp approval. This is optional for base compliance but essential for organizations concerned about long-term maintainability and cognitive atrophy.

Organizations may adopt AIV incrementally:

1. **Start with A–F** for audit compliance and evidence integrity
2. **Add Class G** when ready to enforce cognitive engagement

### 1.3 Scope

This standard applies to:

- Pull requests / merge requests containing AI-generated or AI-assisted code
- Changes produced by LLMs, code generation tools, or autonomous agents
- Repositories using CI/CD pipelines capable of artifact retention

This standard does not apply to:

- Model training, fine-tuning, or RLHF governance
- Runtime monitoring or observability systems
- Threat modeling or design review processes
- Non-code artifacts (documentation-only changes may use reduced requirements per §5.1)

**Positioning:** AIV is intentionally downstream of code generation tools and model choices. AIV does not evaluate which AI models are "safer" or how code should be generated. It evaluates whether the resulting code was verified with auditable evidence before deployment.

### 1.4 Relationship to Existing Standards

AIV formalizes practices implicit in existing compliance frameworks:

| Standard               | AIV Alignment            | Specific Controls                    |
| ---------------------- | ------------------------ | ------------------------------------ |
| SOC 2 (CC8.1)          | Evidence Classes A, B, E | Change management, testing evidence  |
| SLSA v1.0              | Evidence Class F         | Build provenance, artifact integrity |
| ISO 27001 (A.14.2)     | Risk Classification, SoD | Secure development, change control   |
| NIST SSDF (PW.7, PW.8) | Verification Process     | Code review, security testing        |
| CycloneDX 1.5          | Evidence Class D         | Dependency tracking, SBOM            |

#### 1.4.1 Relationship to AI-Specific Standards (Informative)

AIV is designed to complement emerging AI governance frameworks:

| Framework                                     | Focus                                | AIV Relationship                                                                                    |
| --------------------------------------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------- |
| **OWASP AISVS (draft as-of 2026-01-09)**      | Security requirements for AI systems | AIV provides evidence schemas to make AISVS-aligned requirements auditable at the code-change level |
| **NIST AI RMF 1.0**                           | Risk management framework            | AIV implements "Map" and "Measure" functions with auditable artifacts                               |
| **ISO/IEC 42001:2023**                        | AI management systems                | AIV generates change-level audit artifacts for 42001 compliance                                     |
| **OpenAI Codex Review (snapshot 2026-01-09)** | AI-assisted code verification        | AIV attests human oversight of AI-assisted review processes                                         |

**Positioning:** These frameworks answer different questions:

| Question                                           | Framework                                 |
| -------------------------------------------------- | ----------------------------------------- |
| _What_ security properties should AI systems have? | OWASP AISVS (draft as-of 2026-01-09)      |
| _How_ should organizations manage AI risk?         | NIST AI RMF 1.0, ISO/IEC 42001:2023       |
| _How_ can AI assist in code verification?          | OpenAI Codex Review (snapshot 2026-01-09) |
| _How do we prove_ verification occurred?           | **AIV**                                   |

AIV does not compete with these frameworks. AIV provides the **evidence specification** that makes their requirements auditable at the code-change level.

### 1.5 Conformance Claims

An organization MAY claim AIV conformance at a specified Compliance Level (L1–L3) when:

1. All applicable requirements for that level are satisfied for changes in scope
2. Evidence artifacts are retained per §6.9
3. Conformance is validated per §14
4. Governance controls per §15 are documented

**WARNING:** Claims of conformance without validated evidence constitute misrepresentation and may expose the organization to liability.

### 1.6 Conformance Scopes

AIV requirements operate at two distinct scopes. Auditors and validators MUST understand which scope applies to each requirement.

#### 1.6.1 Per-Change Requirements

**Per-Change Requirements** are validated against individual AIV Packets. A single change either satisfies these requirements or it does not. A "change" is identified by a `pr_id` (for PR/MR workflows) or a `change_id` (for direct-to-main workflows). See §B.1 for identification requirements.

| Characteristic        | Description                                                                            |
| --------------------- | -------------------------------------------------------------------------------------- |
| **Validation Target** | Individual AIV Packet                                                                  |
| **Validator Scope**   | Can be checked by automated tooling on each PR                                         |
| **Finding Impact**    | Blocks or warns on specific change                                                     |
| **Examples**          | Evidence class presence, SHA binding, claim-evidence mapping, attestation completeness |

**Sections containing primarily Per-Change Requirements:**

- §5 Risk Classification (classification record)
- §6 Evidence Requirements (evidence classes A-F, evidence items)
- §7 Verification Process (attestation, known limitations)
- §8 Compliance Levels (level determination per change)
- §9.1–9.2 Gating Rules (merge gates)

#### 1.6.2 Program Requirements

**Program Requirements** are validated against the organization's AIV implementation as a whole. They cannot be assessed by examining a single packet.

| Characteristic        | Description                                                                      |
| --------------------- | -------------------------------------------------------------------------------- |
| **Validation Target** | Organizational policy, tooling, metrics                                          |
| **Validator Scope**   | Requires audit of multiple changes, policies, configurations                     |
| **Finding Impact**    | Affects conformance claim, not individual merges                                 |
| **Examples**          | Automated enforcement, audit sampling, retention verification, exception metrics |

**Sections containing primarily Program Requirements:**

- §6.9 Evidence Retention (retention policy implementation)
- §9.3 Automated Enforcement (CI/CD configuration)
- §10 Exception Protocol (exception metrics, thresholds)
- §11.4 Audit Sampling (sampling implementation)
- §14.3 Conformance Claim Requirements (program-level thresholds)
- §15 Governance and Versioning (policy documentation)

#### 1.6.3 Scope Markers

Throughout this specification, requirements are marked with scope indicators where ambiguity might arise:

- **[Per-Change]** — Requirement validated per packet
- **[Program]** — Requirement validated at organizational level

Where no marker is present, context determines scope: requirements about packet contents are Per-Change; requirements about organizational controls are Program.

### 1.7 Adoption Ladder (Informative)

This section is **non-normative**. It illustrates a typical adoption progression to help organizations understand that AIV conformance is incremental, not all-or-nothing.

```
┌─────────────────────────────────────────────────────────────────┐
│  ADOPTION LADDER                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Level 0: No AIV                                                │
│    → AI code ships with green CI only                           │
│    → Risk: Unquantified, unauditable                            │
│                                                                 │
│  Level 1: AIV-L1 (Classes A + B + E)                            │
│    → Auditability without friction                              │
│    → Proves: Tests ran, code is traceable, intent documented    │
│    → Effort: Minimal (can be automated)                         │
│                                                                 │
│  Level 2: AIV-L2 (Classes A + B + C + E)                        │
│    → Production-grade AI changes                                │
│    → Adds: Negative evidence (no forbidden patterns)            │
│    → Effort: Moderate (requires test integrity tooling)         │
│                                                                 │
│  Level 3: AIV-L3 (Classes A – F)                                │
│    → Regulated / critical systems                               │
│    → Adds: Differential evidence, cryptographic provenance      │
│    → Effort: Significant (requires immutable storage, signing)  │
│                                                                 │
│  Level 4: AIV-L3 + Class G                                      │
│    → Cognitive ownership enforced                               │
│    → Adds: Prediction, trace, adversarial probe, ownership      │
│    → Effort: High (requires workflow changes, not just tooling) │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Recommendation:** Most organizations should start at Level 1, stabilize tooling, then progress based on risk appetite and regulatory requirements.

---

## 2. Normative References

The following documents are referenced normatively. For dated references, only the edition cited applies. For undated references, the latest edition applies.

| Reference     | Title                                                    | Usage in AIV                         |
| ------------- | -------------------------------------------------------- | ------------------------------------ |
| RFC 2119      | Key words for use in RFCs to Indicate Requirement Levels | Normative keyword definitions (§2.1) |
| SLSA v1.0     | Supply-chain Levels for Software Artifacts               | Provenance requirements (§6.8)       |
| CycloneDX 1.5 | Software Bill of Materials Standard                      | SBOM format (§6.6)                   |
| ISO 8601      | Date and time format                                     | Timestamp formatting                 |
| SHA-256       | FIPS 180-4 Secure Hash Standard                          | Artifact hashing                     |

### 2.1 Normative Keyword Definitions

The keywords "MUST", "MUST NOT", "REQUIRED", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

For clarity:

- **MUST / REQUIRED:** Absolute requirement; non-compliance is a blocking finding
- **MUST NOT:** Absolute prohibition; violation is a blocking finding
- **SHOULD / RECOMMENDED:** Strong recommendation; deviation requires documented justification
- **SHOULD NOT:** Strong discouragement; use requires documented justification
- **MAY / OPTIONAL:** Truly optional; no justification required for either choice

---

## 3. Terms and Definitions

### 3.1 Change Terminology

| Term                   | Definition                                                                                                                                                                    |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AI-Assisted Change** | A change where code was authored or materially modified by an LLM, code generation tool, or autonomous agent, regardless of whether a human prompted or guided the generation |
| **Change**             | A proposed modification to a repository submitted as a pull request (PR), merge request (MR), or a logical grouping of commits pushed directly to a protected branch (identified by a `change_id`) |
| **Change ID**          | A human-readable identifier for a logical change in direct-to-main workflows (e.g., `enforcement-gap-fix`). Alternative to `pr_id` for teams not using PRs. See §B.1          |
| **Commit SHA**         | The SHA-1 or SHA-256 cryptographic hash uniquely identifying a Git commit                                                                                                     |
| **Evidence File**      | A per-source-file evidence artifact containing raw verification data (Class A/B/C/F). Referenced BY packets but not itself an AIV Packet. See §6.11                           |
| **Head SHA**           | The commit SHA at the tip of the PR/MR branch, or the last commit in a logical change, at the time of verification                                                            |

### 3.2 Artifact Terminology

| Term                   | Definition                                                                                                                                        |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Artifact**           | A concrete object that can be inspected, executed, or cryptographically verified (CI run, log, coverage report, SBOM, signature, permalink, etc.) |
| **Immutable Artifact** | An artifact meeting the immutability requirements defined in §3.3                                                                                 |
| **Content-Addressed**  | An artifact identified by a cryptographic hash of its contents (e.g., `sha256:abc123...`)                                                         |
| **Commit-Addressed**   | An artifact identified by association with a specific commit SHA                                                                                  |

### 3.3 Immutability Definition

An artifact is considered **immutable** for AIV purposes if it satisfies ALL of the following criteria:

1. **Content Integrity:** The artifact content cannot be modified after creation without detection
2. **Reference Stability:** The reference (URL, path, ID) resolves to the same content indefinitely
3. **Deletion Protection:** The artifact cannot be deleted during the retention period without audit trail
4. **Verification Method:** A mechanism exists to verify the artifact has not been modified

**Acceptable immutability mechanisms** (see Appendix E for implementation details):

| Mechanism                  | Example                              | Verification Method         |
| -------------------------- | ------------------------------------ | --------------------------- |
| Content-addressed storage  | IPFS, OCI registry with digest       | Hash comparison             |
| Commit-SHA-bound permalink | GitHub permalink with SHA            | Git verification            |
| Signed attestation         | Sigstore, GPG signature              | Signature verification      |
| WORM storage               | S3 Object Lock, Azure Immutable Blob | Storage policy verification |
| Hash manifest              | SHA-256 in packet + separate storage | Hash comparison             |

**NOT acceptable as immutable:**

- Branch-based URLs (content changes with branch)
- "Latest" links (content changes over time)
- Mutable issue tracker links without snapshot
- CI artifacts without retention guarantee
- Any reference that can be silently modified

### 3.4 Protocol Terminology

| Term                | Definition                                                                                                                    |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **AIV Packet**      | The structured bundle of claims, evidence, and attestations required by this standard, conforming to the schema in Appendix B |
| **Claim**           | A numbered, testable statement about what changed and what properties hold                                                    |
| **Evidence Item**   | An artifact or reference to an immutable artifact that supports one or more claims                                            |
| **Evidence Class**  | One of the standardized categories (A–F) defined in §6, each with specific minimum requirements                               |
| **Validation Rule** | A machine-checkable requirement with a unique identifier (e.g., A-001)                                                        |
| **Finding**         | A documented instance of non-conformance with a validation rule                                                               |

### 3.5 Classification Terminology

| Term                           | Definition                                                                        |
| ------------------------------ | --------------------------------------------------------------------------------- |
| **Risk Tier**                  | Classification (R0–R3) determining minimum evidence requirements, assigned per §5 |
| **Compliance Level**           | Conformance grade (L1–L3) based on evidence completeness and process controls     |
| **Separation of Duties (SoD)** | Constraint on identity overlap between Author and Verifier roles                  |
| **Critical Surface**           | A code area where defects have elevated impact (defined in §5.2)                  |

### 3.6 Role Terminology

| Term                              | Definition                                                                                          |
| --------------------------------- | --------------------------------------------------------------------------------------------------- |
| **Author**                        | The accountable identity submitting the change; responsible for generating the AIV Packet           |
| **Verifier**                      | The accountable identity validating claim-evidence mapping and attesting to verification completion |
| **Approver**                      | The identity authorizing merge after gates pass; may be the same as Verifier for R0-R1              |
| **Designated Exception Approver** | An identity explicitly authorized by organizational policy to approve exceptions per §10            |

---

## 4. Threat Model

### 4.1 Failure Modes AIV Addresses

AIV is designed to reduce risk from the following failure modes:

| Failure Mode               | Description                                      | AIV Mitigation                            |
| -------------------------- | ------------------------------------------------ | ----------------------------------------- |
| **Rubber-Stamp Approval**  | Verifier approves without examining evidence     | Evidence class requirements, attestation  |
| **Green Test Fallacy**     | Tests pass but implementation violates intent    | Class E (Intent), Class C (Negative)      |
| **Evidence Theater**       | Packet exists but doesn't prove claims           | Validation rules, integrity controls      |
| **Hidden Coupling**        | Change has undocumented dependencies             | Class D (Differential), scope validation  |
| **Silent Regression**      | Behavior changes without explicit acknowledgment | Class C (Negative), test integrity checks |
| **Risk Misclassification** | High-risk change treated as low-risk             | Mandatory escalation rules (§5.2)         |
| **Verifier Gaming**        | Verifier and Author collude to bypass controls   | SoD requirements, audit sampling          |
| **Artifact Manipulation**  | Evidence modified after verification             | Immutability requirements, provenance     |

### 4.2 Failure Modes AIV Does NOT Address

AIV does not guarantee protection against:

| Failure Mode              | Why AIV Doesn't Address                                 | Complementary Control              |
| ------------------------- | ------------------------------------------------------- | ---------------------------------- |
| **Semantic Correctness**  | AIV verifies evidence exists, not that logic is correct | Design review, formal methods      |
| **Novel Vulnerabilities** | Unknown vulnerability classes not in check patterns     | Security research, pen testing     |
| **Compromised CI**        | Malicious CI runner can forge evidence                  | Trusted builder policies, SLSA L3+ |
| **Malicious Maintainer**  | Repo admin can bypass controls                          | Privileged access management       |
| **AI Model Defects**      | Systematic errors in AI training                        | Model governance, testing          |
| **Runtime Failures**      | Production behavior differs from test                   | Observability, canary deployments  |

### 4.3 Trust Boundaries

AIV assumes the following trust boundaries:

| Trusted                                       | Untrusted                           |
| --------------------------------------------- | ----------------------------------- |
| Git commit integrity (SHA-1/256)              | PR description content              |
| CI runner execution (for signed attestations) | Self-reported risk classification   |
| Cryptographic signature verification          | Claim accuracy without evidence     |
| Organizational identity management            | Evidence without immutability proof |

---

## 5. Risk Classification

### 5.1 Risk Tier Definitions

Every change subject to AIV MUST be classified into exactly one Risk Tier. If classification is uncertain, the change MUST be classified at the higher applicable tier.

| Tier   | Name    | Criteria                                                                                               | Examples                                                                 |
| ------ | ------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| **R0** | Trivial | Documentation, comments, formatting only; no runtime effect; no test changes                           | README updates, comment fixes, whitespace normalization                  |
| **R1** | Low     | Isolated logic changes; no critical surfaces (§5.2); bounded blast radius; comprehensive test coverage | Bug fixes in non-critical paths, minor refactors with full test coverage |
| **R2** | Medium  | Broad refactors, dependency changes, public API changes, database migrations, configuration changes    | Library upgrades, schema migrations, API additions, feature flags        |
| **R3** | High    | Any change touching critical surfaces (§5.2), or changes with organization-wide blast radius           | Auth logic, payment processing, credential handling, encryption          |

### 5.2 Critical Surfaces (Mandatory R3 Escalation)

A change MUST be classified as **R3** regardless of other factors if it modifies code in any of the following critical surfaces:

| Critical Surface         | Trigger Patterns                                                              | Examples                                                        |
| ------------------------ | ----------------------------------------------------------------------------- | --------------------------------------------------------------- |
| **Authentication**       | Login, session management, token generation/validation, identity verification | `login()`, `authenticate()`, `verify_token()`, session handlers |
| **Authorization**        | Permission checks, role assignment, access control, capability grants         | `check_permission()`, `has_role()`, ACL modifications           |
| **Secrets Management**   | Credential storage, API key handling, encryption key management               | Key rotation, secret injection, vault integration               |
| **Cryptography**         | Encryption/decryption, signing/verification, hashing, random generation       | Cipher selection, key derivation, signature validation          |
| **Financial Processing** | Payment handling, billing logic, monetary calculations, ledger operations     | `charge_card()`, `calculate_total()`, transaction processing    |
| **PII Handling**         | Personal data storage, processing, transmission, anonymization                | User data CRUD, export functions, data masking                  |
| **Privilege Boundaries** | Sandbox escapes, privilege escalation, trust boundary crossings               | `setuid`, capability grants, container breakouts                |
| **Audit/Logging**        | Security event logging, audit trail generation, compliance logging            | Audit log writes, event capture, log sanitization               |

**Finding (5.2-F1):** Change touching critical surface classified below R3.

### 5.3 Blast Radius Assessment

For changes not touching critical surfaces, Risk Tier is informed by blast radius:

| Blast Radius      | Description                                      | Typical Tier |
| ----------------- | ------------------------------------------------ | ------------ |
| **Local**         | Single function/module, no callers outside file  | R0-R1        |
| **Component**     | Multiple files within single service/package     | R1-R2        |
| **Service**       | Affects entire service behavior or public API    | R2           |
| **Cross-Service** | Affects multiple services or shared libraries    | R2-R3        |
| **Organization**  | Affects all deployments or shared infrastructure | R3           |

### 5.4 Separation of Duties Requirements

| Tier | SoD Mode         | Requirement                                     |
| ---- | ---------------- | ----------------------------------------------- |
| R0   | S0 (Self-Verify) | Author MAY verify own change                    |
| R1   | S0 (Self-Verify) | Author MAY verify own change                    |
| R2   | S1 (Independent) | Verifier MUST be different identity than Author |
| R3   | S1 (Independent) | Verifier MUST be different identity than Author |

**Finding (5.4-F1):** SoD violation — Author and Verifier are same identity for R2+ change.

#### 5.4.1 Identity Definition

Two identities are considered "different" if they correspond to different natural persons. The following do NOT satisfy SoD requirements:

- Shared accounts used by the same person in both roles
- Role accounts or service accounts operated by the same person
- Automation accounts acting on behalf of the same person
- Different usernames that map to the same natural person

#### 5.4.2 Identity Verification Requirements

Organizations MUST document how Author and Verifier identities are verified as belonging to different natural persons. The AIV Policy (§15.1) MUST specify:

| Requirement                | Description                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Identity Provider**      | Which identity provider(s) are authoritative (e.g., corporate SSO, GitHub org membership)            |
| **Cross-Platform Mapping** | How identities are linked across platforms if Author and Verifier use different systems              |
| **Verification Method**    | How validators confirm identities are distinct (e.g., SSO sub claim, email domain, HR system lookup) |
| **Edge Case Handling**     | How the organization handles ambiguous cases (see §5.4.3)                                            |

#### 5.4.3 Edge Cases

| Scenario                            | Guidance                                                                                                                                                                        |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pair Programming**                | Commit author is one person; both may have contributed. SoD satisfied if Verifier was not part of the pair. If both pair members need to be Authors, a third party MUST verify. |
| **AI Agent as Author**              | The human who directed the AI is considered the Author. Verifier must be a different human.                                                                                     |
| **Contractor using client account** | The natural person operating the account is the identity, not the account owner. Document the mapping.                                                                          |
| **Same person, different orgs**     | If a person has accounts in multiple organizations, they are still one natural person. SoD not satisfied by using different org accounts.                                       |

#### 5.4.4 Automated SoD Validation

Validators SHOULD implement automated SoD checks where possible:

```yaml
# Example: SoD validation using email domain
sod_validation:
  method: "email_identity"
  author_identity: "alice@example.com"
  verifier_identity: "bob@example.com"
  same_person: false
  validation_source: "corporate_sso"
```

Where automated validation is not possible, the Verifier attestation MUST include an explicit declaration:

```yaml
attestations:
  - verifier_id: "bob@example.com"
    sod_declaration: "I confirm I am not the same natural person as the Author (alice@example.com)"
```

**Finding (5.4-F2):** SoD verification method not documented in organizational policy.
**Finding (5.4-F3):** Cross-platform identity mapping not documented for multi-platform workflow.

### 5.5 Classification Record

The AIV Packet MUST include a classification record with the following fields:

```yaml
classification:
  risk_tier: R0 | R1 | R2 | R3 # REQUIRED
  sod_mode: S0 | S1 # REQUIRED
  critical_surfaces: [] # REQUIRED for R3; list of surfaces touched
  blast_radius: local | component | service | cross-service | organization # REQUIRED
  classification_rationale: string # REQUIRED; explanation of tier assignment
  classified_by: string # REQUIRED; identity performing classification
  classified_at: ISO-8601 timestamp # REQUIRED
```

**Finding (5.5-F1):** Missing or incomplete classification record.
**Finding (5.5-F2):** Classification rationale missing or inadequate.

---

## 6. Evidence Requirements

### 6.1 Evidence Class Summary

| Class | Name         | Purpose                                        | R0  | R1  | R2  | R3  | Notes              |
| ----- | ------------ | ---------------------------------------------- | :-: | :-: | :-: | :-: | ------------------ |
| **A** | Execution    | Proves tests passed in defined environment     |  ✓  |  ✓  |  ✓  |  ✓  |                    |
| **B** | Referential  | Proves traceability to exact code locations    |  ✓  |  ✓  |  ✓  |  ✓  |                    |
| **C** | Negative     | Proves absence of disallowed patterns          |     |     |  ✓  |  ✓  |                    |
| **D** | Differential | Proves change impact beyond test coverage      |     |     |     |  ✓  |                    |
| **E** | Intent       | Proves alignment with upstream requirement     |     |  ✓  |  ✓  |  ✓  |                    |
| **F** | Provenance   | Proves artifact integrity and chain-of-custody |     |     |     |  ✓  |                    |
| **G** | Cognitive    | Proves human semantic comprehension occurred   |     |     |     |  ○  | Optional; see §6.8 |

**Legend:** ✓ = Required | ○ = Optional | (blank) = Not applicable

**Note on Class G:** Class G is optional for all compliance levels (L1–L3). Organizations seeking enhanced assurance of cognitive engagement SHOULD implement Class G, particularly for R3 changes. See §6.8 for full specification.

### 6.2 Class A — Execution Evidence

**Purpose:** Proves the change was executed in a controlled environment and automated checks passed.

#### 6.2.1 Required Artifacts

| Artifact                  | Requirement                                                  | All Tiers |
| ------------------------- | ------------------------------------------------------------ | :-------: |
| **CI Run Reference**      | Immutable link to CI run bound to exact `commit_sha`         |     ✓     |
| **Test Results**          | Pass/fail/skip counts for all executed test suites           |     ✓     |
| **Test List**             | Enumeration of test names/IDs that executed                  |     ✓     |
| **Static Analysis**       | Lint/typecheck results, or explicit "N/A" with justification |     ✓     |
| **Execution Environment** | OS, runtime version, dependency versions                     |     ✓     |

#### 6.2.2 Validation Rules

| Rule ID | Rule                                                                | Severity |
| ------- | ------------------------------------------------------------------- | -------- |
| A-001   | CI run reference MUST be immutable per §3.3                         | BLOCK    |
| A-002   | CI run commit SHA MUST match packet `head_sha`                      | BLOCK    |
| A-003   | Test results MUST include pass/fail/skip counts (not just "passed") | BLOCK    |
| A-004   | If static analysis is "N/A", justification MUST be documented       | WARN     |
| A-005   | CI artifacts MUST be retained per §6.9                              | BLOCK    |
| A-006   | Test list MUST be reproducible (re-running produces same list)      | WARN     |

#### 6.2.3 Findings

| Finding ID | Description                                           |
| ---------- | ----------------------------------------------------- |
| A-F1       | CI run reference not immutable or not resolvable      |
| A-F2       | CI run SHA does not match packet head_sha             |
| A-F3       | Test results incomplete (missing counts or breakdown) |
| A-F4       | Static analysis N/A without justification             |
| A-F5       | CI artifacts not retained per retention policy        |

### 6.3 Class B — Referential Evidence

**Purpose:** Proves traceability from claims to exact code locations.

#### 6.3.1 Required Artifacts

| Artifact              | Requirement                                                   | All Tiers |
| --------------------- | ------------------------------------------------------------- | :-------: |
| **Code Permalinks**   | Commit-SHA-bound links to relevant files/lines for each claim |     ✓     |
| **Scope Inventory**   | Complete list of created/modified/deleted files               |     ✓     |
| **Symbol References** | Function/class/method identifiers for behavioral claims       |     ✓     |

#### 6.3.2 Validation Rules

| Rule ID | Rule                                                         | Severity                   |
| ------- | ------------------------------------------------------------ | -------------------------- |
| B-001   | All code links MUST resolve to exact commit SHA (not branch) | BLOCK                      |
| B-002   | All code links MUST include line anchors for specific claims | BLOCK (R2+) / WARN (R0-R1) |
| B-003   | Scope inventory MUST match actual Git diff file list         | BLOCK                      |
| B-004   | Each claim MUST have at least one referential evidence item  | BLOCK                      |
| B-005   | Symbol references MUST be valid identifiers in the codebase  | WARN                       |

#### 6.3.3 Findings

| Finding ID | Description                                       |
| ---------- | ------------------------------------------------- |
| B-F1       | Code link references branch instead of commit SHA |
| B-F2       | Code link missing line anchor for specific claim  |
| B-F3       | Scope inventory does not match actual diff        |
| B-F4       | Claim has no referential evidence                 |
| B-F5       | Symbol reference not found in codebase            |

### 6.4 Class C — Negative Evidence

**Purpose:** Proves absence of disallowed patterns and conservation of existing constraints.

#### 6.4.1 Required Artifacts

| Artifact                     | Requirement                                                          | R2+ |
| ---------------------------- | -------------------------------------------------------------------- | :-: |
| **Search Scope Declaration** | Explicit paths/modules/patterns searched                             |  ✓  |
| **Search Method**            | Tool, version, and configuration used                                |  ✓  |
| **Pattern Specification**    | Enumerated patterns checked (allowlist or denylist)                  |  ✓  |
| **Search Results**           | Output demonstrating absence (empty result or explicit "no matches") |  ✓  |
| **Test Integrity Report**    | Evidence that test coverage was not weakened                         |  ✓  |

#### 6.4.2 Test Integrity Requirements

For R2+ changes, the packet MUST include evidence that test integrity was preserved:

| Check                       | Requirement                                               | Method                         |
| --------------------------- | --------------------------------------------------------- | ------------------------------ |
| **No Assertion Weakening**  | Existing assertions not removed or weakened               | Semantic diff of test files    |
| **No Skip Addition**        | No new skip/ignore decorators added without justification | Pattern analysis of test files |
| **Coverage Non-Regression** | Code coverage did not decrease for modified files         | Coverage diff report           |

**IMPORTANT:** Test integrity checks MUST use semantic analysis appropriate to the language/framework. Simple grep patterns are insufficient and MUST NOT be used as the sole verification method.

#### 6.4.2.1 Semantic Analysis Minimum Criteria

A test integrity check qualifies as "semantic analysis" if it satisfies ALL of the following:

1. **Structural Awareness:** The method understands code structure (functions, classes, blocks), not just text patterns
2. **Change Detection Granularity:** Can detect individual assertion/test additions and removals, not just file-level changes
3. **Framework Recognition:** Recognizes the testing framework's assertion patterns (e.g., `assert`, `expect`, `should`, matchers)
4. **Deterministic Output:** Produces the same result when run multiple times on the same inputs
5. **Machine-Readable Results:** Outputs structured data (JSON, XML, etc.) suitable for automated validation

**Acceptable methods with qualification:**

| Method                            | Qualifies If...                                                                            |
| --------------------------------- | ------------------------------------------------------------------------------------------ |
| AST-based diff                    | Parses language syntax; compares structural elements                                       |
| Coverage tool comparison          | Reports line/branch coverage delta with file granularity                                   |
| Test framework JSON output        | Framework reports individual test/assertion counts                                         |
| Language-specific static analysis | Tool explicitly designed for test analysis (e.g., pytest --collect-only, jest --listTests) |

**Not acceptable as sole method:**

| Method                            | Why Not Acceptable                                        |
| --------------------------------- | --------------------------------------------------------- |
| Simple string grep                | No structural awareness; false positives/negatives        |
| Line-count comparison             | No semantic understanding; counts can change legitimately |
| Manual inspection without tooling | Not deterministic or machine-readable                     |
| Generic diff without parsing      | No framework recognition                                  |

**Profile Requirement:** If no language-specific AIV Profile exists for the project's language/framework, the packet MUST include:

1. Documentation of the semantic analysis method used
2. Justification that the method satisfies the minimum criteria above
3. Example output demonstrating structural awareness

#### 6.4.3 Validation Rules

| Rule ID | Rule                                                                  | Severity |
| ------- | --------------------------------------------------------------------- | -------- |
| C-001   | Search scope MUST be explicitly declared                              | BLOCK    |
| C-002   | Search method MUST be documented and deterministic                    | BLOCK    |
| C-003   | Patterns MUST be enumerated (not "checked for issues")                | BLOCK    |
| C-004   | Test integrity report MUST use semantic analysis, not string matching | BLOCK    |
| C-005   | If new skips added, justification MUST be in `known_limitations`      | WARN     |
| C-006   | Coverage decrease MUST be justified in `known_limitations`            | WARN     |

#### 6.4.4 Findings

| Finding ID | Description                                       |
| ---------- | ------------------------------------------------- |
| C-F1       | Search scope not declared                         |
| C-F2       | Search method not documented or non-deterministic |
| C-F3       | Patterns not enumerated                           |
| C-F4       | Test integrity check used inadequate method       |
| C-F5       | Test integrity degradation without justification  |

### 6.5 Class D — Differential Evidence

**Purpose:** Proves change impact beyond what tests capture, including API surface, dependencies, and data schemas.

#### 6.5.1 Required Artifacts (R3)

For R3 changes, the packet MUST include differential evidence for **each category of surface touched**:

| Surface Category     | Required Artifact                     | When Required                          |
| -------------------- | ------------------------------------- | -------------------------------------- |
| **API Surface**      | Public function/endpoint/schema diff  | If public interfaces modified          |
| **Dependencies**     | Lockfile diff + SBOM delta            | If dependencies added/removed/upgraded |
| **Data Schema**      | DDL diff, migration scripts           | If database schema modified            |
| **Configuration**    | Config file diff with impact analysis | If configuration changed               |
| **Security Surface** | Permissions/auth path diff            | If security boundaries modified        |

**NOTE:** "At least one" differential artifact is NOT sufficient. The packet MUST include artifacts for each category that applies to the change.

#### 6.5.2 Validation Rules

| Rule ID | Rule                                                           | Severity |
| ------- | -------------------------------------------------------------- | -------- |
| D-001   | Differential evidence MUST cover each surface category touched | BLOCK    |
| D-002   | Diffs MUST be bound to specific commit SHAs (head and base)    | BLOCK    |
| D-003   | Tools and versions MUST be documented                          | WARN     |
| D-004   | Raw artifacts MUST be available (not only summaries)           | BLOCK    |
| D-005   | SBOM MUST conform to CycloneDX 1.5 or SPDX 2.3 format          | WARN     |

#### 6.5.3 Findings

| Finding ID | Description                                                |
| ---------- | ---------------------------------------------------------- |
| D-F1       | Differential evidence missing for touched surface category |
| D-F2       | Diff not bound to specific commit SHAs                     |
| D-F3       | Raw artifacts not available                                |
| D-F4       | SBOM format non-standard                                   |

### 6.6 Class E — Intent Evidence

**Purpose:** Proves implementation aligns with upstream requirement or specification.

#### 6.6.1 Required Artifacts

| Artifact                      | Requirement                                     | R1+ |
| ----------------------------- | ----------------------------------------------- | :-: |
| **Requirement Reference**     | Immutable reference to requirement source       |  ✓  |
| **Requirement-Claim Mapping** | Each requirement mapped to claims               |  ✓  |
| **Claim-Evidence Mapping**    | Each claim mapped to evidence items             |  ✓  |
| **Acceptance Checklist**      | Criteria marked: satisfied / N/A / out-of-scope |  ✓  |

#### 6.6.2 Immutable Requirement Reference

The requirement reference MUST be immutable per §3.3. Acceptable mechanisms include:

| Source Type       | Acceptable Reference                               | NOT Acceptable           |
| ----------------- | -------------------------------------------------- | ------------------------ |
| Git-tracked spec  | Commit-SHA permalink to spec file                  | Branch link to spec file |
| Issue tracker     | Exported snapshot with hash, or versioned issue ID | Mutable issue URL        |
| External document | PDF/snapshot with SHA-256 hash recorded in packet  | Live document URL        |
| RFC/Standard      | Version-specific reference (e.g., "RFC 2119")      | "Current RFC"            |

**Implementation Guidance:** Organizations SHOULD establish a standard mechanism for creating immutable requirement references. Common approaches:

1. **Spec-in-Repo:** Requirements tracked as markdown files in the repository; reference by commit SHA
2. **Snapshot Export:** Issue/ticket exported to immutable storage; hash recorded in packet
3. **Version Tagging:** Issue tracker configured to create immutable versions; reference specific version ID

#### 6.6.2.1 Transitional Pathway for Requirement Immutability

Recognizing that many organizations use mutable issue trackers (GitHub Issues, Jira, Linear, etc.) without snapshot infrastructure, AIV provides a transitional pathway:

| Compliance Level | Requirement Immutability     | Severity | Conditions                                |
| ---------------- | ---------------------------- | -------- | ----------------------------------------- |
| **L1**           | Mutable reference allowed    | WARN     | Must include snapshot deadline            |
| **L2**           | Mutable reference allowed    | WARN     | Snapshot required within 30 days of merge |
| **L3**           | Immutable reference required | BLOCK    | No exceptions                             |

**For L1/L2 with mutable references:**

When a mutable requirement reference is used at L1 or L2, the packet MUST include:

```yaml
requirement_reference:
  url: "https://github.com/org/repo/issues/42" # Mutable URL
  immutable: false
  snapshot_obligation:
    required_by: ISO-8601 # Within 30 days of merge
    snapshot_method: "pdf_export | api_export | archive_org"
    responsible_party: string
  content_summary: string # Brief summary of requirement at time of verification
  verified_at: ISO-8601 # When verifier confirmed requirement content
```

**Post-Merge Snapshot Requirement:**

For L2 conformance claims, organizations MUST:

1. Create an immutable snapshot within 30 days of merge
2. Update the packet or create a supplement with the snapshot reference
3. Track snapshot completion rate as a program metric

**Finding (E-F1a):** Mutable requirement reference at L3 (BLOCK).
**Finding (E-F1b):** Mutable requirement reference at L1/L2 without snapshot obligation (WARN).
**Finding (E-F6):** Snapshot obligation not fulfilled within deadline (WARN → BLOCK after 30 days).

#### 6.6.3 Validation Rules

| Rule ID | Rule                                                      | Severity |
| ------- | --------------------------------------------------------- | -------- |
| E-001   | Requirement reference MUST be immutable per §3.3          | BLOCK    |
| E-002   | Each requirement MUST map to at least one claim           | BLOCK    |
| E-003   | Each claim MUST map to at least one evidence item         | BLOCK    |
| E-004   | Acceptance checklist MUST be complete (no unmarked items) | WARN     |
| E-005   | Out-of-scope items MUST have justification                | WARN     |

#### 6.6.4 Findings

| Finding ID | Description                             |
| ---------- | --------------------------------------- |
| E-F1       | Requirement reference is mutable        |
| E-F2       | Requirement not mapped to any claim     |
| E-F3       | Claim not mapped to any evidence        |
| E-F4       | Acceptance checklist incomplete         |
| E-F5       | Out-of-scope item without justification |

### 6.7 Class F — Provenance Evidence

**Purpose:** Proves artifact integrity and chain-of-custody; establishes that evidence was not forged.

#### 6.7.1 Required Artifacts (R3)

| Artifact                      | Requirement                                                      | R3  |
| ----------------------------- | ---------------------------------------------------------------- | :-: |
| **Cryptographic Attestation** | At least one: signed commits, CI attestation, or SLSA provenance |  ✓  |
| **Artifact Hashes**           | SHA-256 hashes for all Class A-E evidence artifacts              |  ✓  |
| **Builder Identity**          | CI runner/builder identification with trust basis                |  ✓  |
| **Timestamp Attestation**     | Signed timestamp for packet creation                             |  ✓  |

#### 6.7.2 Acceptable Provenance Mechanisms

| Mechanism               | Trust Basis                       | Implementation                            |
| ----------------------- | --------------------------------- | ----------------------------------------- |
| **Signed Commits**      | GPG/SSH key or Sigstore (Gitsign) | Verify signature chain to trusted key     |
| **CI OIDC Attestation** | CI provider identity federation   | Verify OIDC token binding to workflow     |
| **SLSA Provenance**     | SLSA framework verification       | Verify provenance predicate per SLSA spec |
| **Notarization**        | Timestamping authority            | Verify TSA signature and timestamp        |

#### 6.7.3 Validation Rules

| Rule ID | Rule                                                            | Severity |
| ------- | --------------------------------------------------------------- | -------- |
| F-001   | At least one cryptographic provenance mechanism MUST be present | BLOCK    |
| F-002   | Provenance MUST cryptographically bind to packet `head_sha`     | BLOCK    |
| F-003   | All evidence artifacts MUST have SHA-256 hashes recorded        | BLOCK    |
| F-004   | Builder identity MUST be documented                             | WARN     |
| F-005   | Unsigned evidence MUST be labeled as such                       | WARN     |
| F-006   | Artifact hashes MUST be verifiable (artifact available)         | BLOCK    |

#### 6.7.4 Findings

| Finding ID | Description                                   |
| ---------- | --------------------------------------------- |
| F-F1       | No cryptographic provenance mechanism present |
| F-F2       | Provenance not bound to commit SHA            |
| F-F3       | Evidence artifact missing hash                |
| F-F4       | Artifact hash verification failed             |
| F-F5       | Builder identity not documented               |

### 6.8 Class G — Cognitive Evidence (Optional)

**Purpose:** Proves that human verification involved semantic comprehension, not just approval. Class G addresses the _cognitive problem_ that Classes A–F cannot solve: ensuring the verifier actually understood the change.

**Status:** Optional for all compliance levels (L1–L3). RECOMMENDED for R3 changes. Organizations seeking enhanced assurance of cognitive engagement SHOULD implement Class G.

#### 6.8.1 The Cognitive Problem

Classes A–F prove that verification _occurred_ and that evidence _exists_. They do not prove that the verifier _understood_ the change. This creates a failure mode:

| Failure Mode            | What A–F Prove           | What A–F Cannot Prove         |
| ----------------------- | ------------------------ | ----------------------------- |
| Rubber-stamp approval   | Verifier clicked approve | Verifier read the code        |
| Copy-paste verification | Evidence artifacts exist | Verifier understood artifacts |
| Checkbox compliance     | All fields populated     | Population required thought   |

Class G addresses this gap by requiring evidence of cognitive work product—artifacts that could only be produced by someone who understood the change.

**Critical Framing:** Class G does not guarantee deep understanding. No artifact can prove what someone truly comprehends. What Class G _does_ guarantee is that:

1. **Someone incurred cognitive cost** — producing predictions, traces, and probes requires mental effort
2. **Someone accepted ownership** — the ownership declaration creates personal accountability
3. **A paper trail exists** — if the code fails, there is a named person who attested to understanding it

This reframes Class G as **ownership enforcement**, not epistemic purity. The goal is not to prove the verifier is brilliant—it is to ensure the code is _owned_, not orphaned.

#### 6.8.2 Required Artifacts (When Implemented)

When an organization implements Class G, packets MUST include:

| Artifact                  | Purpose                                                           | Verification Method                        |
| ------------------------- | ----------------------------------------------------------------- | ------------------------------------------ |
| **Prediction Document**   | Verifier predicts behavior BEFORE examining implementation        | Timestamp must precede code examination    |
| **Mental Trace**          | Verifier documents execution path through code                    | Must reference specific lines/functions    |
| **Adversarial Probe**     | Verifier documents edge cases and failure modes considered        | Must include at least one non-obvious case |
| **Ownership Declaration** | Verifier attests to ability to debug/modify without AI assistance | Explicit attestation                       |

#### 6.8.3 The Four-Phase Verification Process (SVP)

Class G artifacts follow the Systematic Verifier Protocol (SVP):

**Phase 1: Black Box Prediction**
Before examining implementation, the verifier documents:

- Expected behavior based on requirements
- Predicted approach to solving the problem
- Anticipated edge cases

**Phase 2: Mental Trace**
While examining code, the verifier documents:

- Execution flow for primary use case
- State transformations at each step
- Where predictions matched or diverged

**Phase 3: Adversarial Probe**
After understanding implementation, the verifier documents:

- At least 3 edge cases considered
- At least 1 potential failure mode
- How implementation handles (or fails to handle) each

**Phase 4: Ownership Lock**
The verifier attests:

- "I could debug this code without AI assistance"
- "I could explain this code to another engineer"
- "I could modify this code to handle a new requirement"

#### 6.8.4 Evidence Structure

```yaml
evidence_items:
  - id: "EV-G-001"
    class: G
    description: "Cognitive verification evidence"
    artifacts:
      - type: prediction_document
        reference: string # URL or content-addressed ID
        created_before_code_review: boolean # MUST be true
        timestamp: ISO-8601
        content_hash: string # SHA-256 of prediction content

      - type: mental_trace
        reference: string
        lines_referenced: [string] # Specific line numbers traced
        functions_traced: [string] # Function names in trace

      - type: adversarial_probe
        edge_cases_count: integer # Minimum 3
        failure_modes_count: integer # Minimum 1
        reference: string

      - type: ownership_declaration
        attestations:
          - can_debug_without_ai: boolean
          - can_explain_to_peer: boolean
          - can_modify_for_new_requirement: boolean
        verifier_signature: string
```

#### 6.8.5 Validation Rules

| Rule ID | Rule                                                            | Severity |
| ------- | --------------------------------------------------------------- | -------- |
| COG-001 | Prediction document MUST be timestamped before code examination | BLOCK    |
| COG-002 | Mental trace MUST reference specific code locations             | BLOCK    |
| COG-003 | Adversarial probe MUST include ≥3 edge cases                    | WARN     |
| COG-004 | Adversarial probe MUST include ≥1 failure mode                  | WARN     |
| COG-005 | Ownership declaration MUST include all three attestations       | BLOCK    |

#### 6.8.6 Findings

| Finding ID | Description                                              |
| ---------- | -------------------------------------------------------- |
| G-F1       | Prediction document timestamp after code examination     |
| G-F2       | Mental trace lacks specific code references              |
| G-F3       | Adversarial probe insufficient (fewer than 3 edge cases) |
| G-F4       | Adversarial probe lacks failure mode analysis            |
| G-F5       | Ownership declaration incomplete                         |

#### 6.8.7 Gaming Resistance

Class G is inherently more susceptible to gaming than Classes A–F because cognitive work cannot be machine-verified. Mitigations include:

| Gaming Vector          | Mitigation                                                     |
| ---------------------- | -------------------------------------------------------------- |
| Post-hoc prediction    | Cryptographic timestamp or commit-before-review workflow       |
| Generic traces         | Require specific line numbers; audit sampling checks coherence |
| Checkbox edge cases    | Require prose descriptions; audit sampling evaluates quality   |
| False ownership claims | Random spot-checks; pair debugging sessions                    |

**Audit Sampling for Class G:** Organizations implementing Class G SHOULD conduct periodic spot-checks where verifiers are asked to explain or modify code they previously verified.

#### 6.8.8 When to Implement Class G

| Scenario                                   | Recommendation |
| ------------------------------------------ | -------------- |
| High-risk changes (R3)                     | RECOMMENDED    |
| Security-critical surfaces                 | RECOMMENDED    |
| New team members verifying unfamiliar code | RECOMMENDED    |
| Established team, low-risk changes         | Optional       |
| Heavily tested, well-understood codebase   | Optional       |

**Organizational Adoption Path:**

1. Start with Classes A–F for all changes
2. Add Class G for R3 changes only
3. Expand to R2 as tooling matures
4. Evaluate whether R1 benefits from Class G

### 6.9 Evidence Item Structure

Each evidence item in the packet MUST conform to this structure:

```yaml
evidence_items:
  - id: string # Unique identifier within packet
    class: A | B | C | D | E | F | G # Evidence class
    description: string # Human-readable description
    claim_refs: [string] # IDs of claims this evidence supports
    artifacts:
      - type: string # ci_run | permalink | search_output | diff | attestation | prediction_document | mental_trace | etc.
        reference: string # URL or content-addressed ID
        immutability_mechanism: string # How immutability is achieved (§3.3)
        canonical_form: string # How artifact was canonicalized for hashing (§6.9.1)
        sha256: string # SHA-256 hash of canonical form (REQUIRED for R3)
        retrieved_at: ISO-8601 # When artifact was retrieved/created
    scope: string # What this evidence covers
    validation_method: string # How to verify this evidence
    limitations: [string] # Known limitations of this evidence
```

#### 6.9.1 Artifact Canonicalization for Hashing

Artifact hashes MUST be computed on a **canonical, stable representation** of the artifact content. Hashing raw HTTP responses or rendered HTML is NOT acceptable because these contain dynamic elements (timestamps, session tokens, ads, etc.) that change on each retrieval.

**Canonicalization Requirements:**

| Artifact Type           | Canonical Form                       | How to Obtain                                 |
| ----------------------- | ------------------------------------ | --------------------------------------------- |
| **CI Run**              | Exported JSON/log file               | CI provider API export or downloaded artifact |
| **Test Results**        | Test framework JSON/XML output       | `pytest --json`, `jest --json`, JUnit XML     |
| **Coverage Report**     | Coverage tool native format          | `coverage.py json`, Istanbul JSON, lcov       |
| **Code Permalink**      | Raw file content at SHA              | `git show {sha}:{path}` or raw API            |
| **Search Output**       | Tool stdout captured to file         | Redirect: `grep ... > output.txt`             |
| **Diff**                | Git diff output                      | `git diff {base}..{head} > diff.patch`        |
| **SBOM**                | CycloneDX/SPDX JSON                  | SBOM generator output file                    |
| **Attestation**         | Signed attestation file              | Sigstore bundle, GPG signature file           |
| **Cognitive Artifacts** | Markdown/JSON with stripped metadata | Export without editor-specific fields         |

**Canonicalization Rules:**

1. **Export over scrape:** Use API exports or file downloads, not scraped HTML
2. **Deterministic format:** Output format must produce identical bytes for identical content
3. **Strip dynamic elements:** Remove timestamps, session IDs, or other volatile fields before hashing (document what was stripped)
4. **Document the form:** The `canonical_form` field MUST describe how the artifact was canonicalized

**Example Canonical Forms:**

```yaml
# GOOD - CI run exported as JSON via API
canonical_form: "GitHub Actions API JSON export (workflow run endpoint)"
sha256: "abc123..."

# GOOD - Test output captured from framework
canonical_form: "pytest --json-report output file"
sha256: "def456..."

# BAD - HTML page scraped
canonical_form: "Downloaded HTML from CI URL"  # NOT ACCEPTABLE - HTML contains dynamic content
```

**Finding (6.9-F1):** Artifact hash computed on non-canonical form.
**Finding (6.9-F2):** Canonical form not documented.
**Finding (6.9-F3):** Hash verification failed due to dynamic content in canonical form.

### 6.10 Evidence Retention

#### 6.10.1 Default Retention Periods

The following are **default minimum retention periods** for organizations without regulatory requirements. These defaults align with common compliance frameworks:

| Tier | Default Minimum | Rationale                             | Regulatory Alignment      |
| ---- | --------------- | ------------------------------------- | ------------------------- |
| R0   | 90 days         | Sufficient for incident investigation | —                         |
| R1   | 1 year          | Aligns with SOC 2 audit cycles        | SOC 2                     |
| R2   | 3 years         | Aligns with typical contract periods  | ISO 27001                 |
| R3   | 7 years         | Aligns with financial/legal retention | SOX, HIPAA (6yr), PCI-DSS |

#### 6.10.2 Organizational Override

Organizations MAY specify different retention periods in their AIV Policy (§15.1), subject to the following constraints:

| Tier | Minimum Floor | Maximum Ceiling | Override Conditions                                |
| ---- | ------------- | --------------- | -------------------------------------------------- |
| R0   | 30 days       | Unlimited       | Policy documented                                  |
| R1   | 90 days       | Unlimited       | Policy documented                                  |
| R2   | 1 year        | Unlimited       | Policy documented with rationale                   |
| R3   | 3 years       | Unlimited       | Policy documented; regulatory analysis if <7 years |

**NOTE:** Organizations subject to specific regulations (SOX, HIPAA, PCI-DSS, etc.) MUST comply with those regulations regardless of AIV defaults. The AIV defaults are designed for organizations without such requirements.

#### 6.10.3 Retention by Artifact Type

| Tier | Artifacts Covered                                       | Storage Requirements          |
| ---- | ------------------------------------------------------- | ----------------------------- |
| R0   | CI logs, packet                                         | Standard storage with backup  |
| R1   | CI logs, packet, test results                           | Standard storage with backup  |
| R2   | All evidence artifacts                                  | Immutable storage RECOMMENDED |
| R3   | All evidence artifacts, provenance, cognitive artifacts | Immutable storage REQUIRED    |

#### 6.10.4 Storage Requirements for R3

- Artifacts MUST be stored in immutable storage (WORM, Object Lock, or equivalent)
- Access logs MUST be retained for the same period
- Deletion MUST require documented approval and audit trail
- Organizations using override periods <7 years MUST document regulatory analysis justifying the shorter period

**Finding (6.10-F1):** Evidence retention below minimum for tier (or organizational override floor).
**Finding (6.10-F2):** R3 artifacts not in immutable storage.
**Finding (6.10-F3):** Retention override without documented policy.

### 6.11 Evidence File References

Verification packets MAY reference per-file evidence files stored in the repository. Evidence files are per-source-file artifacts containing raw verification data (e.g., test results, AST coverage, downstream impact analysis) that are auto-generated during the development workflow.

#### 6.11.1 Referencing Requirements

Evidence file references MUST include a commit SHA that pins the reference to a specific version of the evidence file, satisfying the immutability requirement of §3.3 via git's content-addressed storage. This ensures the reference resolves to the exact evidence that existed when the packet was created, even if the evidence file is subsequently overwritten.

```yaml
# Example evidence reference in packet identification (§B.1)
evidence_refs:
  - file: "EVIDENCE_LIB_AUDITOR.md"
    commit_sha: "a0280c8"     # Pins this reference to a specific git blob
    classes: [A, B, C]
```

To retrieve the referenced evidence:
```bash
git show a0280c8:.github/aiv-evidence/EVIDENCE_LIB_AUDITOR.md
```

#### 6.11.2 Evidence Files Are Not AIV Packets

Evidence files are NOT AIV Packets. They are artifacts referenced BY packets. Validators MUST NOT validate evidence files against the packet schema (§B.1). Evidence files have their own lifecycle:

- **Mutability:** Evidence files are overwritten each time the corresponding source file is committed. This is intentional — the evidence file always reflects the current state of the source file.
- **History:** Previous versions are preserved in git history. Each version is an immutable git blob.
- **Chain of custody:** Evidence files SHOULD include a `Previous:` header linking to the commit SHA of the prior version, making the evidence chain explicit.

#### 6.11.3 Storage Location

Evidence files SHOULD be stored in a dedicated directory separate from verification packets:

- Evidence files: `.github/aiv-evidence/` (mutable, per-file)
- Verification packets: `.github/aiv-packets/` (immutable, per-change)

This separation makes the mutability contract explicit at the directory level.

**Finding (6.11-F1):** Evidence reference missing commit SHA (not pinned).
**Finding (6.11-F2):** Evidence file validated as packet (wrong schema applied).

---

## 7. Verification Process

### 7.1 Verifier Obligations

For all changes requiring verification (all tiers except where organizational policy explicitly overrides for R0), the Verifier MUST:

| Step  | Obligation                                                 | Output                |
| ----- | ---------------------------------------------------------- | --------------------- |
| 7.1.1 | Confirm Verifier is authorized for this risk tier          | Authorization check   |
| 7.1.2 | Validate risk classification is appropriate                | Classification review |
| 7.1.3 | Validate required evidence classes present for `risk_tier` | Evidence checklist    |
| 7.1.4 | Validate each claim maps to sufficient evidence            | Mapping verification  |
| 7.1.5 | Validate evidence artifacts are immutable per §3.3         | Immutability check    |
| 7.1.6 | Validate evidence artifacts are retrievable                | Retrieval check       |
| 7.1.7 | For R3: Validate artifact hashes match                     | Hash verification     |
| 7.1.8 | Record verification decision with rationale                | Attestation           |

### 7.2 Verification Decision

The Verifier MUST record exactly one decision:

| Decision          | Meaning                                                            | Merge Permitted | Constraints           |
| ----------------- | ------------------------------------------------------------------ | --------------- | --------------------- |
| **COMPLIANT**     | All BLOCK requirements satisfied; WARN items addressed or accepted | Yes             | None                  |
| **CONDITIONAL**   | WARN-severity findings present with remediation plan               | Yes             | See §7.3              |
| **NON-COMPLIANT** | One or more BLOCK-severity findings present                        | No              | Must resolve findings |

### 7.3 Conditional Decision Constraints

**CRITICAL:** A CONDITIONAL decision MUST NOT be used to bypass BLOCK-severity findings.

CONDITIONAL is permitted ONLY when:

1. ALL BLOCK-severity validation rules pass
2. One or more WARN-severity findings exist
3. A remediation plan is documented for each WARN finding
4. Remediation deadline does not exceed 30 days
5. Responsible party is identified for remediation

**Finding (7.3-F1):** CONDITIONAL decision used to bypass BLOCK-severity finding.

### 7.4 Attestation Record

The AIV Packet MUST include a Verifier attestation with the following structure:

```yaml
attestations:
  - id: string # Unique attestation ID
    verifier_id: string # Verifier identity (REQUIRED)
    verifier_identity_type: string # github | email | oidc | etc.
    decision: COMPLIANT | CONDITIONAL | NON-COMPLIANT # (REQUIRED)
    timestamp: ISO-8601 # When attestation was created (REQUIRED)

    # Verification details
    evidence_classes_validated: [A, B, C, D, E, F] # Which classes were checked
    validation_rules_checked: [string] # Rule IDs that were validated
    findings: [Finding] # Any findings discovered

    # Conditional decision details (REQUIRED if CONDITIONAL)
    conditions:
      - finding_id: string
        remediation_plan: string
        remediation_deadline: ISO-8601
        responsible_party: string

    # Non-compliant decision details (REQUIRED if NON-COMPLIANT)
    blocking_findings: [string] # Finding IDs that block merge
    rationale: string # Explanation of non-compliance

    # Cryptographic binding (REQUIRED for R3)
    signature_method: GPG | OIDC | sigstore | unsigned
    signature: string # If signed
    signed_fields: [string] # Which fields are covered by signature
```

**Finding (7.4-F1):** Missing Verifier attestation.
**Finding (7.4-F2):** Attestation incomplete (missing required fields).
**Finding (7.4-F3):** R3 attestation unsigned.

### 7.5 Known Limitations

Every AIV Packet MUST include a `known_limitations` section.

**This section MUST NOT be empty.** If no limitations are identified, it MUST explicitly state: `["No limitations identified. Full evidence coverage achieved for declared scope."]`

Limitations SHOULD include:

- Untested scenarios or edge cases
- Partial coverage areas
- Non-reproducible elements (with justification)
- Deferred validations
- Environmental assumptions

**Finding (7.5-F1):** `known_limitations` field missing or genuinely empty (not explicitly stating none).

---

## 8. Compliance Levels

### 8.1 Level Definitions

| Level  | Name     | Description                                                      | Typical Use                              |
| ------ | -------- | ---------------------------------------------------------------- | ---------------------------------------- |
| **L1** | Baseline | Minimum viable verification; execution and reference evidence    | Low-risk changes, internal tools         |
| **L2** | Standard | Production-grade verification; adds negative and intent evidence | Production changes, customer-facing      |
| **L3** | Assured  | High-assurance verification; full evidence chain with provenance | Critical systems, regulated environments |

### 8.2 Tier-to-Level Minimum Mapping

A change MUST NOT claim a compliance level below its risk tier minimum:

| Risk Tier | Minimum Compliance Level |
| --------- | ------------------------ |
| R0        | L1                       |
| R1        | L1                       |
| R2        | L2                       |
| R3        | L3                       |

**Finding (8.2-F1):** Compliance level below minimum for risk tier.

### 8.3 Level Requirements Matrix

| Requirement                    |   L1    |   L2    |   L3    |
| ------------------------------ | :-----: | :-----: | :-----: |
| **Evidence Classes**           |         |         |         |
| Class A (Execution)            |    ✓    |    ✓    |    ✓    |
| Class B (Referential)          |    ✓    |    ✓    |    ✓    |
| Class C (Negative)             |         |    ✓    |    ✓    |
| Class D (Differential)         |         |         |    ✓    |
| Class E (Intent)               |         |    ✓    |    ✓    |
| Class F (Provenance)           |         |         |    ✓    |
| **Process Controls**           |         |         |         |
| SoD: S1 (Independent Verifier) |         |    ✓    |    ✓    |
| Signed Attestation             |         |         |    ✓    |
| Immutable Storage              |         |         |    ✓    |
| **Retention**                  |         |         |         |
| Minimum Retention              | 90 days | 3 years | 7 years |

---

## 9. Gating Rules

### 9.1 Merge Gate

A change MUST NOT merge if any of the following conditions are true:

| Gate ID | Condition                                                    | Finding |
| ------- | ------------------------------------------------------------ | ------- |
| G-001   | Required evidence classes for risk tier are missing          | 9.1-F1  |
| G-002   | Packet schema validation fails                               | 9.1-F2  |
| G-003   | Any evidence artifact fails immutability requirements (§3.3) | 9.1-F3  |
| G-004   | SoD requirements violated (§5.4)                             | 9.1-F4  |
| G-005   | Verifier attestation missing                                 | 9.1-F5  |
| G-006   | Attestation decision is NON-COMPLIANT                        | 9.1-F6  |
| G-007   | Any BLOCK-severity validation rule fails                     | 9.1-F7  |
| G-008   | Exception invoked but requirements not met (§10)             | 9.1-F8  |

### 9.2 Artifact Immutability Gate

| Rule     | Requirement                                                             |
| -------- | ----------------------------------------------------------------------- |
| G-IMM-01 | Evidence links MUST satisfy immutability criteria (§3.3)                |
| G-IMM-02 | Branch-based links MUST NOT satisfy immutability for any evidence class |
| G-IMM-03 | "Latest" or "current" links MUST NOT satisfy immutability               |
| G-IMM-04 | CI artifacts without retention guarantee MUST NOT satisfy immutability  |
| G-IMM-05 | For R3: All evidence artifacts MUST have verifiable SHA-256 hashes      |

**Finding (9.2-F1):** Mutable artifact reference in required evidence.
**Finding (9.2-F2):** R3 evidence artifact without verifiable hash.

### 9.3 Automated Enforcement [Program]

**Scope:** This section defines Program Requirements, not Per-Change Requirements. These are validated during organizational audits, not per-packet validation.

Organizations SHOULD implement automated gate enforcement via:

- CI/CD pipeline integration
- Branch protection rules
- Policy-as-code validators (e.g., OPA, Kyverno)

Automated enforcement MUST:

- Execute on every PR/MR update
- Block merge on any BLOCK-severity finding
- Produce machine-readable results conforming to §14.2
- Log all gate decisions to audit trail

**Finding (9.3-F1):** [Program] Automated enforcement not implemented for repository.

---

## 10. Exception Protocol

### 10.1 Purpose

The exception protocol (break-glass) exists to handle genuine emergencies where evidence cannot be produced without unacceptable harm. It is NOT a mechanism for bypassing verification on a routine basis.

### 10.2 Exception Conditions

An exception MAY be invoked ONLY when ALL of the following are true:

1. A production incident or security vulnerability requires immediate remediation
2. Delay to produce required evidence would cause measurable harm (downtime, data loss, security exposure)
3. The harm from delay exceeds the risk of reduced verification
4. A Designated Exception Approver (§10.3) authorizes the exception

### 10.3 Designated Exception Approver

Organizations MUST define Designated Exception Approvers in their AIV policy. The designation MUST specify:

| Field                   | Requirement                                                                                   |
| ----------------------- | --------------------------------------------------------------------------------------------- |
| **Role Definition**     | Functional role, not job title (e.g., "On-call incident commander", "Security response lead") |
| **Authorization Scope** | Which risk tiers the role can approve exceptions for                                          |
| **Escalation Path**     | Who approves if the designated approver is unavailable                                        |
| **Audit Requirements**  | What documentation the approver must provide                                                  |

**Minimum authorization requirements:**

| Risk Tier | Minimum Approver Authority                          |
| --------- | --------------------------------------------------- |
| R0-R1     | Team lead or equivalent                             |
| R2        | Engineering manager or security engineer            |
| R3        | Director-level or designated security response lead |

### 10.4 Exception Record

When an exception is invoked, the packet MUST include:

```yaml
exception:
  invoked: true

  # Justification (REQUIRED)
  incident_reference: string # Link to incident ticket/page
  harm_description: string # What harm would delay cause
  harm_severity: string # Quantified impact if possible

  # Approval (REQUIRED)
  approver_id: string # Identity of approver
  approver_role: string # Functional role, not job title
  approval_timestamp: ISO-8601
  approval_method: string # How approval was recorded (Slack, PagerDuty, etc.)

  # Scope (REQUIRED)
  evidence_classes_waived: [A, B, C, D, E, F] # Which classes are incomplete
  validation_rules_waived: [string] # Which rules are not enforced

  # Time bounds (REQUIRED)
  exception_start: ISO-8601
  validity_window_hours: integer # MUST NOT exceed 72
  exception_expires: ISO-8601 # Calculated from start + window

  # Follow-up (REQUIRED)
  follow_up_obligation: string # What must be done within window
  follow_up_deadline: ISO-8601 # MUST be within validity window
  follow_up_owner: string # Identity responsible for follow-up

  # Resolution (populated after exception period)
  resolution_status: pending | completed | reverted
  resolution_timestamp: ISO-8601
  resolution_evidence: string # Link to completed evidence or revert commit
```

### 10.5 Exception Constraints

| Constraint               | Requirement                                                                 |
| ------------------------ | --------------------------------------------------------------------------- |
| **Maximum Duration**     | 72 hours from exception start                                               |
| **Follow-up Obligation** | Missing evidence MUST be produced within window, OR change MUST be reverted |
| **Audit Trail**          | All exception approvals MUST be logged to immutable audit storage           |
| **Reuse Prohibition**    | Same incident MUST NOT justify multiple exceptions for different changes    |
| **Monitoring**           | Active exceptions MUST be visible in operational dashboards                 |

### 10.6 Exception Metrics and Thresholds

Organizations MUST track exception metrics:

| Metric                              | Threshold      | Action                   |
| ----------------------------------- | -------------- | ------------------------ |
| Exception rate (% of R2+ changes)   | >5%            | Process review required  |
| Exception follow-up completion rate | <95%           | Escalation to leadership |
| Average exception duration          | >48 hours      | Process review required  |
| Repeat exception rate (same author) | >2 per quarter | Individual review        |

**Finding (10.6-F1):** Exception invoked without required approvals.
**Finding (10.6-F2):** Exception validity window exceeded without resolution.
**Finding (10.6-F3):** Exception not logged to audit trail.
**Finding (10.6-F4):** Exception rate exceeds threshold without documented review.

---

## 11. Evidence Integrity Controls

### 11.1 Purpose

Evidence integrity controls prevent "verification theater" — situations where packets exist but do not actually prove claims. These controls operate as meta-verification of the verification process itself.

For repositories using per-file evidence files (§6.11), the evidence file's git history constitutes an auditable chain of custody. Each version of the evidence file is an immutable git blob, retrievable via `git show <sha>:<path>`. This satisfies the Content Integrity and Reference Stability requirements of §3.3. Verification packets reference evidence files at specific commit SHAs, ensuring the reference is immutable even though the evidence file itself may be overwritten by subsequent commits.

### 11.2 Required Controls by Tier

| Control ID | Description                           | R0  | R1  | R2  | R3  |
| ---------- | ------------------------------------- | :-: | :-: | :-: | :-: |
| EIC-001    | CI run SHA validation                 |  ✓  |  ✓  |  ✓  |  ✓  |
| EIC-002    | Evidence link immutability validation |  ✓  |  ✓  |  ✓  |  ✓  |
| EIC-003    | Scope-diff consistency check          |     |     |  ✓  |  ✓  |
| EIC-004    | Test integrity validation (semantic)  |     |     |  ✓  |  ✓  |
| EIC-005    | Claim-evidence coverage analysis      |     |     |  ✓  |  ✓  |
| EIC-006    | Artifact hash verification            |     |     |     |  ✓  |
| EIC-007    | Provenance chain validation           |     |     |     |  ✓  |
| EIC-008    | Random reproduction audits            |     |     |     |  ✓  |

### 11.3 Test Integrity Validation

For R2+ changes, test integrity MUST be validated using semantic analysis:

| Validation             | Method                                           | NOT Acceptable           |
| ---------------------- | ------------------------------------------------ | ------------------------ |
| Assertion preservation | AST diff showing no assertion removal            | String grep for "assert" |
| Skip pattern detection | Test framework skip reporting                    | String grep for "@skip"  |
| Coverage comparison    | Coverage tool diff (e.g., coverage.py, Istanbul) | Manual inspection        |
| Test count validation  | Test framework discovery count                   | Line count comparison    |

**Implementation Note:** Organizations MUST use language-appropriate tooling. The AIV-Python and AIV-Node profiles (Appendix F) provide specific tool recommendations.

**Finding (11.3-F1):** Test integrity validation used inadequate method.
**Finding (11.3-F2):** Test integrity degradation detected without justification.

### 11.4 Audit Sampling [Program]

**Scope:** This section defines Program Requirements, not Per-Change Requirements. These are validated during organizational audits, not per-packet validation.

For R3 changes, organizations MUST implement audit sampling:

| Requirement              | Specification                                         |
| ------------------------ | ----------------------------------------------------- |
| **Sampling Rate**        | Minimum 10% of R3 changes per quarter                 |
| **Selection Method**     | Random selection; MUST NOT be author-selected         |
| **Audit Scope**          | Full reproduction of evidence chain                   |
| **Auditor Independence** | Auditor MUST NOT be original Author or Verifier       |
| **Audit Record**         | Findings logged to immutable audit storage            |
| **Remediation**          | BLOCK-severity findings require documented resolution |

**Audit Checklist (per sampled change):**

1. Retrieve all evidence artifacts using only packet references
2. Verify each artifact hash matches packet record
3. Verify CI run executed at recorded commit SHA
4. Verify test results match CI run output
5. Verify negative evidence searches are reproducible
6. Verify requirement reference is retrievable and immutable
7. Verify provenance signatures are valid
8. Document any discrepancies as findings

**Finding (11.4-F1):** [Program] Audit sampling not implemented for R3 changes.
**Finding (11.4-F2):** [Program] Audit sampling rate below 10%.
**Finding (11.4-F3):** [Program] Audit findings not resolved.

---

## 12. Security Considerations

### 12.1 Packet Security

| Risk                       | Mitigation                                                                |
| -------------------------- | ------------------------------------------------------------------------- |
| Packet tampering           | R3 packets MUST be signed; all packets SHOULD be signed                   |
| Secret leakage in evidence | Evidence artifacts MUST be sanitized; secret patterns MUST be redacted    |
| Unauthorized verification  | Verifier identity MUST be validated against authorized list               |
| Replay attacks             | Packet MUST be bound to specific commit SHA; timestamps MUST be validated |

### 12.2 Evidence Security

| Risk                  | Mitigation                                                         |
| --------------------- | ------------------------------------------------------------------ |
| Evidence forgery      | R3 requires cryptographic provenance; CI attestation recommended   |
| Evidence deletion     | Retention policies MUST be enforced; R3 requires immutable storage |
| Evidence substitution | Artifact hashes MUST be recorded and verified                      |
| Link manipulation     | Links MUST be SHA-bound, not branch-based                          |

### 12.3 CI/CD Security

| Risk                  | Mitigation                                                    |
| --------------------- | ------------------------------------------------------------- |
| Compromised CI runner | Use trusted builders; verify OIDC identity; consider SLSA L3+ |
| Log manipulation      | CI logs SHOULD be written to append-only storage              |
| Artifact tampering    | CI artifacts MUST have integrity verification                 |
| Workflow modification | Workflow changes SHOULD require elevated review               |

### 12.4 Secret Scanning

Evidence artifacts MUST NOT contain:

- API keys or tokens
- Passwords or credentials
- Private keys or certificates
- Connection strings with credentials
- PII beyond minimum necessary

Organizations SHOULD implement automated secret scanning on evidence artifacts before packet finalization.

---

## 13. Privacy Considerations

### 13.1 Data Minimization

Evidence artifacts SHOULD contain the minimum data necessary to support claims. Specifically:

- Logs SHOULD be filtered to relevant entries
- Stack traces SHOULD be truncated to relevant frames
- Test output SHOULD exclude verbose debugging
- Screenshots SHOULD be cropped to relevant areas

### 13.2 PII Handling

| Data Type                | Requirement                                   |
| ------------------------ | --------------------------------------------- |
| Test data containing PII | MUST be anonymized or use synthetic data      |
| User identifiers in logs | SHOULD be pseudonymized                       |
| Author/Verifier identity | MAY be retained (necessary for audit)         |
| IP addresses in logs     | SHOULD be anonymized unless security-relevant |

### 13.3 Retention and Deletion

- Retention periods (§6.9) represent MINIMUM retention
- Organizations MAY retain longer if permitted by applicable law
- Deletion requests MUST be handled per applicable privacy regulations
- Audit trails of deletions MUST be maintained

---

## 14. Conformance Testing

### 14.1 Validator Requirements

A conforming AIV validator MUST be able to verify:

| Test ID | Requirement                                                              |
| ------- | ------------------------------------------------------------------------ |
| CT-001  | Packet schema validity (all required fields present and correctly typed) |
| CT-002  | Evidence classes present meet tier requirements                          |
| CT-003  | All evidence artifact references are resolvable                          |
| CT-004  | All evidence artifact references satisfy immutability requirements       |
| CT-005  | CI run SHA matches packet `head_sha`                                     |
| CT-006  | SoD rules are satisfied                                                  |
| CT-007  | Attestation is present and complete                                      |
| CT-008  | Attestation decision is COMPLIANT or CONDITIONAL (for merge)             |
| CT-009  | CONDITIONAL decisions have valid remediation plans                       |
| CT-010  | `known_limitations` field is populated (not empty)                       |
| CT-011  | For R3: All artifact hashes are present and verifiable                   |
| CT-012  | For R3: Provenance signatures are valid                                  |

### 14.2 Validation Output Schema

A conforming validator MUST produce machine-readable output:

```yaml
validation_result:
  # Identification
  validator_id: string # Validator name and version
  packet_id: string # Packet being validated
  repository: string
  pr_id: integer
  head_sha: string
  validated_at: ISO-8601

  # Results
  overall_result: PASS | FAIL
  compliance_level: L1 | L2 | L3 | NON-COMPLIANT
  risk_tier_validated: R0 | R1 | R2 | R3

  # Detailed results
  evidence_class_results:
    - class: A | B | C | D | E | F
      required: boolean
      present: boolean
      valid: boolean
      findings: [Finding]

  validation_rule_results:
    - rule_id: string
      result: PASS | FAIL | SKIP
      finding_id: string # If FAIL

  # Findings
  findings:
    - id: string
      severity: BLOCK | WARN | INFO
      rule_id: string
      description: string
      remediation: string

  # Summary
  block_count: integer
  warn_count: integer
  info_count: integer
```

### 14.3 Conformance Claim Requirements

An organization MAY claim AIV conformance when:

| Requirement                                          | Verification Method |
| ---------------------------------------------------- | ------------------- |
| Validator produces `PASS` for all changes in scope   | Validator logs      |
| Audit sampling shows ≤5% BLOCK-severity finding rate | Audit reports       |
| Exception rate ≤5% of R2+ changes                    | Exception logs      |
| Evidence retention verified                          | Storage audit       |
| Governance controls documented per §15               | Policy documents    |

**Conformance claim format:**

> "[Organization] claims AIV v1.0.0 conformance at Level [L1/L2/L3] for [scope description], validated as of [date], with audit evidence available at [reference]."

---

## 15. Governance and Versioning

### 15.1 Organizational Policy Requirements

Organizations implementing AIV MUST document:

| Policy Element               | Contents                                                     |
| ---------------------------- | ------------------------------------------------------------ |
| **Scope Definition**         | Which repositories/changes are subject to AIV                |
| **Role Assignments**         | Who can serve as Author, Verifier, Exception Approver        |
| **Tool Configuration**       | Which validator(s), CI integration, storage systems          |
| **Exception Authority**      | Designated Exception Approvers by tier                       |
| **Audit Process**            | Sampling methodology, auditor assignment, finding resolution |
| **Retention Implementation** | Where evidence is stored, how retention is enforced          |
| **Training Requirements**    | What training Authors/Verifiers must complete                |

### 15.2 Specification Versioning

AIV specification versions follow Semantic Versioning (SemVer):

- **MAJOR:** Breaking changes to packet schema or evidence class definitions
- **MINOR:** New optional features, new profiles, clarifications
- **PATCH:** Bug fixes, typo corrections, non-normative clarifications

### 15.3 Backward Compatibility

| Change Type                      | Compatibility Guarantee          |
| -------------------------------- | -------------------------------- |
| Evidence Class definitions (A-F) | Stable across all 1.x versions   |
| Packet schema required fields    | Stable across all 1.x versions   |
| Validation rule IDs              | Stable; new rules get new IDs    |
| Finding IDs                      | Stable; new findings get new IDs |
| Profiles                         | May evolve independently         |

### 15.4 Deprecation Policy

- Deprecated features MUST be announced at least one minor version before removal
- Deprecated features MUST include migration guidance
- Removed features MUST increment major version

---

## Appendix A — Auditor Checklist

### A.1 Per-Change Verification Checklist

| #                    | Check                                                  | Evidence Location                         | Pass | Fail | N/A |
| -------------------- | ------------------------------------------------------ | ----------------------------------------- | :--: | :--: | :-: |
| **Classification**   |                                                        |                                           |      |      |
| 1                    | Risk tier assigned                                     | `classification.risk_tier`                |  ☐   |  ☐   |  ☐  |
| 2                    | Risk tier appropriate for change content               | Manual review                             |  ☐   |  ☐   |  ☐  |
| 3                    | Critical surfaces listed if R3                         | `classification.critical_surfaces`        |  ☐   |  ☐   |  ☐  |
| 4                    | Classification rationale documented                    | `classification.classification_rationale` |  ☐   |  ☐   |  ☐  |
| 5                    | SoD mode appropriate for tier                          | `classification.sod_mode`                 |  ☐   |  ☐   |  ☐  |
| **Evidence Classes** |                                                        |                                           |      |      |
| 6                    | Required evidence classes present                      | Per §6.1 matrix                           |  ☐   |  ☐   |  ☐  |
| 7                    | Class A: CI run SHA matches head_sha                   | `evidence_items[class=A]`                 |  ☐   |  ☐   |  ☐  |
| 8                    | Class A: Test results include counts                   | `evidence_items[class=A]`                 |  ☐   |  ☐   |  ☐  |
| 9                    | Class B: All links are SHA-bound                       | `evidence_items[class=B]`                 |  ☐   |  ☐   |  ☐  |
| 10                   | Class B: Scope matches actual diff                     | `evidence_items[class=B]`                 |  ☐   |  ☐   |  ☐  |
| 11                   | Class C: Search scope declared                         | `evidence_items[class=C]`                 |  ☐   |  ☐   |  ☐  |
| 12                   | Class C: Test integrity uses semantic analysis         | `evidence_items[class=C]`                 |  ☐   |  ☐   |  ☐  |
| 13                   | Class D: Covers all touched surfaces (R3)              | `evidence_items[class=D]`                 |  ☐   |  ☐   |  ☐  |
| 14                   | Class E: Requirement reference immutable               | `evidence_items[class=E]`                 |  ☐   |  ☐   |  ☐  |
| 15                   | Class E: Requirements mapped to claims                 | `evidence_items[class=E]`                 |  ☐   |  ☐   |  ☐  |
| 16                   | Class F: Provenance present (R3)                       | `evidence_items[class=F]`                 |  ☐   |  ☐   |  ☐  |
| 17                   | Class F: Artifact hashes present (R3)                  | `evidence_items[class=F]`                 |  ☐   |  ☐   |  ☐  |
| **Attestation**      |                                                        |                                           |      |      |
| 18                   | Verifier attestation present                           | `attestations[]`                          |  ☐   |  ☐   |  ☐  |
| 19                   | Verifier differs from Author (R2+)                     | Identity comparison                       |  ☐   |  ☐   |  ☐  |
| 20                   | Attestation decision is COMPLIANT or valid CONDITIONAL | `attestations[].decision`                 |  ☐   |  ☐   |  ☐  |
| 21                   | Attestation signed (R3)                                | `attestations[].signature`                |  ☐   |  ☐   |  ☐  |
| **Completeness**     |                                                        |                                           |      |      |
| 22                   | Known limitations documented                           | `known_limitations`                       |  ☐   |  ☐   |  ☐  |
| 23                   | All claims have evidence                               | Claim-evidence mapping                    |  ☐   |  ☐   |  ☐  |

### A.2 Program-Level Audit Checklist

| #                  | Check                                 | Evidence Source         | Pass | Fail |
| ------------------ | ------------------------------------- | ----------------------- | :--: | :--: |
| **Implementation** |                                       |                         |      |
| 1                  | AIV validator deployed and running    | CI configuration        |  ☐   |  ☐   |
| 2                  | Merge gates enforced                  | Branch protection rules |  ☐   |  ☐   |
| 3                  | Evidence retention policy implemented | Storage configuration   |  ☐   |  ☐   |
| 4                  | R3 artifacts in immutable storage     | Storage audit           |  ☐   |  ☐   |
| **Process**        |                                       |                         |      |
| 5                  | Audit sampling implemented (R3)       | Audit logs              |  ☐   |  ☐   |
| 6                  | Audit sampling rate ≥10%              | Audit logs              |  ☐   |  ☐   |
| 7                  | Exception process documented          | Policy document         |  ☐   |  ☐   |
| 8                  | Exception approvers designated        | Policy document         |  ☐   |  ☐   |
| **Metrics**        |                                       |                         |      |
| 9                  | Exception rate ≤5%                    | Metrics dashboard       |  ☐   |  ☐   |
| 10                 | Audit finding rate ≤5% BLOCK          | Audit reports           |  ☐   |  ☐   |
| 11                 | Exception follow-up rate ≥95%         | Exception logs          |  ☐   |  ☐   |

---

## Appendix B — Packet Schema

### B.1 Complete Packet Schema

```yaml
# AIV Packet Schema v1.0.0
# This schema is normative. Packets MUST conform to this structure.

aiv_version: "1.0.0" # REQUIRED - AIV spec version
packet_schema_version: "1.0.0" # REQUIRED - This schema version

# ============================================================================
# IDENTIFICATION
# ============================================================================
identification:
  repository: string # REQUIRED - Canonical repo identifier (e.g., "github.com/org/repo")

  # Change identifier — exactly ONE of the following MUST be present:
  pr_id: integer # REQUIRED for PR/MR workflows - PR/MR number
  change_id: string # REQUIRED for direct-to-main workflows - Logical change identifier (e.g., "enforcement-gap-fix")

  pr_url: string # REQUIRED if pr_id present - PR URL as identifier (NOTE: PR content is mutable; evidence artifacts must be immutable per §3.3)
  branch: string # REQUIRED - Source branch name
  base_branch: string # REQUIRED - Target branch name
  head_sha: string # REQUIRED - HEAD commit SHA (40 or 64 hex chars) - THIS is the immutable anchor
  base_sha: string # REQUIRED - Base commit SHA
  commit_range: [string] # RECOMMENDED - All commit SHAs in this change, ordered chronologically
  created_at: ISO-8601 # REQUIRED - Packet creation timestamp
  created_by: string # REQUIRED - Identity creating packet

  # Evidence layer references (§6.11)
  evidence_refs: # RECOMMENDED - References to per-file evidence artifacts
    - file: string # Evidence file name (e.g., "EVIDENCE_LIB_AUDITOR.md")
      commit_sha: string # Commit SHA when evidence was generated (pins the reference per §3.3)
      classes: [A, B, C, D, E, F] # Evidence classes present in this file

# ============================================================================
# CLASSIFICATION (§5)
# ============================================================================
classification:
  risk_tier: R0 | R1 | R2 | R3 # REQUIRED
  sod_mode: S0 | S1 # REQUIRED
  critical_surfaces: # REQUIRED if R3
    - string # List of critical surfaces touched
  blast_radius: local | component | service | cross-service | organization # REQUIRED
  classification_rationale: string # REQUIRED - Explanation of tier assignment
  classified_by: string # REQUIRED - Identity performing classification
  classified_at: ISO-8601 # REQUIRED

# ============================================================================
# CLAIMS
# ============================================================================
claims:
  - id: string # REQUIRED - Stable unique identifier (e.g., "CLM-001")
    type: # REQUIRED - At least one type
      - functional | structural | dependency | interface | security | performance | operational
    statement: string # REQUIRED - Testable assertion
    risk_surfaces: # REQUIRED if security-relevant
      - string # auth | payments | secrets | crypto | pii | data_integrity | api | privilege
    scope:
      files: [string] # Files this claim applies to
      functions: [string] # Functions/methods this claim applies to
    evidence_refs: [string] # REQUIRED - Evidence item IDs supporting this claim

# ============================================================================
# EVIDENCE (§6)
# ============================================================================
evidence_items:
  - id: string # REQUIRED - Unique identifier (e.g., "EV-A-001")
    class: A | B | C | D | E | F # REQUIRED - Evidence class
    description: string # REQUIRED - Human-readable description
    claim_refs: [string] # REQUIRED - Claim IDs this evidence supports

    artifacts: # REQUIRED - At least one artifact
      - type: string # REQUIRED - ci_run | permalink | search_output | diff | attestation | coverage | sbom | etc.
        reference: string # REQUIRED - URL or content-addressed ID
        immutability_mechanism: string # REQUIRED - How immutability is achieved
        canonical_form: string # REQUIRED for R3 - How artifact was canonicalized for hashing (§6.8.1)
        sha256: string # REQUIRED for R3 - SHA-256 hash of canonical form
        retrieved_at: ISO-8601 # REQUIRED - When artifact was retrieved/created
        retention_verified: boolean # SHOULD - Has retention been confirmed

    scope: string # REQUIRED - What this evidence covers
    validation_method: string # REQUIRED - How to verify this evidence
    limitations: [string] # Any known limitations

# ============================================================================
# VERIFICATION (§7)
# ============================================================================
attestations:
  - id: string # REQUIRED - Unique attestation ID
    verifier_id: string # REQUIRED - Verifier identity
    verifier_identity_type: string # REQUIRED - github | email | oidc | corporate_sso
    decision: COMPLIANT | CONDITIONAL | NON-COMPLIANT # REQUIRED
    timestamp: ISO-8601 # REQUIRED

    evidence_classes_validated: # REQUIRED
      - A | B | C | D | E | F
    validation_rules_checked: [string] # REQUIRED - Rule IDs validated

    findings: # REQUIRED - May be empty array
      - id: string
        severity: BLOCK | WARN | INFO
        rule_id: string
        description: string
        remediation: string

    # For CONDITIONAL decisions
    conditions: # REQUIRED if decision is CONDITIONAL
      - finding_id: string
        remediation_plan: string
        remediation_deadline: ISO-8601
        responsible_party: string

    # For NON-COMPLIANT decisions
    blocking_findings: [string] # REQUIRED if decision is NON-COMPLIANT
    rationale: string # REQUIRED if decision is NON-COMPLIANT

    # Cryptographic binding
    signature_method: GPG | OIDC | sigstore | unsigned # REQUIRED
    signature: string # REQUIRED if not unsigned
    signed_fields: [string] # REQUIRED if not unsigned

# ============================================================================
# KNOWN LIMITATIONS (§7.5)
# ============================================================================
known_limitations: # REQUIRED - MUST NOT be empty
  - string # Each limitation as a string
    # If none: ["No limitations identified. Full evidence coverage achieved for declared scope."]

# ============================================================================
# EXCEPTION (§10) - Only if exception invoked
# ============================================================================
exception:
  invoked: boolean # REQUIRED - true if exception active

  # Justification
  incident_reference: string # REQUIRED if invoked
  harm_description: string # REQUIRED if invoked
  harm_severity: string # REQUIRED if invoked

  # Approval
  approver_id: string # REQUIRED if invoked
  approver_role: string # REQUIRED if invoked
  approval_timestamp: ISO-8601 # REQUIRED if invoked
  approval_method: string # REQUIRED if invoked

  # Scope
  evidence_classes_waived: [A, B, C, D, E, F] # REQUIRED if invoked
  validation_rules_waived: [string] # REQUIRED if invoked

  # Time bounds
  exception_start: ISO-8601 # REQUIRED if invoked
  validity_window_hours: integer # REQUIRED if invoked (max 72)
  exception_expires: ISO-8601 # REQUIRED if invoked

  # Follow-up
  follow_up_obligation: string # REQUIRED if invoked
  follow_up_deadline: ISO-8601 # REQUIRED if invoked
  follow_up_owner: string # REQUIRED if invoked

  # Resolution
  resolution_status: pending | completed | reverted # Updated after resolution
  resolution_timestamp: ISO-8601
  resolution_evidence: string

# ============================================================================
# METADATA
# ============================================================================
metadata:
  generator: string # Tool that generated this packet
  generator_version: string
  generation_timestamp: ISO-8601
  packet_hash: string # SHA-256 of packet content (excluding this field)
```

### B.2 Schema Hash

The canonical schema definition above has the following SHA-256 hash for verification:

```
Schema Version: 1.0.0
SHA-256: [To be computed on final publication]
```

Organizations MAY verify schema integrity by computing SHA-256 of the schema YAML above (excluding this B.2 section).

---

## Appendix C — Validation Rules

### C.1 Complete Rule Index

| Rule ID                      | Section | Description                                         | Severity   | Tier               |
| ---------------------------- | ------- | --------------------------------------------------- | ---------- | ------------------ |
| **Classification Rules**     |         |                                                     |            |                    |
| CLS-001                      | §5.1    | Risk tier MUST be assigned                          | BLOCK      | All                |
| CLS-002                      | §5.2    | Change touching critical surface MUST be R3         | BLOCK      | All                |
| CLS-003                      | §5.4    | SoD mode MUST match tier requirements               | BLOCK      | R2+                |
| CLS-004                      | §5.5    | Classification rationale MUST be documented         | WARN       | All                |
| **Class A Rules**            |         |                                                     |            |                    |
| A-001                        | §6.2    | CI run reference MUST be immutable                  | BLOCK      | All                |
| A-002                        | §6.2    | CI run SHA MUST match packet head_sha               | BLOCK      | All                |
| A-003                        | §6.2    | Test results MUST include counts                    | BLOCK      | All                |
| A-004                        | §6.2    | Static analysis N/A MUST be justified               | WARN       | All                |
| A-005                        | §6.2    | CI artifacts MUST be retained per tier              | BLOCK      | All                |
| A-006                        | §6.2    | Test list MUST be reproducible                      | WARN       | All                |
| **Class B Rules**            |         |                                                     |            |                    |
| B-001                        | §6.3    | Code links MUST be SHA-bound                        | BLOCK      | All                |
| B-002                        | §6.3    | Code links MUST include line anchors                | BLOCK/WARN | R2+/R0-R1          |
| B-003                        | §6.3    | Scope inventory MUST match diff                     | BLOCK      | All                |
| B-004                        | §6.3    | Each claim MUST have referential evidence           | BLOCK      | All                |
| B-005                        | §6.3    | Symbol references MUST be valid                     | WARN       | All                |
| **Class C Rules**            |         |                                                     |            |                    |
| C-001                        | §6.4    | Search scope MUST be declared                       | BLOCK      | R2+                |
| C-002                        | §6.4    | Search method MUST be documented                    | BLOCK      | R2+                |
| C-003                        | §6.4    | Patterns MUST be enumerated                         | BLOCK      | R2+                |
| C-004                        | §6.4    | Test integrity MUST use semantic analysis           | BLOCK      | R2+                |
| C-005                        | §6.4    | New skips MUST be justified                         | WARN       | R2+                |
| C-006                        | §6.4    | Coverage decrease MUST be justified                 | WARN       | R2+                |
| **Class D Rules**            |         |                                                     |            |                    |
| D-001                        | §6.5    | Differential evidence MUST cover each surface       | BLOCK      | R3                 |
| D-002                        | §6.5    | Diffs MUST be SHA-bound                             | BLOCK      | R3                 |
| D-003                        | §6.5    | Tools MUST be documented                            | WARN       | R3                 |
| D-004                        | §6.5    | Raw artifacts MUST be available                     | BLOCK      | R3                 |
| D-005                        | §6.5    | SBOM MUST be standard format                        | WARN       | R3                 |
| **Class E Rules**            |         |                                                     |            |                    |
| E-001                        | §6.6    | Requirement reference MUST be immutable             | BLOCK      | R1+                |
| E-002                        | §6.6    | Each requirement MUST map to claim                  | BLOCK      | R1+                |
| E-003                        | §6.6    | Each claim MUST map to evidence                     | BLOCK      | R1+                |
| E-004                        | §6.6    | Acceptance checklist MUST be complete               | WARN       | R1+                |
| E-005                        | §6.6    | Out-of-scope items MUST be justified                | WARN       | R1+                |
| **Class F Rules**            |         |                                                     |            |                    |
| F-001                        | §6.7    | Cryptographic provenance MUST be present            | BLOCK      | R3                 |
| F-002                        | §6.7    | Provenance MUST bind to head_sha                    | BLOCK      | R3                 |
| F-003                        | §6.7    | All artifacts MUST have SHA-256 hashes              | BLOCK      | R3                 |
| F-004                        | §6.7    | Builder identity MUST be documented                 | WARN       | R3                 |
| F-005                        | §6.7    | Unsigned evidence MUST be labeled                   | WARN       | R3                 |
| F-006                        | §6.7    | Artifact hashes MUST be verifiable                  | BLOCK      | R3                 |
| **Class G Rules (Optional)** |         |                                                     |            |                    |
| COG-001                      | §6.8    | Prediction document MUST precede code examination   | BLOCK      | When G implemented |
| COG-002                      | §6.8    | Mental trace MUST reference specific code locations | BLOCK      | When G implemented |
| COG-003                      | §6.8    | Adversarial probe MUST include ≥3 edge cases        | WARN       | When G implemented |
| COG-004                      | §6.8    | Adversarial probe MUST include ≥1 failure mode      | WARN       | When G implemented |
| COG-005                      | §6.8    | Ownership declaration MUST be complete              | BLOCK      | When G implemented |
| **Attestation Rules**        |         |                                                     |            |                    |
| ATT-001                      | §7.4    | Verifier attestation MUST be present                | BLOCK      | All                |
| ATT-002                      | §7.4    | Attestation MUST be complete                        | BLOCK      | All                |
| ATT-003                      | §7.4    | R3 attestation MUST be signed                       | BLOCK      | R3                 |
| ATT-004                      | §7.3    | CONDITIONAL MUST NOT bypass BLOCK findings          | BLOCK      | All                |
| **Gate Rules**               |         |                                                     |            |                    |
| G-001                        | §9.1    | Required evidence classes MUST be present           | BLOCK      | All                |
| G-002                        | §9.1    | Packet schema MUST validate                         | BLOCK      | All                |
| G-003                        | §9.1    | Evidence MUST satisfy immutability                  | BLOCK      | All                |
| G-004                        | §9.1    | SoD MUST be satisfied                               | BLOCK      | R2+                |
| G-005                        | §9.1    | Attestation MUST be present                         | BLOCK      | All                |
| G-006                        | §9.1    | Decision MUST NOT be NON-COMPLIANT                  | BLOCK      | All                |
| **Integrity Rules**          |         |                                                     |            |                    |
| EIC-001                      | §11.2   | CI SHA validation                                   | BLOCK      | All                |
| EIC-002                      | §11.2   | Evidence immutability validation                    | BLOCK      | All                |
| EIC-003                      | §11.2   | Scope-diff consistency                              | BLOCK      | R2+                |
| EIC-004                      | §11.2   | Test integrity validation                           | BLOCK      | R2+                |
| EIC-005                      | §11.2   | Claim-evidence coverage                             | BLOCK      | R2+                |
| EIC-006                      | §11.2   | Artifact hash verification                          | BLOCK      | R3                 |
| EIC-007                      | §11.2   | Provenance chain validation                         | BLOCK      | R3                 |

### C.2 Finding Index

| Finding ID                      | Rule ID   | Description                                              | Scope      |
| ------------------------------- | --------- | -------------------------------------------------------- | ---------- |
| **Classification Findings**     |           |                                                          |            |
| 5.2-F1                          | CLS-002   | Critical surface under-classified                        | Per-Change |
| 5.4-F1                          | CLS-003   | SoD violation                                            | Per-Change |
| 5.4-F2                          | —         | SoD verification method not documented                   | Program    |
| 5.4-F3                          | —         | Cross-platform identity mapping not documented           | Program    |
| 5.5-F1                          | CLS-001   | Missing classification                                   | Per-Change |
| 5.5-F2                          | CLS-004   | Missing classification rationale                         | Per-Change |
| **Class A Findings**            |           |                                                          |            |
| A-F1                            | A-001     | CI run reference not immutable                           | Per-Change |
| A-F2                            | A-002     | CI run SHA mismatch                                      | Per-Change |
| A-F3                            | A-003     | Test results incomplete                                  | Per-Change |
| A-F4                            | A-004     | Static analysis N/A without justification                | Per-Change |
| A-F5                            | A-005     | Artifacts not retained                                   | Per-Change |
| **Class B Findings**            |           |                                                          |            |
| B-F1                            | B-001     | Branch-based code link                                   | Per-Change |
| B-F2                            | B-002     | Missing line anchor                                      | Per-Change |
| B-F3                            | B-003     | Scope mismatch                                           | Per-Change |
| B-F4                            | B-004     | Claim without evidence                                   | Per-Change |
| B-F5                            | B-005     | Invalid symbol reference                                 | Per-Change |
| **Class C Findings**            |           |                                                          |            |
| C-F1                            | C-001     | Search scope not declared                                | Per-Change |
| C-F2                            | C-002     | Search method not documented                             | Per-Change |
| C-F3                            | C-003     | Patterns not enumerated                                  | Per-Change |
| C-F4                            | C-004     | Inadequate test integrity method                         | Per-Change |
| C-F5                            | C-005/006 | Unjustified test degradation                             | Per-Change |
| **Class D Findings**            |           |                                                          |            |
| D-F1                            | D-001     | Missing differential for surface                         | Per-Change |
| D-F2                            | D-002     | Diff not SHA-bound                                       | Per-Change |
| D-F3                            | D-004     | Raw artifacts unavailable                                | Per-Change |
| D-F4                            | D-005     | Non-standard SBOM format                                 | Per-Change |
| **Class E Findings**            |           |                                                          |            |
| E-F1                            | E-001     | Mutable requirement reference (L3: BLOCK)                | Per-Change |
| E-F1a                           | E-001     | Mutable requirement reference at L3                      | Per-Change |
| E-F1b                           | E-001     | Mutable requirement at L1/L2 without snapshot obligation | Per-Change |
| E-F2                            | E-002     | Unmapped requirement                                     | Per-Change |
| E-F3                            | E-003     | Claim without evidence mapping                           | Per-Change |
| E-F4                            | E-004     | Incomplete acceptance checklist                          | Per-Change |
| E-F5                            | E-005     | Unjustified out-of-scope                                 | Per-Change |
| E-F6                            | —         | Snapshot obligation not fulfilled                        | Per-Change |
| **Class F Findings**            |           |                                                          |            |
| F-F1                            | F-001     | No provenance mechanism                                  | Per-Change |
| F-F2                            | F-002     | Provenance not SHA-bound                                 | Per-Change |
| F-F3                            | F-003     | Missing artifact hash                                    | Per-Change |
| F-F4                            | F-006     | Hash verification failed                                 | Per-Change |
| F-F5                            | F-004     | Builder identity not documented                          | Per-Change |
| **Class G Findings (Optional)** |           |                                                          |            |
| G-F1                            | COG-001   | Prediction document timestamp after code examination     | Per-Change |
| G-F2                            | COG-002   | Mental trace lacks specific code references              | Per-Change |
| G-F3                            | COG-003   | Adversarial probe insufficient (<3 edge cases)           | Per-Change |
| G-F4                            | COG-004   | Adversarial probe lacks failure mode analysis            | Per-Change |
| G-F5                            | COG-005   | Ownership declaration incomplete                         | Per-Change |
| **Canonicalization Findings**   |           |                                                          |            |
| 6.9-F1                          | —         | Artifact hash computed on non-canonical form             | Per-Change |
| 6.9-F2                          | —         | Canonical form not documented                            | Per-Change |
| 6.9-F3                          | —         | Hash verification failed due to dynamic content          | Per-Change |
| **Attestation Findings**        |           |                                                          |            |
| 7.3-F1                          | ATT-004   | CONDITIONAL bypassing BLOCK                              | Per-Change |
| 7.4-F1                          | ATT-001   | Missing attestation                                      | Per-Change |
| 7.4-F2                          | ATT-002   | Incomplete attestation                                   | Per-Change |
| 7.4-F3                          | ATT-003   | R3 attestation unsigned                                  | Per-Change |
| 7.5-F1                          | —         | Empty known_limitations                                  | Per-Change |
| **Compliance Findings**         |           |                                                          |            |
| 8.2-F1                          | —         | Compliance level below tier minimum                      | Per-Change |
| **Gate Findings**               |           |                                                          |            |
| 9.1-F1                          | G-001     | Missing required evidence class                          | Per-Change |
| 9.1-F2                          | G-002     | Schema validation failure                                | Per-Change |
| 9.1-F3                          | G-003     | Immutability failure                                     | Per-Change |
| 9.1-F4                          | G-004     | SoD violation                                            | Per-Change |
| 9.1-F5                          | G-005     | Missing attestation                                      | Per-Change |
| 9.1-F6                          | G-006     | NON-COMPLIANT decision                                   | Per-Change |
| 9.2-F1                          | G-003     | Mutable artifact reference                               | Per-Change |
| 9.2-F2                          | EIC-006   | R3 artifact without hash                                 | Per-Change |
| 9.3-F1                          | —         | Automated enforcement not implemented                    | Program    |
| **Exception Findings**          |           |                                                          |            |
| 10.6-F1                         | —         | Exception without approval                               | Per-Change |
| 10.6-F2                         | —         | Exception window exceeded                                | Per-Change |
| 10.6-F3                         | —         | Exception not logged                                     | Program    |
| 10.6-F4                         | —         | Exception rate exceeded                                  | Program    |
| **Integrity Findings**          |           |                                                          |            |
| 11.3-F1                         | EIC-004   | Inadequate test integrity method                         | Per-Change |
| 11.3-F2                         | EIC-004   | Test degradation without justification                   | Per-Change |
| 11.4-F1                         | EIC-008   | No audit sampling                                        | Program    |
| 11.4-F2                         | EIC-008   | Audit rate below 10%                                     | Program    |
| 11.4-F3                         | EIC-008   | Unresolved audit findings                                | Program    |
| **Retention Findings**          |           |                                                          |            |
| 6.10-F1                         | —         | Retention below minimum                                  | Program    |
| 6.10-F2                         | —         | R3 artifacts not in immutable storage                    | Program    |
| 6.10-F3                         | —         | Retention override without policy                        | Program    |

---

## Appendix D — Finding Severity Taxonomy

### D.1 Severity Definitions

| Severity  | Definition                                                   | Merge Impact                     | Metrics Impact             |
| --------- | ------------------------------------------------------------ | -------------------------------- | -------------------------- |
| **BLOCK** | Violation of MUST/MUST NOT requirement that cannot be waived | Merge prohibited                 | Counts toward finding rate |
| **WARN**  | Violation of SHOULD/SHOULD NOT that requires justification   | Merge permitted with CONDITIONAL | Counts toward finding rate |
| **INFO**  | Observation or recommendation                                | No impact                        | Does not count             |

### D.2 Finding Rate Calculation

The finding rate for conformance metrics is calculated as:

```
finding_rate = (changes_with_BLOCK_or_WARN_findings / total_changes_audited) × 100
```

Where:

- `changes_with_BLOCK_or_WARN_findings` = count of audited changes with at least one BLOCK or WARN finding
- `total_changes_audited` = count of changes in audit sample
- INFO findings are excluded from rate calculation

### D.3 Threshold Definitions

| Metric                   | Calculation                 | Conformance Threshold      |
| ------------------------ | --------------------------- | -------------------------- |
| **Finding Rate**         | Per D.2                     | ≤5% for conformance claim  |
| **Exception Rate**       | exceptions / R2+ changes    | ≤5% for conformance claim  |
| **Follow-up Completion** | resolved / total exceptions | ≥95% for conformance claim |

---

## Appendix E — Immutability Mechanisms

### E.1 Acceptable Mechanisms

This appendix provides implementation guidance for achieving artifact immutability per §3.3.

#### E.1.1 Git Commit SHA Binding

**Mechanism:** Reference artifacts by commit SHA, not branch name.

**Implementation:**

```
# NOT ACCEPTABLE (mutable)
https://github.com/org/repo/blob/main/src/file.py

# ACCEPTABLE (immutable)
https://github.com/org/repo/blob/abc123def456.../src/file.py#L10-L20
```

**Verification:** Git commit SHAs are cryptographically bound to content; modification changes the SHA.

**Limitations:** Does not prevent repository deletion; requires retention policy.

#### E.1.2 Content-Addressed Storage

**Mechanism:** Store artifacts in content-addressed storage where the identifier is derived from content hash.

**Implementation:**

```
# OCI Registry with digest
registry.example.com/artifacts@sha256:abc123...

# IPFS
ipfs://QmXyz...

# Git LFS with SHA
git-lfs://sha256:abc123...
```

**Verification:** Retrieve artifact, compute hash, compare to identifier.

**Limitations:** Requires access to storage system; does not prevent deletion without retention policy.

#### E.1.3 Signed Attestations

**Mechanism:** Cryptographically sign artifact with key controlled by trusted party.

**Implementation:**

```yaml
# Sigstore (Cosign)
cosign verify --key cosign.pub artifact.tar.gz

# GPG
gpg --verify artifact.tar.gz.sig artifact.tar.gz

# In-toto
in-toto-verify --layout layout.json --layout-keys key.pub
```

**Verification:** Verify signature against trusted public key.

**Limitations:** Requires key management; signature proves creation, not prevention of deletion.

#### E.1.4 WORM Storage

**Mechanism:** Store artifacts in Write-Once-Read-Many storage with retention lock.

**Implementation:**

```
# AWS S3 Object Lock
aws s3api put-object-retention --bucket artifacts --key evidence/packet.json \
  --retention '{"Mode":"GOVERNANCE","RetainUntilDate":"2028-01-01"}'

# Azure Immutable Blob
az storage blob immutability-policy set --container artifacts --name packet.json \
  --expiry-time 2028-01-01 --policy-mode Locked
```

**Verification:** Storage policy prevents modification; audit logs show no changes.

**Limitations:** Requires cloud provider; retention must exceed AIV retention requirement.

#### E.1.5 Hash Manifest

**Mechanism:** Record SHA-256 hash in packet; store artifact separately.

**Implementation:**

```yaml
artifacts:
  - reference: "https://ci.example.com/jobs/12345/artifacts/report.html"
    sha256: "abc123def456..."
```

**Verification:** Retrieve artifact, compute SHA-256, compare to recorded hash.

**Limitations:** Does not prevent artifact deletion; requires artifact to remain available.

### E.2 Immutability Verification Checklist

| Check               | Pass Criteria                                                   |
| ------------------- | --------------------------------------------------------------- |
| Content Integrity   | Hash/signature verification succeeds                            |
| Reference Stability | Same URL/ID resolves to same content across multiple retrievals |
| Deletion Protection | Documented retention policy covers AIV retention period         |
| Verification Method | At least one verification method is documented and executable   |

### E.3 Requirement Reference Immutability

For Class E (Intent Evidence), requirement references require special handling because most issue trackers are mutable by default.

#### E.3.1 Acceptable Approaches

| Approach             | Implementation                                            | Verification         |
| -------------------- | --------------------------------------------------------- | -------------------- |
| **Spec-in-Repo**     | Requirements as markdown in repo; reference by commit SHA | Git SHA verification |
| **Issue Snapshot**   | Export issue to PDF/JSON; store with hash; reference hash | Hash comparison      |
| **Versioned Issue**  | Use issue tracker versioning; reference version ID        | Version retrieval    |
| **External Archive** | Archive requirement to Wayback Machine or similar         | Archive retrieval    |

#### E.3.2 NOT Acceptable

| Reference Type         | Why Not Acceptable                    |
| ---------------------- | ------------------------------------- |
| Mutable issue URL      | Content can change after verification |
| "Latest" document link | Content changes over time             |
| Branch-based spec file | Content changes with branch           |
| Verbal agreement       | No artifact to verify                 |

---

## Appendix F — Profiles and Extensions

### F.1 Profile Framework

AIV MAY be extended via **Profiles** that provide language-specific, framework-specific, or industry-specific guidance.

#### F.1.1 Profile Constraints

Profiles MUST NOT:

- Redefine Evidence Classes A–G
- Reduce minimum requirements for any tier
- Remove required fields from packet schema
- Weaken validation rules
- Make Class G required for L1/L2 (only AIV-Regulated profile may require Class G universally)

Profiles MAY:

- Add sub-requirements to evidence classes
- Specify recommended tools for evidence generation
- Define language-specific test integrity checks
- Add additional evidence artifacts
- Define industry-specific critical surfaces
- Extend Class G with domain-specific requirements (see F.3)

#### F.1.2 Profile Structure

```yaml
profile:
  id: string # e.g., "AIV-Python"
  name: string
  version: string
  aiv_version_compatibility: string # e.g., ">=1.0.0"
  scope: string # What this profile applies to

  # Additional requirements
  evidence_class_extensions:
    A:
      additional_artifacts: []
      recommended_tools: []
    C:
      test_integrity_tools: []
      patterns: []

  # Additional critical surfaces
  critical_surfaces: []

  # Tool recommendations
  tooling:
    ci_integration: []
    static_analysis: []
    coverage: []
```

### F.2 Registered Profiles

| Profile ID    | Name                  | Scope               | Status  |
| ------------- | --------------------- | ------------------- | ------- |
| AIV-Python    | Python Profile        | Python projects     | Draft   |
| AIV-Node      | Node.js Profile       | Node.js projects    | Draft   |
| AIV-Go        | Go Profile            | Go projects         | Planned |
| AIV-Java      | Java Profile          | Java projects       | Planned |
| AIV-Data      | Data Pipeline Profile | Data/ML pipelines   | Planned |
| AIV-Regulated | Regulated Industries  | SOX, HIPAA, PCI-DSS | Planned |

### F.3 Class G — Cognitive Evidence Profiles

**Status:** Class G is now defined in the main specification (§6.8). This appendix describes Profile extensions for Class G.

Class G is optional for all compliance levels (L1–L3). Profiles MAY extend Class G with language-specific or industry-specific cognitive verification requirements.

#### F.3.1 Profile Extensions for Class G

Profiles extending Class G MAY specify:

| Extension Type                  | Description                                      | Example                          |
| ------------------------------- | ------------------------------------------------ | -------------------------------- |
| **Framework-Specific Traces**   | Mental trace format for specific frameworks      | React component lifecycle trace  |
| **Domain-Specific Edge Cases**  | Required adversarial probes for domain           | Financial calculation edge cases |
| **Industry-Specific Ownership** | Additional ownership attestations                | Regulated industry sign-offs     |
| **Tooling Requirements**        | Recommended tools for cognitive artifact capture | IDE plugins, timestamp services  |

#### F.3.2 Class G Applicability by Profile

| Profile       | Class G Requirement                    |
| ------------- | -------------------------------------- |
| AIV-Python    | RECOMMENDED for R3; Optional otherwise |
| AIV-Node      | RECOMMENDED for R3; Optional otherwise |
| AIV-Regulated | REQUIRED for all tiers                 |
| AIV-Data      | RECOMMENDED for ML model changes       |

#### F.3.3 Future Enhancements (Planned for v1.1+)

- Verifier scoring / ELO ratings based on audit sampling
- Cognitive artifact quality metrics
- Automated coherence checking for mental traces
- Cross-change cognitive continuity tracking

Organizations requiring enhanced cognitive verification assurance SHOULD implement §6.8 and monitor profile development.

### F.4 Extension: R4 — Regulated Tier (Preview)

**Status:** Planned for AIV-Regulated Profile

R4 extends AIV for environments subject to regulatory compliance (SOX, HIPAA, PCI-DSS, etc.).

#### F.4.1 Proposed R4 Requirements

| Requirement         | Description                                   |
| ------------------- | --------------------------------------------- |
| Class G (Cognitive) | REQUIRED (per §6.8)                           |
| S2 SoD              | Independent Verifier + Specialist Attestation |
| Dual Control        | Two independent verifiers required            |
| Retention           | 10+ years                                     |
| Audit Sampling      | 25% minimum                                   |
| External Audit      | Annual third-party audit                      |

---

## Document History

| Version | Date       | Changes         |
| ------- | ---------- | --------------- |
| 1.0.0   | 2025-01-07 | Initial release |

---

## Acknowledgments

This standard incorporates concepts and aligns with practices from:

- SLSA (Supply-chain Levels for Software Artifacts)
- SOC 2 Trust Services Criteria
- NIST Secure Software Development Framework (SSDF)
- OpenSSF Security Scorecards
- ISO/IEC 27001:2022

---

## Contact

For questions, feedback, or contributions to this specification:

- **Specification Repository:** [To be established]
- **Issue Tracker:** [To be established]
- **Mailing List:** [To be established]

---

**End of AIV Canonical Specification v1.0.0**
