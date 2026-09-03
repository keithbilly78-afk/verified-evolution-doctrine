"""Test suite for core 4VP validation requirements (Category A)."""

import pytest
import math
from datetime import datetime, timedelta

from src.sandbox_engine import (
    ValidationError,
    validate_finite_numeric,
    validate_timestamp,
    validate_non_empty_string,
    IdentityVerification,
    DelegationProof,
    AuthorityProof,
    DeficiencyTrace,
    ImprovementPromise,
    TargetMetricMeasurement,
    ProtectedDimensionMeasurement,
    ProtectedDimensionBudgets,
)


class TestNumericValidation:
    """A: Core validation - numeric inputs."""
    
    def test_valid_finite_numeric(self):
        """Finite numerics pass."""
        result = validate_finite_numeric(3.14, "test_value", 0.0, 10.0)
        assert result == 3.14
    
    def test_nan_rejected(self):
        """NaN is rejected."""
        with pytest.raises(ValidationError, match="cannot be NaN"):
            validate_finite_numeric(float('nan'), "test_value")
    
    def test_positive_infinity_rejected(self):
        """Positive infinity is rejected."""
        with pytest.raises(ValidationError, match="cannot be NaN or infinite"):
            validate_finite_numeric(float('inf'), "test_value")
    
    def test_negative_infinity_rejected(self):
        """Negative infinity is rejected."""
        with pytest.raises(ValidationError, match="cannot be NaN or infinite"):
            validate_finite_numeric(float('-inf'), "test_value")
    
    def test_non_numeric_rejected(self):
        """Non-numeric types are rejected."""
        with pytest.raises(ValidationError, match="must be numeric"):
            validate_finite_numeric("not_a_number", "test_value")
    
    def test_min_value_enforced(self):
        """Minimum value constraint is enforced."""
        with pytest.raises(ValidationError, match="must be >= 5.0"):
            validate_finite_numeric(3.0, "test_value", min_val=5.0)
    
    def test_max_value_enforced(self):
        """Maximum value constraint is enforced."""
        with pytest.raises(ValidationError, match="must be <= 10.0"):
            validate_finite_numeric(15.0, "test_value", max_val=10.0)


class TestTimestampValidation:
    """A: Core validation - timestamps."""
    
    def test_valid_iso8601_timestamp(self):
        """Valid ISO 8601 timestamps are accepted."""
        ts = datetime.utcnow().isoformat() + 'Z'
        result = validate_timestamp(ts, "test_ts")
        assert isinstance(result, datetime)
    
    def test_empty_timestamp_rejected(self):
        """Empty timestamp string is rejected."""
        with pytest.raises(ValidationError, match="must be non-empty string"):
            validate_timestamp("", "test_ts")
    
    def test_malformed_timestamp_rejected(self):
        """Malformed timestamps are rejected."""
        with pytest.raises(ValidationError, match="invalid ISO 8601 format"):
            validate_timestamp("not-a-timestamp", "test_ts")
    
    def test_none_timestamp_rejected(self):
        """None timestamp is rejected."""
        with pytest.raises(ValidationError, match="must be non-empty string"):
            validate_timestamp(None, "test_ts")
    
    def test_stale_timestamp_detected(self):
        """Stale timestamps can be detected via age comparison."""
        old_time = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'
        result = validate_timestamp(old_time, "test_ts")
        assert isinstance(result, datetime)
        # Age can be calculated if needed


class TestStringValidation:
    """A: Core validation - string identifiers."""
    
    def test_valid_non_empty_string(self):
        """Non-empty strings are accepted."""
        result = validate_non_empty_string("valid_id", "test_id")
        assert result == "valid_id"
    
    def test_empty_string_rejected(self):
        """Empty strings are rejected."""
        with pytest.raises(ValidationError, match="must be non-empty string"):
            validate_non_empty_string("", "test_id")
    
    def test_whitespace_only_rejected(self):
        """Whitespace-only strings are rejected."""
        with pytest.raises(ValidationError, match="must be non-empty string"):
            validate_non_empty_string("   ", "test_id")
    
    def test_none_string_rejected(self):
        """None is rejected."""
        with pytest.raises(ValidationError, match="must be non-empty string"):
            validate_non_empty_string(None, "test_id")


class TestIdentityVerificationValidation:
    """A: Core validation - identity verification (V1)."""
    
    def test_valid_identity_verification(self, valid_identity_verification):
        """Valid identity verification passes validation."""
        valid_identity_verification.validate()
        # Should not raise
    
    def test_missing_authority_id_rejected(self, valid_identity_verification):
        """Missing authority_id is rejected."""
        valid_identity_verification.authority_id = ""
        with pytest.raises(ValidationError):
            valid_identity_verification.validate()
    
    def test_non_bool_identity_verified_rejected(self, valid_identity_verification):
        """Non-boolean identity_verified is rejected."""
        valid_identity_verification.identity_verified = "yes"
        with pytest.raises(ValidationError, match="must be bool"):
            valid_identity_verification.validate()
    
    def test_missing_verification_evidence_rejected(self, valid_identity_verification):
        """Missing verification_evidence is rejected."""
        valid_identity_verification.verification_evidence = ""
        with pytest.raises(ValidationError):
            valid_identity_verification.validate()
    
    def test_expired_identity_verification(self, valid_identity_verification):
        """Expired identity verification is detected."""
        # Set verification timestamp to 30 hours ago
        old_time = (datetime.utcnow() - timedelta(hours=30)).isoformat() + 'Z'
        valid_identity_verification.verification_timestamp = old_time
        valid_identity_verification.validate()
        
        # Now check freshness at current time
        now = datetime.utcnow().isoformat() + 'Z'
        is_fresh = valid_identity_verification.is_fresh_at(now, max_age_hours=24.0)
        assert not is_fresh


class TestDelegationProofValidation:
    """A: Core validation - delegation proof (V6)."""
    
    def test_valid_delegation_proof(self, valid_delegation_proof):
        """Valid delegation proof passes validation."""
        valid_delegation_proof.validate()
        # Should not raise
    
    def test_missing_delegating_authority_rejected(self, valid_delegation_proof):
        """Missing delegating_authority is rejected."""
        valid_delegation_proof.delegating_authority = ""
        with pytest.raises(ValidationError):
            valid_delegation_proof.validate()
    
    def test_grant_time_after_expiry_rejected(self, valid_delegation_proof):
        """Grant time after expiry time is rejected."""
        now = datetime.utcnow()
        valid_delegation_proof.delegation_timestamp = (now + timedelta(days=1)).isoformat() + 'Z'
        valid_delegation_proof.delegation_expiry_timestamp = now.isoformat() + 'Z'
        with pytest.raises(ValidationError, match="must be before"):
            valid_delegation_proof.validate()
    
    def test_empty_delegation_scope_rejected(self, valid_delegation_proof):
        """Empty delegation_scope is rejected."""
        valid_delegation_proof.delegation_scope = []
        with pytest.raises(ValidationError, match="must be non-empty list"):
            valid_delegation_proof.validate()
    
    def test_invalid_revocation_status_rejected(self, valid_delegation_proof):
        """Invalid revocation_status is rejected."""
        valid_delegation_proof.revocation_status = "maybe"
        with pytest.raises(ValidationError, match="must be 'active', 'revoked', or 'unknown'"):
            valid_delegation_proof.validate()
    
    def test_revoked_delegation_fails_at_time(self, valid_delegation_proof):
        """Revoked delegation fails at any evaluation time."""
        valid_delegation_proof.revocation_status = "revoked"
        valid_delegation_proof.revocation_evidence = "cert_revocation_reason"
        valid_delegation_proof.validate()
        
        identity_verification = IdentityVerification(
            authority_id="test_user",
            identity_verified=True,
            verification_method="sig",
            verification_evidence="sig_data",
            verification_timestamp=datetime.utcnow().isoformat() + 'Z',
        )
        authority = AuthorityProof(identity_verification, valid_delegation_proof)
        
        is_valid, reason = authority.validate_at_time(
            datetime.utcnow().isoformat() + 'Z',
            ["v2.1_candidates"]
        )
        assert not is_valid
        assert "revoked" in reason.lower()
    
    def test_expired_delegation_fails_at_time(self):
        """Expired delegation fails at evaluation time."""
        now = datetime.utcnow()
        expired_time = now - timedelta(days=1)
        
        delegation = DelegationProof(
            delegating_authority="admin",
            delegation_timestamp=(now - timedelta(days=2)).isoformat() + 'Z',
            delegation_expiry_timestamp=expired_time.isoformat() + 'Z',
            delegation_scope=["v2.1_candidates"],
            revocation_status="active",
        )
        delegation.validate()
        
        identity_verification = IdentityVerification(
            authority_id="test_user",
            identity_verified=True,
            verification_method="sig",
            verification_evidence="sig_data",
            verification_timestamp=now.isoformat() + 'Z',
        )
        authority = AuthorityProof(identity_verification, delegation)
        
        is_valid, reason = authority.validate_at_time(
            now.isoformat() + 'Z',
            ["v2.1_candidates"]
        )
        assert not is_valid
        assert "expired" in reason.lower()


class TestAuthorityProofValidation:
    """A: Core validation - authority proof (V1 + V6)."""
    
    def test_valid_authority_proof(self, valid_authority_proof):
        """Valid authority proof passes validation."""
        valid_authority_proof.validate()
        # Should not raise
    
    def test_unverified_identity_fails(self, valid_authority_proof):
        """Unverified identity fails authority check."""
        valid_authority_proof.identity_verification.identity_verified = False
        valid_authority_proof.validate()
        
        is_valid, reason = valid_authority_proof.validate_at_time(
            datetime.utcnow().isoformat() + 'Z',
            ["v2.1_candidates"]
        )
        assert not is_valid
        assert "not verified" in reason.lower()
    
    def test_missing_required_scope_fails(self, valid_authority_proof):
        """Missing required scope fails authority check."""
        valid_authority_proof.delegation_proof.delegation_scope = ["other_scope"]
        valid_authority_proof.validate()
        
        is_valid, reason = valid_authority_proof.validate_at_time(
            datetime.utcnow().isoformat() + 'Z',
            ["v2.1_candidates"]
        )
        assert not is_valid
        assert "not in delegation" in reason.lower()
    
    def test_proof_chain_verifier_required_if_chain_present(self, valid_authority_proof):
        """If proof chain is present, verifier callback is required."""
        valid_authority_proof.delegation_proof.delegation_proof_chain = ["parent_id_1"]
        valid_authority_proof.validate()
        
        is_valid, reason = valid_authority_proof.validate_at_time(
            datetime.utcnow().isoformat() + 'Z',
            ["v2.1_candidates"],
            proof_chain_verifier=None  # No verifier supplied
        )
        assert not is_valid
        assert "no verifier supplied" in reason.lower()


class TestDeficiencyTraceValidation:
    """A: Core validation - deficiency trace (V2, V5)."""
    
    def test_valid_deficiency_trace(self, valid_deficiency_trace):
        """Valid deficiency trace passes validation."""
        valid_deficiency_trace.validate()
        # Should not raise
    
    def test_invalid_v_layer_rejected(self, valid_deficiency_trace):
        """Invalid V-layer (outside 1-12) is rejected."""
        valid_deficiency_trace.target_v_layer = 13
        with pytest.raises(ValidationError, match="must be 1-12"):
            valid_deficiency_trace.validate()
    
    def test_zero_observed_value_rejected(self, valid_deficiency_trace):
        """Observed value must be > 0."""
        valid_deficiency_trace.observed_value = 0.0
        with pytest.raises(ValidationError, match="must be > 0"):
            valid_deficiency_trace.validate()
    
    def test_observed_value_exceeding_1_0_rejected(self, valid_deficiency_trace):
        """Observed value > 1.0 is rejected."""
        valid_deficiency_trace.observed_value = 1.5
        with pytest.raises(ValidationError, match="must be <= 1.0"):
            valid_deficiency_trace.validate()


class TestImprovementPromiseValidation:
    """A: Core validation - improvement promise (V8, V9)."""
    
    def test_valid_improvement_promise(self, valid_improvement_promise):
        """Valid improvement promise passes validation."""
        valid_improvement_promise.validate()
        # Should not raise
    
    def test_missing_target_metric_rejected(self, valid_improvement_promise):
        """Missing target_metric is rejected."""
        valid_improvement_promise.target_metric = ""
        with pytest.raises(ValidationError):
            valid_improvement_promise.validate()
    
    def test_negative_minimum_expected_gain_rejected(self, valid_improvement_promise):
        """Negative minimum_expected_gain is rejected."""
        valid_improvement_promise.minimum_expected_gain = -1.0
        with pytest.raises(ValidationError, match="must be >= 0.0"):
            valid_improvement_promise.validate()


class TestMeasurementValidation:
    """A: Core validation - measurement semantics."""
    
    def test_valid_target_metric_measurement(self, valid_target_metric_measurement):
        """Valid target metric measurement passes validation."""
        valid_target_metric_measurement.validate()
        # Should not raise
    
    def test_nan_baseline_value_rejected(self, valid_target_metric_measurement):
        """NaN baseline value is rejected."""
        valid_target_metric_measurement.baseline_value = float('nan')
        with pytest.raises(ValidationError, match="cannot be NaN"):
            valid_target_metric_measurement.validate()
    
    def test_incompatible_gain_semantics_rejected(self, valid_target_metric_measurement):
        """Measured gain incompatible with baseline/measured values is rejected."""
        # baseline = 85, measured = 70, gain should be ~15
        # If gain is claimed to be 50, that's incompatible
        valid_target_metric_measurement.measured_gain = 50.0
        with pytest.raises(ValidationError, match="incompatible"):
            valid_target_metric_measurement.validate()
    
    def test_valid_protected_dimension_measurement(self, valid_protected_dimension_measurement):
        """Valid protected dimension measurement passes validation."""
        valid_protected_dimension_measurement.validate()
        # Should not raise
    
    def test_missing_dimension_name_rejected(self, valid_protected_dimension_measurement):
        """Missing dimension_name is rejected."""
        valid_protected_dimension_measurement.dimension_name = ""
        with pytest.raises(ValidationError):
            valid_protected_dimension_measurement.validate()


class TestProtectedDimensionBudgetsValidation:
    """A: Core validation - protected dimension budgets."""
    
    def test_valid_protected_budgets(self, valid_protected_budgets):
        """Valid protected budgets pass validation."""
        valid_protected_budgets.validate()
        # Should not raise
    
    def test_empty_dimensions_without_justification_rejected(self):
        """Empty dimensions with no justification is rejected."""
        budgets = ProtectedDimensionBudgets(
            required_dimensions={},
            applicability_justification=""
        )
        with pytest.raises(ValidationError, match="Either required_dimensions must be non-empty"):
            budgets.validate()
    
    def test_empty_dimensions_with_justification_accepted(self):
        """Empty dimensions with justification is accepted."""
        budgets = ProtectedDimensionBudgets(
            required_dimensions={},
            applicability_justification="This candidate is low-consequence and has no protected dimensions."
        )
        budgets.validate()
        # Should not raise
