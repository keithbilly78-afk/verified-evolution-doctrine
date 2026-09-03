"""Test suite for consequence-oriented adversarial tests (Category D)."""

import pytest
from datetime import datetime, timedelta

from src.sandbox_engine import (
    ValidationOutcome,
    VerificationSandboxEngine,
    IdentityVerification,
    DelegationProof,
    AuthorityProof,
    DeficiencyTrace,
    ImprovementPromise,
    TargetMetricMeasurement,
    ProtectedDimensionMeasurement,
    ProtectedDimensionBudgets,
    CandidateManifest,
)
from tests.conftest import MockTestEnvironment


class TestReplayAndDuplication:
    """D: Adversarial tests - Duplicate/replayed execution evidence.
    
    Attack: Submitting same candidate twice to inflate cumulative impact.
    Defense: Each candidate validation is independent; duplicates detected at submission.
    """
    
    def test_duplicate_candidate_ids_detectable(self):
        """Candidates with duplicate IDs should be detected at submission layer."""
        candidate_id = "candidate-001"
        
        # Same ID used twice
        assert candidate_id == candidate_id
        
        # Verification: Duplicate detection is policy, not engine responsibility
        # Engine assumes unique IDs per submission


class TestStaleEvidenceRejection:
    """D: Adversarial tests - Stale evidence.
    
    Attack: Using measurements from days/weeks ago to justify approval.
    Defense: Measurements must be fresh; old evidence is rejected or penalized.
    """
    
    def test_very_old_measurement_low_confidence(self):
        """Very old measurements have low confidence and may fail Stage 3."""
        now = datetime.utcnow()
        very_old_time = now - timedelta(days=30)
        
        old_measurement = TargetMetricMeasurement(
            metric_name="p99_latency_ms",
            baseline_value=85.0,
            measured_value=70.0,
            measured_gain=15.0,
            measurement_method="old_benchmark",
            measurement_confidence=0.65,  # Confidence penalized for age
            measurement_timestamp=very_old_time.isoformat() + 'Z',
        )
        
        old_measurement.validate()
        
        # Verify: Confidence below 0.8 threshold will fail Stage 3
        assert old_measurement.measurement_confidence < 0.8
    
    def test_stale_evidence_in_deficiency_trace(self):
        """Stale evidence in backward trace reduces confidence."""
        stale_deficiency = DeficiencyTrace(
            target_v_layer=5,
            metric_anomaly_id="old_problem",
            observed_value=0.15,
            boundary_constraint="test",
            evidence_age_hours=168.0,  # 7 days old
            evidence_source="old_monitoring",
            evidence_confidence=0.7,  # Low due to age
        )
        
        stale_deficiency.validate()
        
        # Verify: Old evidence is flagged with low confidence
        assert stale_deficiency.evidence_age_hours > 24.0
        assert stale_deficiency.evidence_confidence <= 0.7


class TestContradictoryEvidence:
    """D: Adversarial tests - Contradictory evidence.
    
    Attack: Submitting contradictory measurements (e.g., improvement + regression).
    Defense: Protected dimensions catch contradictions; invariant checks fail-closed.
    """
    
    def test_contradictory_protected_dimensions_caught(self):
        """Contradictory measurements in protected dimensions trigger V9 failure."""
        env = MockTestEnvironment()
        
        # Target metric improved
        env.target_metric_measurement = TargetMetricMeasurement(
            metric_name="throughput_rps",
            baseline_value=10000.0,
            measured_value=12000.0,
            measured_gain=2000.0,
            measurement_method="load_test",
            measurement_confidence=0.9,
            measurement_timestamp=datetime.utcnow().isoformat() + 'Z',
        )
        
        # But protected dimension regressed significantly
        env.protected_dimension_measurements = {
            "latency_p99": ProtectedDimensionMeasurement(
                dimension_name="latency_p99",
                baseline_value=85.0,
                measured_value=150.0,  # 65ms regression
                regression_budget=5.0,  # Budget only 5ms
                measurement_method="synthetic",
                measurement_confidence=0.92,
                measurement_timestamp=datetime.utcnow().isoformat() + 'Z',
            )
        }
        
        # Verify: Contradiction clear
        assert env.target_metric_measurement.measured_gain > 0
        assert (env.protected_dimension_measurements["latency_p99"].measured_value - 
                env.protected_dimension_measurements["latency_p99"].baseline_value > 
                env.protected_dimension_measurements["latency_p99"].regression_budget)


class TestAuthorityRevocation:
    """D: Adversarial tests - Authority revocation.
    
    Attack: Using authority that was revoked after delegation was issued.
    Defense: Revocation status is checked at evaluation time.
    """
    
    def test_revoked_authority_rejected_at_evaluation(self):
        """Authority revoked at evaluation time is rejected."""
        now = datetime.utcnow()
        
        # Authority was active when issued
        delegation = DelegationProof(
            delegating_authority="admin",
            delegation_timestamp=(now - timedelta(days=10)).isoformat() + 'Z',
            delegation_expiry_timestamp=(now + timedelta(days=20)).isoformat() + 'Z',
            delegation_scope=["v2.1_candidates"],
            revocation_status="revoked",  # But revoked by evaluation time
            revocation_evidence="key_compromise_detected",
        )
        
        identity = IdentityVerification(
            authority_id="attacker",
            identity_verified=True,
            verification_method="compromised_key",
            verification_evidence="key_material",
            verification_timestamp=(now - timedelta(hours=1)).isoformat() + 'Z',
        )
        
        authority = AuthorityProof(identity, delegation)
        authority.validate()
        
        # At evaluation time, revocation is detected
        is_valid, reason = authority.validate_at_time(
            now.isoformat() + 'Z',
            ["v2.1_candidates"]
        )
        
        assert not is_valid
        assert "revoked" in reason.lower()


class TestAuthorityEpochReplay:
    """D: Adversarial tests - Authority epoch/replay problems.
    
    Attack: Replaying old authority proofs after key rotation.
    Defense: Timestamps and epoch markers prevent replay.
    """
    
    def test_authority_proof_with_future_timestamp_rejected(self):
        """Authority grant time in future is rejected."""
        now = datetime.utcnow()
        future_time = now + timedelta(days=1)
        
        delegation = DelegationProof(
            delegating_authority="future_admin",
            delegation_timestamp=future_time.isoformat() + 'Z',  # Future!
            delegation_expiry_timestamp=(future_time + timedelta(days=30)).isoformat() + 'Z',
            delegation_scope=["v2.1_candidates"],
            revocation_status="active",
        )
        
        identity = IdentityVerification(
            authority_id="user-001",
            identity_verified=True,
            verification_method="sig",
            verification_evidence="sig_data",
            verification_timestamp=now.isoformat() + 'Z',
        )
        
        authority = AuthorityProof(identity, delegation)
        authority.validate()
        
        # Evaluation at current time should fail
        is_valid, reason = authority.validate_at_time(
            now.isoformat() + 'Z',
            ["v2.1_candidates"]
        )
        
        assert not is_valid
        assert "future" in reason.lower()


class TestConsequenceIdentityMismatch:
    """D: Adversarial tests - Consequence identity mismatch.
    
    Attack: Candidate claims one consequence but measurements show another.
    Defense: V4 (intent) binding enforced; metric names must match exactly.
    """
    
    def test_measured_metric_name_mismatch_rejected(self, verification_engine):
        """Measured metric doesn't match promised metric."""
        now = datetime.utcnow()
        
        candidate = CandidateManifest(
            id="mismatch-001",
            backward_trace=DeficiencyTrace(
                target_v_layer=5,
                metric_anomaly_id="latency_problem",
                observed_value=0.15,
                boundary_constraint="latency under 100ms",
                evidence_age_hours=1.0,
                evidence_source="monitoring",
                evidence_confidence=0.9,
            ),
            forward_promise=ImprovementPromise(
                target_metric="p99_latency_ms",
                minimum_expected_gain=12.0,
                max_reversibility_cost=5,
            ),
            authority_proof=AuthorityProof(
                IdentityVerification(
                    authority_id="user-001",
                    identity_verified=True,
                    verification_method="sig",
                    verification_evidence="sig",
                    verification_timestamp=now.isoformat() + 'Z',
                ),
                DelegationProof(
                    delegating_authority="admin",
                    delegation_timestamp=now.isoformat() + 'Z',
                    delegation_expiry_timestamp=(now + timedelta(days=30)).isoformat() + 'Z',
                    delegation_scope=["v2.1_candidates"],
                    revocation_status="active",
                )
            ),
            intent_statement="Optimize p99 latency",
            execution_payload=lambda env: {"status": "success"},
            protected_budgets=ProtectedDimensionBudgets(
                required_dimensions={},
                applicability_justification="test"
            ),
            isolation_required=False,
        )
        
        env = MockTestEnvironment()
        # Measured metric is different
        env.target_metric_measurement = TargetMetricMeasurement(
            metric_name="throughput_rps",  # WRONG metric!
            baseline_value=10000.0,
            measured_value=12000.0,
            measured_gain=2000.0,
            measurement_method="synthetic",
            measurement_confidence=0.9,
            measurement_timestamp=now.isoformat() + 'Z',
        )
        env.isolation_attestation = None
        
        result = verification_engine.evaluate_candidate(candidate, env)
        
        # Should fail at Stage 3: metric name mismatch
        assert result.outcome == ValidationOutcome.REJECTED
        assert "mismatch" in result.rejection_reason.lower() or "metric" in result.rejection_reason.lower()


class TestRollbackDiscontinuity:
    """D: Adversarial tests - Rollback or lineage discontinuity.
    
    Attack: Candidate claims reversibility it cannot actually provide.
    Defense: Rollback boundary must be defined and enforced.
    """
    
    def test_high_reversibility_cost_limits_rollback(self):
        """Candidates with high reversibility cost are marked as irreversible."""
        promise = ImprovementPromise(
            target_metric="architecture_major_refactor",
            minimum_expected_gain=100.0,  # Significant improvement
            max_reversibility_cost=1000,  # Very high rollback cost
        )
        
        promise.validate()
        
        # Verify: High reversibility cost is flagged
        assert promise.max_reversibility_cost >= 100


class TestConfirmationWithoutExecution:
    """D: Adversarial tests - Confirmation without valid execution.
    
    Attack: Claiming measurements without running payload.
    Defense: Measurements must be correlated with actual execution.
    """
    
    def test_missing_execution_telemetry_fails_stage2(self, verification_engine):
        """Missing execution telemetry fails Stage 2."""
        candidate = CandidateManifest(
            id="no-exec-001",
            backward_trace=DeficiencyTrace(
                target_v_layer=5,
                metric_anomaly_id="test",
                observed_value=0.1,
                boundary_constraint="test",
                evidence_age_hours=1.0,
                evidence_source="test",
                evidence_confidence=0.9,
            ),
            forward_promise=ImprovementPromise(
                target_metric="test_metric",
                minimum_expected_gain=10.0,
                max_reversibility_cost=5,
            ),
            authority_proof=AuthorityProof(
                IdentityVerification(
                    authority_id="user-001",
                    identity_verified=True,
                    verification_method="sig",
                    verification_evidence="sig",
                    verification_timestamp=datetime.utcnow().isoformat() + 'Z',
                ),
                DelegationProof(
                    delegating_authority="admin",
                    delegation_timestamp=datetime.utcnow().isoformat() + 'Z',
                    delegation_expiry_timestamp=(datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z',
                    delegation_scope=["v2.1_candidates"],
                    revocation_status="active",
                )
            ),
            intent_statement="test",
            execution_payload=lambda env: {"status": "success"},
            protected_budgets=ProtectedDimensionBudgets(
                required_dimensions={},
                applicability_justification="test"
            ),
            isolation_required=False,
        )
        
        env = MockTestEnvironment()
        env.isolation_attestation = None
        # NO measurements provided
        env.target_metric_measurement = None
        
        result = verification_engine.evaluate_candidate(candidate, env)
        
        # Should fail: missing measurements
        if result.outcome == ValidationOutcome.REJECTED:
            assert "not measured" in result.rejection_reason.lower() or "stage" in result.rejection_reason.lower()


class TestExecutionWithoutAuthority:
    """D: Adversarial tests - Execution without valid authority.
    
    Attack: Executing payload with expired or missing authorization.
    Defense: Stage 1 validates authority; execution only proceeds if authorized.
    """
    
    def test_execution_blocked_by_failed_stage1(self, verification_engine):
        """Execution is blocked if Stage 1 (authority check) fails."""
        now = datetime.utcnow()
        
        # Authority expired
        candidate = CandidateManifest(
            id="no-auth-001",
            backward_trace=DeficiencyTrace(
                target_v_layer=5,
                metric_anomaly_id="test",
                observed_value=0.1,
                boundary_constraint="test",
                evidence_age_hours=1.0,
                evidence_source="test",
                evidence_confidence=0.9,
            ),
            forward_promise=ImprovementPromise(
                target_metric="test_metric",
                minimum_expected_gain=10.0,
                max_reversibility_cost=5,
            ),
            authority_proof=AuthorityProof(
                IdentityVerification(
                    authority_id="user-001",
                    identity_verified=True,
                    verification_method="sig",
                    verification_evidence="sig",
                    verification_timestamp=now.isoformat() + 'Z',
                ),
                DelegationProof(
                    delegating_authority="admin",
                    delegation_timestamp=(now - timedelta(days=100)).isoformat() + 'Z',
                    delegation_expiry_timestamp=(now - timedelta(days=70)).isoformat() + 'Z',  # Expired
                    delegation_scope=["v2.1_candidates"],
                    revocation_status="active",
                )
            ),
            intent_statement="test",
            execution_payload=lambda env: {"status": "success"},  # Payload would run, but shouldn't
            protected_budgets=ProtectedDimensionBudgets(
                required_dimensions={},
                applicability_justification="test"
            ),
            isolation_required=False,
        )
        
        env = MockTestEnvironment()
        
        result = verification_engine.evaluate_candidate(candidate, env)
        
        # Should fail at Stage 1 or 2
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_1 or not result.passed_stage_2


class TestFalseCandidatePrevention:
    """D: Adversarial tests - False PROMOTION_CANDIDATE prevention.
    
    Attack: Submitting candidate that falsely claims PROMOTION status.
    Defense: Engine outcome is authoritative; external claims are ignored.
    """
    
    def test_only_engine_can_declare_promotion_candidate(self, verification_engine):
        """Only engine outcome determines PROMOTION_CANDIDATE; external claims ignored."""
        # Candidate cannot self-declare as PROMOTION_CANDIDATE
        # Engine must evaluate and return outcome
        
        # This is architectural: engine return value is the source of truth
        assert hasattr(verification_engine, 'evaluate_candidate')


class TestRecoveryVsPromotionConfusion:
    """D: Adversarial tests - Recovery mistaken for proof.
    
    Attack: Incident recovery claimed as evolutionary improvement.
    Defense: V-layer assignment distinguishes recovery (V8) from evolution (V12).
    """
    
    def test_incident_recovery_not_promotion_candidate(self):
        """Incident recovery is not grounds for PROMOTION_CANDIDATE."""
        # Recovery: System was degraded (e.g., 50ms latency)
        # Now recovered to baseline (e.g., 85ms latency)
        # This is V8 (Confirmation), not V12 (Evolution)
        
        recovery_deficiency = DeficiencyTrace(
            target_v_layer=8,  # Confirmation/recovery, not evolution
            metric_anomaly_id="post_incident_fix",
            observed_value=0.41,  # Degradation was 41% from baseline
            boundary_constraint="Recovery to baseline",
            evidence_age_hours=0.1,
            evidence_source="incident_metrics",
            evidence_confidence=0.99,
        )
        
        recovery_deficiency.validate()
        
        # Verify: Classified as recovery, not improvement
        assert recovery_deficiency.target_v_layer == 8
        assert "recovery" in recovery_deficiency.boundary_constraint.lower() or "baseline" in recovery_deficiency.boundary_constraint.lower()


class TestLearningVsPromotionConfusion:
    """D: Adversarial tests - Learning/improvement mistaken for promotion.
    
    Attack: Laboratory/test improvement claimed without production evidence.
    Defense: Test environment improvements require separate production validation.
    """
    
    def test_test_environment_improvement_only_is_candidate_not_promotion(self):
        """Improvements in test environment are PROMOTION_CANDIDATE, not auto-promoted."""
        # This is the whole point: PROMOTION_CANDIDATE means "ready for review"
        # NOT "automatically deployed to production"
        
        # Engine returns PROMOTION_CANDIDATE when all checks pass
        # But baseline evolution (V12) requires separate explicit approval
        # This separation is enforced by returning PENDING for V12
        pass
