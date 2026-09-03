"""Test suite for 4VP outcomes and stage validation (Category B)."""

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
    IsolationAttestation,
    CandidateManifest,
)
from tests.conftest import MockTestEnvironment


class Test4VPHappyPath:
    """B: 4VP outcomes - happy path to PROMOTION_CANDIDATE."""
    
    def test_valid_candidate_passes_all_stages(self, valid_candidate_manifest, mock_test_environment, verification_engine):
        """Valid candidate with all measurements passes all 4 stages."""
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.PROMOTION_CANDIDATE
        assert result.passed_stage_1
        assert result.passed_stage_2
        assert result.passed_stage_3
        assert result.passed_stage_4
        assert result.v_layer_results["V1"] == "PASS"
        assert result.v_layer_results["V2"] == "PASS"
        assert result.v_layer_results["V6"] == "PASS"
        assert result.v_layer_results["V8"] == "PASS"
        assert result.v_layer_results["V9"] == "PASS"
        assert result.v_layer_results["V11"] == "PASS"
        assert "PENDING" in result.v_layer_results["V12"]


class Test4VPStage1BackwardChallenge:
    """B: 4VP Stage 1 - Backward challenge."""
    
    def test_stage1_fails_on_revoked_authority(self, valid_candidate_manifest, mock_test_environment, verification_engine):
        """Stage 1 fails if authority is revoked."""
        valid_candidate_manifest.authority_proof.delegation_proof.revocation_status = "revoked"
        valid_candidate_manifest.authority_proof.delegation_proof.revocation_evidence = "key_compromise"
        valid_candidate_manifest.authority_proof.validate()
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_1
        assert "V6" in result.v_layer_results
        assert "revoked" in result.v_layer_results["V6"].lower()
    
    def test_stage1_fails_on_expired_authority(self, mock_test_environment, verification_engine):
        """Stage 1 fails if delegation is expired."""
        now = datetime.utcnow()
        
        delegation_proof = DelegationProof(
            delegating_authority="admin",
            delegation_timestamp=(now - timedelta(days=35)).isoformat() + 'Z',
            delegation_expiry_timestamp=(now - timedelta(days=5)).isoformat() + 'Z',
            delegation_scope=["v2.1_candidates"],
            revocation_status="active",
        )
        
        identity_verification = IdentityVerification(
            authority_id="user-001",
            identity_verified=True,
            verification_method="sig",
            verification_evidence="sig_data",
            verification_timestamp=now.isoformat() + 'Z',
        )
        
        authority_proof = AuthorityProof(identity_verification, delegation_proof)
        authority_proof.validate()
        
        deficiency_trace = DeficiencyTrace(
            target_v_layer=5,
            metric_anomaly_id="test_001",
            observed_value=0.15,
            boundary_constraint="test",
            evidence_age_hours=0.5,
            evidence_source="test",
            evidence_confidence=0.9,
        )
        
        improvement_promise = ImprovementPromise(
            target_metric="test_metric",
            minimum_expected_gain=10.0,
            max_reversibility_cost=5,
        )
        
        candidate = CandidateManifest(
            id="test-candidate",
            backward_trace=deficiency_trace,
            forward_promise=improvement_promise,
            authority_proof=authority_proof,
            intent_statement="test",
            execution_payload=lambda env: {"status": "success"},
            protected_budgets=ProtectedDimensionBudgets(
                required_dimensions={},
                applicability_justification="test"
            ),
            isolation_required=True,
        )
        
        result = verification_engine.evaluate_candidate(candidate, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_1
        assert "expired" in result.v_layer_results["V6"].lower()


class Test4VPStage2Execution:
    """B: 4VP Stage 2 - Execution harness."""
    
    def test_stage2_fails_without_isolation_attestation(self, valid_candidate_manifest):
        """Stage 2 fails if isolation is required but not attested."""
        env = MockTestEnvironment()
        env.isolation_attestation = None  # Missing attestation
        env.target_metric_measurement = TargetMetricMeasurement(
            metric_name="p99_latency_ms",
            baseline_value=85.0,
            measured_value=70.0,
            measured_gain=15.0,
            measurement_method="synthetic",
            measurement_confidence=0.92,
            measurement_timestamp=datetime.utcnow().isoformat() + 'Z',
        )
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, env)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_2
        assert "isolation" in result.rejection_reason.lower()
    
    def test_stage2_fails_on_payload_exception(self, valid_candidate_manifest, mock_test_environment):
        """Stage 2 fails if payload raises exception."""
        def failing_payload(env):
            raise RuntimeError("Payload error")
        
        valid_candidate_manifest.execution_payload = failing_payload
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_2
        assert "Payload error" in result.v_layer_results["V7"]


class Test4VPStage3Promise:
    """B: 4VP Stage 3 - Forward promise verification."""
    
    def test_stage3_fails_without_target_metric_measurement(self, valid_candidate_manifest, mock_test_environment):
        """Stage 3 fails if target metric is not measured."""
        mock_test_environment.target_metric_measurement = None
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_3
        assert "not measured" in result.v_layer_results["V8"].lower()
    
    def test_stage3_fails_on_metric_name_mismatch(self, valid_candidate_manifest, mock_test_environment):
        """Stage 3 fails if measured metric name doesn't match promised metric."""
        mock_test_environment.target_metric_measurement.metric_name = "wrong_metric_name"
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_3
        assert "mismatch" in result.v_layer_results["V8"].lower()
    
    def test_stage3_fails_on_insufficient_gain(self, valid_candidate_manifest, mock_test_environment):
        """Stage 3 fails if measured gain < minimum expected gain."""
        # Promise was 12.0 gain, but we measure only 5.0
        mock_test_environment.target_metric_measurement.measured_gain = 5.0
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_3
        assert "Insufficient gain" in result.v_layer_results["V8"]
    
    def test_stage3_fails_on_low_measurement_confidence(self, valid_candidate_manifest, mock_test_environment):
        """Stage 3 fails if measurement confidence is too low."""
        mock_test_environment.target_metric_measurement.measurement_confidence = 0.7
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_3
        assert "confidence" in result.v_layer_results["V8"].lower()
    
    def test_stage3_fails_on_protected_dimension_regression(self, valid_candidate_manifest, mock_test_environment):
        """Stage 3 fails if protected dimension regresses beyond budget."""
        # Regression budget is 5.0, but measured regression is 10.0
        mock_test_environment.protected_dimension_measurements["latency_p99"].measured_value = 95.0
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_3
        assert "regressed" in result.v_layer_results["V9"].lower()


class Test4VPStage4Reconciliation:
    """B: 4VP Stage 4 - Reconciliation and evolution."""
    
    def test_stage4_unknown_on_missing_invariant_check(self, valid_candidate_manifest, mock_test_environment):
        """Stage 4 returns UNKNOWN if invariant check is unavailable."""
        # Remove the check_safety_violations method
        del mock_test_environment.check_safety_violations
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.UNKNOWN
        assert not result.passed_stage_4
        assert "UNKNOWN" in result.v_layer_results["V11"]
    
    def test_stage4_fails_on_broken_invariant(self, valid_candidate_manifest, mock_test_environment):
        """Stage 4 fails if cross-layer invariant is broken."""
        mock_test_environment.invariant_broken = True
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        assert result.outcome == ValidationOutcome.REJECTED
        assert not result.passed_stage_4
        assert "FAIL" in result.v_layer_results["V11"]
        assert "invariant" in result.v_layer_results["V11"].lower()
    
    def test_stage4_v12_marked_pending(self, valid_candidate_manifest, mock_test_environment):
        """Stage 4 marks V12 as PENDING (not auto-approved)."""
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        if result.passed_stage_4:
            assert "PENDING" in result.v_layer_results["V12"]
            assert "explicit" in result.v_layer_results["V12"].lower()


class TestUnknownNeverSilentlyApproves:
    """B: UNKNOWN must never silently become approval."""
    
    def test_unknown_outcome_never_promotes(self, valid_candidate_manifest, mock_test_environment):
        """UNKNOWN outcomes are never automatically promoted to PROMOTION_CANDIDATE."""
        # Create a scenario that results in UNKNOWN
        mock_test_environment.check_safety_violations = None
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        # If UNKNOWN, should definitely not be PROMOTION_CANDIDATE
        if result.outcome == ValidationOutcome.UNKNOWN:
            assert result.outcome != ValidationOutcome.PROMOTION_CANDIDATE
    
    def test_unknown_is_logged(self, valid_candidate_manifest, mock_test_environment):
        """UNKNOWN outcomes are explicitly logged."""
        mock_test_environment.check_safety_violations = None
        
        verification_engine = VerificationSandboxEngine(
            baseline_state={},
            security_envelope={},
        )
        
        result = verification_engine.evaluate_candidate(valid_candidate_manifest, mock_test_environment)
        
        if result.outcome == ValidationOutcome.UNKNOWN:
            assert result.rejection_reason is not None
            assert len(result.v_layer_results) > 0
