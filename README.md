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
|-------|-------------------|--------------------------|
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

## Baseline Anchoring (Drift Detection)

**Canonical baseline is a locked reference, not a moving average.**

- Recent observations may **propose** candidate baselines
- Candidate baselines cannot **silently replace** the long-horizon verified baseline
- Baseline updates require:
  - Explicit consequence-gated approval
  - Fresh evidence (passes V5 Evidence layer)
  - V12 Evolution layer recertification
  - Quantitative reason, approving authority, evidence references, previous baseline, candidate baseline, and rollback boundary recorded in an immutable or tamper-evident evolution decision log

Every observation is compared against:
1. **Recent state** (local context, short-window anomaly detection)
2. **Locked long-horizon anchor** (foundational baseline, prevents "boiling frog" drift)

Cumulative drift measured continuously; promotion blocked if drift exceeds configured material threshold before anchor recertification.

---

## Framework Validation vs. Candidate Validation

### Framework Validation

The reference implementation should survive the applicable **eight adversarial/falsification protocols**:
1. Slow-drift / boiling-frog
2. Baseline poisoning
3. Spoofed intent with valid credentials
4. Partial improvement
5. Local-vs-global correlation
6. Stale consensus
7. Controller overhead
8. Recovery/evolution confusion

Passing framework tests validates the structural approach; it does not establish universal validity.

### Candidate Validation

An individual candidate must pass its **applicable 4VP, V-layer, regression, authority, confirmation, and reconciliation requirements** based on:
- Consequence profile
- Domain dependencies
- Regulatory or operational context

A candidate does not necessarily need to execute all eight framework attack suites on every promotion attempt unless the domain profile requires them.

---

## Logging & Decision Records

**Evolution Decision Log (Immutable/Tamper-Evident):**
- Baseline updates recorded with:
  - Quantitative reason
  - Approving authority
  - Evidence references
  - Previous baseline snapshot
  - Candidate baseline snapshot
  - Rollback boundary definition
  - Timestamp and cryptographic signature (if deployed)

**Rejection Log (Candidate Failures):**
- Candidates that fail 4VP, V-layer checks, or regression budgets
- Quantitative evidence of failure
- V-layer trace and decision point
- Timestamp and requesting authority

**Unknown / Inconclusive Log:**
- Candidates with indeterminate results
- Reason for inconclusiveness
- Required re-evaluation or domain-specific decision criteria
- Must never auto-promote

---

## Repository Structure

```
verified-evolution-doctrine/
├── docs/
│   ├── DOCTRINE_v2.1.md           # Complete standard specification
│   ├── LIFECYCLE.md               # 7-stage lifecycle detailed walkthrough
│   ├── OPERATIONAL_LAWS.md        # 5 core constraints
│   ├── RESOURCE_CALCULUS.md       # v2.1 formula with saturation & B₀
│   ├── V_LAYERS.md                # V1–V12 canonical definitions & controls
│   └── 4VP_RECONCILIATION.md      # Strengthened 4-stage protocol
├── src/
│   ├── sandbox_engine.py          # VerificationSandboxEngine (4VP enhanced)
│   ├── drift_detection.py         # Long-horizon baseline anchoring
│   ├── consequence_calculus.py    # Resource allocation (v2.1 formula)
│   ├── intent_authority.py        # Intent (V4) vs. credentials separation
│   ├── protection_budgets.py      # Multi-dimensional regression protection
│   ├── correlation_analysis.py    # Cross-component fault correlation
│   ├── evidence_tracker.py        # Freshness & decay management (V5)
│   ├── controller_instrumentation.py  # Overhead measurement
│   ├── v_layer_checks.py          # V1–V12 assurance contract validators
│   ├── recovery_evolution_fsm.py  # State machine separation
│   └── logging_systems.py         # Evolution decision log & rejection log
├── tests/
│   ├── test_falsification_1_drift.py
│   ├── test_falsification_2_baseline.py
│   ├── test_falsification_3_spoofed_intent.py
│   ├── test_falsification_4_partial_improvement.py
│   ├── test_falsification_5_correlation.py
│   ├── test_falsification_6_stale_consensus.py
│   ├── test_falsification_7_overhead.py
│   ├── test_falsification_8_recovery_evolution.py
│   ├── test_v_layers.py           # V1–V12 assurance contract validation
│   ├── test_lifecycle.py          # 7-stage lifecycle verification
│   ├── test_4vp.py                # Enhanced 4VP reconciliation tests
│   ├── test_logging.py            # Evolution decision log & rejection log
│   └── conftest.py                # Pytest fixtures
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI pipeline
├── FALSIFICATION_PLAN.md          # 8 attack vectors & success criteria
├── LOGGING_SPEC.md                # Detailed logging format & examples
├── LICENSE                        # Apache 2.0
└── pyproject.toml                 # Python package config
```

---

## The Eight Falsification Tests (Framework Validation)

| # | Attack Vector | Success Criterion | V-Layer Focus |
|---|---|---|---|
| 1 | Slow-drift / boiling-frog | Detect cumulative drift before material threshold; lock baseline | V2, V5, V12 |
| 2 | Baseline poisoning | Baseline never moves without consequence-gated approval & fresh evidence | V5, V6, V12 |
| 3 | Spoofed intent with valid credentials | Credentials alone never authorize; intent (V4) must be independently verified | V1, V3, V4, V6 |
| 4 | Partial improvement | Regression in protected dimensions blocks promotion | V8, V9, V11 |
| 5 | Local-vs-global correlation | Systemic failures detected; consequence boundary expands when local resolution insufficient | V10, V11 |
| 6 | Stale consensus | Agreement does not substitute for freshness; V5 Evidence layer enforced | V5, V8, V9 |
| 7 | Controller overhead | Overhead < allowed budget; deadlines maintained; no denial-of-service | V7 |
| 8 | Recovery/evolution confusion | Recovery restores known-good baseline (V12 Rest); redesign is separate candidate | V10, V12 |

All tests produce **quantitative rejection logs** for independent review.

---

## Test Results & Promotion Criteria

### Framework Validation

✅ **Framework passes adversarial suites** — The reference implementation survives applicable attack vectors and falsification protocols.

❌ **Framework fails** — One or more attack vectors succeeded in compromising the model.

### Candidate Validation

✅ **PROMOTION_CANDIDATE**
- Passed applicable 4VP stages (I–IV)
- Passed relevant V-layer assurance contracts
- Passed protected-dimension regression budgets
- Authority and intent lineage verified
- Confirmation and reconciliation independent
- Baseline recertification explicit (if updating)
- Recorded in evolution decision log or rejection log
- Ready for peer review
- Domain-specific validation required before deployment
- NOT production safety certification

❌ **REJECTED**
- Failed one or more applicable requirements
- Rejection log includes quantitative evidence and V-layer trace
- Candidate is blocked from promotion

❓ **UNKNOWN**
- Inconclusive results
- Must not silently become approval
- Requires explicit re-evaluation or domain-specific decision
- Recorded in inconclusive decision log

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

### Run Falsification Tests Only (Framework Validation)
```bash
pytest tests/test_falsification_*.py -v
```

### Run V-Layer Validation
```bash
pytest tests/test_v_layers.py -v
```

### Run with Coverage & Quantitative Logs
```bash
pytest tests/ --cov=src --cov-report=html -v --log-cli-level=INFO
```

---

## Key Implementation Areas

### 1. VerificationSandboxEngine (4VP Enhanced)

Enforces all four stages with strengthened reconciliation:
- Stage 1: Backward challenge with authority lineage tracing
- Stage 2: Isolated execution with full telemetry
- Stage 3: Forward promise with protected-dimension budget validation
- Stage 4: Independent reconciliation with deficiency-closure threshold

Returns: `PROMOTION_CANDIDATE`, `REJECTED`, or `UNKNOWN` (never silent approval).

### 2. Baseline Anchoring & Drift Detection

Long-horizon locked baseline prevents "boiling frog":
- Compare every observation against recent state AND locked anchor
- Baseline updates require V12 recertification + evolution decision log
- Cumulative drift threshold configurable per domain

### 3. Resource Allocation (v2.1 Formula)

```
SpendBudget = B₀ + Φ × f(C, U, Aₑ, Dₒ)
```

- B₀ ensures minimum inspection even when C/U low
- f() is bounded and saturating (no runaway computation)
- Configuration by domain (quantum vs. healthcare vs. AI)

### 4. V-Layer Assurance Stack

V1–V12 validators enforce canonical meanings:
- V1 Identity: Source authentication
- V2 Truth: Fact establishment
- V3 Eligibility: Participation/action permission under applicable rules
- V4 Intent: Explicit intent binding; ambiguity detection
- V5 Evidence: Freshness & chain validation
- V6 Authority: Backward lineage
- V7 Execution: Minimal state mutation
- V8 Confirmation: Reality measurement
- V9 Reconciliation: Expectation vs. reality
- V10 Projection: Downstream truth representation (not truth manufacturing)
- V11 Continuity: Cross-layer coherence
- V12 Evolution / Rest: Baseline recertification or return to rest

### 5. Protected-Dimension Regression Budgets

Multi-dimensional guards prevent "partial improvements":
- Latency (p99) regression threshold
- Recovery time regression threshold
- Security surface expansion limit
- Authority audit trail completeness
- Confirmation fidelity floor
- Reconciliation verifiability requirement

### 6. Evolution Decision Log & Rejection Log

- **Evolution Decision Log:** Immutable/tamper-evident records of baseline updates with authority, evidence, and rollback info
- **Rejection Log:** Candidates that fail validation with quantitative evidence
- **Inconclusive Log:** UNKNOWN results that must never auto-promote

### 7. Recovery vs. Evolution State Machine

Strict separation:
- **Recovery:** Restores known-good baseline only (V12 Rest path)
- **Evolution:** Proposes new candidate (separate V12 Evolution approval gate)
- Recovery cannot morph into unreviewed optimization

---

## Documentation

- **[DOCTRINE_v2.1.md](docs/DOCTRINE_v2.1.md)** — Complete standard specification
- **[V_LAYERS.md](docs/V_LAYERS.md)** — V1–V12 canonical definitions with domain-specific controls
- **[4VP_RECONCILIATION.md](docs/4VP_RECONCILIATION.md)** — Strengthened 4-stage protocol
- **[RESOURCE_CALCULUS.md](docs/RESOURCE_CALCULUS.md)** — v2.1 formula with saturation & B₀
- **[FALSIFICATION_PLAN.md](FALSIFICATION_PLAN.md)** — 8 attack vectors & success criteria
- **[LOGGING_SPEC.md](LOGGING_SPEC.md)** — Evolution decision log, rejection log, and inconclusive log formats

---

## Contributing

This is an open research framework. Contributions should focus on:
- **Validating or falsifying** architectural principles (submit falsification manifests)
- **Domain-specific adaptations** (quantum, AI, healthcare, infrastructure)
- **Test coverage expansion** for edge cases and cross-layer interactions
- **Independent peer review** and analysis
- **Logging and decision audit** improvements

Submit research findings via issues or pull requests.

---

## Citation

```
Verified Evolution Doctrine v2.1 — Reference Implementation & Validation Framework
Experimental Research Architecture
https://github.com/keithbilly78-afk/verified-evolution-doctrine
```

---

## License

Apache License 2.0 — See LICENSE file.

---

**Status:** 🔬 Research Phase — Not production safety certified.

All formulas, thresholds, V-layer implementations, and experimental success criteria are testable hypotheses.

Passing tests: `PROMOTION_CANDIDATE` only. Framework validation does not establish universal applicability.
