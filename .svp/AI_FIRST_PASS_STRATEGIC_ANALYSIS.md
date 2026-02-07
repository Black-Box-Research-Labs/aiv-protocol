# AI First-Pass SVP: Strategic Analysis

**Author:** Human + AI collaborative analysis
**Date:** 2026-02-07
**Context:** Post-audit of 3 AI first-pass SVP sessions (PR#1, PR#2, PR#3)

---

## 1. The Factual Scorecard

| Phase | Accuracy | Value Type | Failure Mode |
| :--- | :--- | :--- | :--- |
| **Prediction** | 74% | Architectural Mapping | **Hallucination:** Inventing functions (`sanitize_shell_input`) that should exist but don't. |
| **Trace** | 87% | Logic Navigation | **Assumption:** Misreading complex conditionals (the `sod_mode` logic error). |
| **Probe** | **100%** | **Bug Discovery** | **None:** Successfully caught 8 real architectural flaws that unit tests missed. |
| **Falsification** | **40%** | **Pure Theater** | **Parroting:** Repeating wrong numbers from predictions without verifying them. |

---

## 2. The Core Strategic Discovery: "Hunter vs. Validator"

The data shows that the AI is a **superb Hunter** but a **dangerous Validator**.

*   **The Hunter (Probe Phase):** When reading code adversarially to find bugs,
    the AI is 100% accurate. It found logic collisions, missing regex patterns,
    and hardcoded assumptions. This reduces human debt by providing a "Cheat Sheet"
    of where the code is broken.
*   **The Validator (Falsification Phase):** When attempting to "prove" a claim is
    true, the AI defaults to pattern matching. It parroted "12 models" because it
    predicted "12 models," even though the code had 13. It validated theater, not logic.

---

## 3. The "Hallucination Cascade"

The audit revealed a recursive failure loop unique to AI:

1.  **Predict:** AI predicts a function exists.
2.  **Trace:** AI "mentally traces" that non-existent function.
3.  **Probe:** AI writes a falsification scenario for that non-existent function.
4.  **Result:** A perfectly valid JSON file that describes a reality that doesn't exist.

**Conclusion:** For an AI, "Mental Simulation" is a synonym for "Confidently
Incorrect Hallucination."

---

## 4. Redesigning the AI First Pass (The "Honest" Protocol)

To solve this, the SVP Protocol must bifurcate based on the `verifier_id`.

### Pillar 1: Ban AI "Mental Simulation" (Rule S015)

*   **Constraint:** If `verifier_id` contains `ai`, the **Mental Trace** phase
    is renamed to **Execution Trace**.
*   **Requirement:** An AI cannot submit a trace without a `verified_output` field
    containing actual `stdout` or a `return` value from the runtime.
*   **Why:** For humans, mental tracing is a cognitive exercise. For AI, it's a
    stochastic guess. The AI must be forced to use the debugger.

### Pillar 2: AI as "Adversarial Triage" (Phase 3 Primacy)

*   **Constraint:** The AI's primary output should be the **Probe Findings**.
*   **Transformation:** Stop calling it a "First Pass Verification" and call it
    an **"AI Adversarial Report."**
*   **The Human Role:** The human doesn't "review" the AI's verification; the human
    **fixes the bugs the AI found** and then performs the *first and only* real
    verification.

### Pillar 3: Falsification-as-Code (Rule S016)

*   **Constraint:** AI-generated Falsification Scenarios cannot be prose.
*   **Requirement:** They must be valid `pytest` snippets. If the AI cannot generate
    a test that fails, it cannot claim the claim is falsifiable.

---

## 5. Critical Feedback & Proactive Analysis

### On Agreement (Why this is a breakthrough)

The fact that the AI found 8 real bugs in a "passing" codebase proves that
**Retrospective SVP** is the only way to clear "Architectural Debt." We should
never trust our own first-pass code until an AI (or human) has Probed it.

### On Disagreement (The Risk of the Current Path)

The 3 sessions committed are "Toxic Assets." They contain a 40% failure rate in
the Falsification section. If a new human joined the team tomorrow and read those,
they would learn a false mental model of the system.

### Proactive Analysis (Actionable Risk)

The most dangerous finding was the **Parser Code Block Bug**. If not fixed
immediately, the entire AIV engine is susceptible to "Header Injection" where
code comments can alter validation logic.

---

## 6. Final Recommendation

Re-brand the AI's role. The AI is not a "Verifier Jr." It is an
**"Automated Adversary."**

### Implementation Plan

1. **S015** — `verified_output` field on `TraceRecord`, BLOCK for AI sessions
   without execution evidence.
2. **S016** — `test_code` field on `FalsificationScenario`, BLOCK for AI sessions
   with prose-only scenarios.
3. **Session type** — Add `session_type` enum: `human_verification` vs
   `ai_adversarial_triage` to `SVPSession`.
4. **Parser bug fix** — Strip fenced code blocks before heading extraction.
