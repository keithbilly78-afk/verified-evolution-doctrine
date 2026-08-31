# Verified Evolution Doctrine v2.1 — Reference Implementation & Validation Framework

⚠️ **EXPERIMENTAL RESEARCH ARCHITECTURE** ⚠️

This repository contains reference implementations and validation protocols for the **Verified Evolution Doctrine v2.1**, a structural standard for high-assurance systems. **This is NOT production safety certification.** All formulas, thresholds, V-layer implementations, and experimental success criteria are testable hypotheses. Passing tests yield `PROMOTION_CANDIDATE` labels only, pending independent peer review and domain-specific deployment validation.

---

## Governance Doctrine

```
[Observe] ➔ [Understand] ➔ [Verify] ➔ [Authorize] ➔ [Act] ➔ [Confirm] ➔ [Evolve]
                                                                      │
                                                            (Return to Rest State)
```

**Bidirectional Truth:**
- **Forward to justify:** Every action must prove its necessity.
- **Backward to challenge:** Every justification must trace to legitimate intent.
- **Reality to confirm:** Expectations must reconcile against actual outcomes.

**Build down to truth. Act through justified authority. Test both directions against reality. Evolve up through evidence.**

---

## Core Principle

Learning velocity must not imply authority velocity.

The **Stable Core** evolves slowly and only through:
- Stronger evidence
- Explicit authority
- Regression proof
- Recertification

The perimeter may experiment continuously, but evolution of core structures requires rigorous, bidirectional validation constraints.

**Resolve locally. Escalate uncertainty, not everything.**

---

## The Canonical V-Layer Deep-Assurance Model (V1–V12)

V1–V12 defines the canonical deep-assurance model. A consequential operation must satisfy the assurance contracts relevant to its consequence and dependencies; implementations should not wake or traverse irrelevant layers merely to satisfy numbering.

Domain-specific controls (cryptographic proof, uncertainty localization, physical confirmation, correlation analysis, baseline locking) are implemented as **controls/tests associated with appropriate layers**, not as replacements for canonical meanings.

| Layer | Canonical Meaning | Typical Controls & Tests |
|-------|-------------------|---------------------------|
| **V1** | Identity | Who/what initiated this? Authenticate source. |
| **V2** | Truth | What facts are claimed? Establish via proof. |
| **V3** | Eligibility | Is participation/action permitted under applicable rules, conditions, jurisdiction, or policy? |
| **V4** | Intent | What exactly was requested? Bind the consequential action to explicit intent and detect ambiguity. |
| **V5** | Evidence | What data supports the claim? Measure freshness; validate chain. |
| **V6** | Authority | What legitimate power justifies this action? Trace backward lineage. |
| **V7** | Execution | Do the smallest necessary thing. Minimize state mutation. |
| **V8** | Confirmation | What actually happened? Measure physical/deterministic reality. |
| **V9** | Reconciliation | Do outcomes match expectations? Analyze deltas; log mismatches. |
| **V10** | Projection | What should downstream views, models, or consumers know about verified state? Projections represent truth; they do not own or manufacture truth. |
| **V11** | Continuity | Does the change preserve system coherence? Cross-layer consistency. |
| **V12** | Evolution / Rest | Should the baseline evolve? Recertify or return to rest state. |

---

## Resource Allocation Hypothesis (v2.1)

⚠️ This formula is a **research hypothesis**, not an established law. It is configurable by domain.

```
SpendBudget = B₀ + Φ × f(C, U, Aₑ, Dₒ)
```

**Where:**
- **B₀** — Minimum inspection budget (ensures baseline observation even when consequence/uncertainty is low)
- **Φ** — Global scaling factor (hardware capacity or cloud credit ceiling)
- **f(C, U, Aₑ, Dₒ)** — Bounded, saturating function (never returns values that would exceed configured limits)
  - **C** (Consequence Vector): `w₁ · BlastRadius_norm + w₂ · Irreversibility_cost`, bounded `[0.0, 1.0]`
  - **U** (Uncertainty Coefficient): `[H(Observation) / H_max] × (1 - Confidence_source)`, bounded `[0.0, 1.0]`
  - **Aₑ** (Evidence Decay): `1 + λ × [(t_current - t_last_verified) / τ]`, saturates at configurable max
  - **Dₒ** (Observed Drift): `1 + D_KL(P_baseline ∥ P_current)`, saturates at configurable max

**Historical reference:** v2.0 used pure multiplicative form `Φ × (C · U · Aₑ · Dₒ)`. v2.1 adds minimum budget and saturation bounds.

---

## 4-Stage Verification Vice-Versa Protocol (4VP)

Enhanced reconciliation requirement (stronger than invariant_breached check):

**Stage 1: Backward Challenge**
- ✓ Independently established deficiency or opportunity documented
- ✓ Legitimate intent and authority lineage verified
- ✓ Requester traces back to trusted user or system authorization

**Stage 2: Sandboxed Execution**
- ✓ Payload runs in isolated test environment
- ✓ No side effects on production state
- ✓ Telemetry captured throughout

**Stage 3: Forward Promise Verification**
- ✓ Measured improvement materializes
- ✓ Meets or exceeds minimum_expected_gain threshold
- ✓ All protected dimensions within regression budget

**Stage 4: Reconciliation Equality (Strengthened)**
- ✓ Independently confirm outcome via external or deterministic measurement
- ✓ Deficiency closure threshold met (configurable per domain)
- ✓ Protected-dimension regression budgets respected:
  - Latency (p99)
  - Recovery time
  - Security surface
  - Authority audit trail completeness
  - Confirmation fidelity
  - Reconciliation verifiability
- ✓ All V-layer invariants preserved
- ✓ Baseline recertification explicit (not implicit)

**Outcomes:**
- ✅ **PROMOTION_CANDIDATE** — Passed applicable 4VP, V-layer, regression, authority, confirmation, and reconciliation requirements; ready for peer review & domain-specific validation
- ❌ **REJECTED** — Failed one or more requirements; rejection log includes quantitative evidence
- ❓ **UNKNOWN** — Inconclusive; must never silently become approval; requires explicit re-evaluation

---

## Documentation

- **[DOCTRINE_v2.1.md](docs/DOCTRINE_v2.1.md)** — Complete standard specification
- **[V_LAYERS.md](docs/V_LAYERS.md)** — V1–V12 canonical definitions with domain-specific controls
- **[FALSIFICATION_PLAN.md](FALSIFICATION_PLAN.md)** — 8 attack vectors & success criteria
- **[LOGGING_SPEC.md](LOGGING_SPEC.md)** — Evolution decision log and rejection log formats

---

## Quick Start

### Install
```bash
git clone https://github.com/keithbilly78-afk/verified-evolution-doctrine
cd verified-evolution-doctrine
pip install -e .
```

### Run All Tests
```bash
pytest tests/ -v --tb=short
```

### Run Falsification Tests Only
```bash
pytest tests/test_falsification_*.py -v
```

---

## License

Apache License 2.0 — See LICENSE file.

---

**Status:** 🔬 Research Phase — Not production safety certified.

All formulas, thresholds, V-layer implementations, and experimental success criteria are testable hypotheses.