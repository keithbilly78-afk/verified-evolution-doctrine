"""Pytest fixtures for 4VP validation tests."""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from src.sandbox_engine import (
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
    VerificationSandboxEngine,
)


class MockTestEnvironment:
    """Mock test environment with configurable measurements."""
    
    def __init__(self):
        self.target_metric_measurement = None
        self.protected_dimension_measurements = {}
        self.invariant_broken = False
        self.isolation_attestation = None
    
    def get_isolation_attestation(self):
        """Return isolation attestation if configured."""
        return self.isolation_attestation
    
    def get_target_metric_measurement(self):
        """Return target metric measurement if configured."""
        return self.target_metric_measurement
    
    def get_protected_dimension_measurements(self):
        """Return protected dimension measurements if configured."""
        return self.protected_dimension_measurements
    
    def check_safety_violations(self):
        """Return True if safe, False if invariant broken."""
        return not self.invariant_broken


@pytest.fixture
def valid_identity_verification():
    """A valid identity verification."""
    return IdentityVerification(
        authority_id="user-001",
        identity_verified=True,
        verification_method="cryptographic_signature",
        verification_evidence="sig_0x12345",
        verification_timestamp=datetime.utcnow().isoformat() + 'Z',
    )


@pytest.fixture
def valid_delegation_proof():
    """A valid delegation proof."""
    now = datetime.utcnow()
    expiry = now + timedelta(days=30)
    
    return DelegationProof(
        delegating_authority="system-admin",
        delegation_timestamp=now.isoformat() + 'Z',
        delegation_expiry_timestamp=expiry.isoformat() + 'Z',
        delegation_scope=["v2.1_candidates"],
        delegation_proof_chain=[],
        revocation_status="active",
    )


@pytest.fixture
def valid_authority_proof(valid_identity_verification, valid_delegation_proof):
    """A valid authority proof."""
    return AuthorityProof(
        identity_verification=valid_identity_verification,
        delegation_proof=valid_delegation_proof,
    )


@pytest.fixture
def valid_deficiency_trace():
    """A valid deficiency trace."""
    return DeficiencyTrace(
        target_v_layer=5,
        metric_anomaly_id="latency_spike_001",
        observed_value=0.15,  # 15% degradation
        boundary_constraint="p99_latency must stay under 100ms",
        evidence_age_hours=2.0,
        evidence_source="monitoring_system",
        evidence_confidence=0.95,
    )


@pytest.fixture
def valid_improvement_promise():
    """A valid improvement promise."""
    return ImprovementPromise(
        target_metric="p99_latency_ms",
        minimum_expected_gain=12.0,  # Must improve by at least 12ms
        max_reversibility_cost=5,
    )


@pytest.fixture
def valid_target_metric_measurement():
    """A valid target metric measurement."""
    return TargetMetricMeasurement(
        metric_name="p99_latency_ms",
        baseline_value=85.0,
        measured_value=70.0,
        measured_gain=15.0,
        measurement_method="synthetic_benchmark",
        measurement_confidence=0.92,
        measurement_timestamp=datetime.utcnow().isoformat() + 'Z',
    )


@pytest.fixture
def valid_protected_dimension_measurement():
    """A valid protected dimension measurement (latency p99)."""
    return ProtectedDimensionMeasurement(
        dimension_name="latency_p99",
        baseline_value=85.0,
        measured_value=82.0,  # Slight improvement, no regression
        regression_budget=5.0,
        measurement_method="synthetic_benchmark",
        measurement_confidence=0.9,
        measurement_timestamp=datetime.utcnow().isoformat() + 'Z',
    )


@pytest.fixture
def valid_protected_budgets():
    """Valid protected dimension budgets."""
    return ProtectedDimensionBudgets(
        required_dimensions={
            "latency_p99": 5.0,
            "recovery_time": 2.0,
        },
        applicability_justification="Latency and recovery time critical for user experience.",
    )


@pytest.fixture
def valid_isolation_attestation():
    """A valid isolation attestation."""
    return IsolationAttestation(
        isolation_method="container",
        attestation_timestamp=datetime.utcnow().isoformat() + 'Z',
        attestation_evidence="container_id_abc123",
    )


@pytest.fixture
def mock_test_environment(valid_target_metric_measurement, valid_protected_dimension_measurement, valid_isolation_attestation):
    """A mock test environment with valid measurements."""
    env = MockTestEnvironment()
    env.target_metric_measurement = valid_target_metric_measurement
    env.protected_dimension_measurements = {
        "latency_p99": valid_protected_dimension_measurement,
    }
    env.isolation_attestation = valid_isolation_attestation
    env.invariant_broken = False
    return env


@pytest.fixture
def simple_payload():
    """A simple payload that executes successfully."""
    def payload(env):
        return {"status": "success"}
    return payload


@pytest.fixture
def valid_candidate_manifest(
    valid_deficiency_trace,
    valid_improvement_promise,
    valid_authority_proof,
    valid_protected_budgets,
    simple_payload,
):
    """A valid candidate manifest for 4VP validation."""
    return CandidateManifest(
        id="candidate-001",
        backward_trace=valid_deficiency_trace,
        forward_promise=valid_improvement_promise,
        authority_proof=valid_authority_proof,
        intent_statement="Optimize p99 latency by 15% via cache layer improvement",
        execution_payload=simple_payload,
        protected_budgets=valid_protected_budgets,
        deficiency_closure_threshold=0.8,
        isolation_required=True,
    )


@pytest.fixture
def verification_engine():
    """A verification engine with baseline state."""
    return VerificationSandboxEngine(
        baseline_state={"latency_p99": 85.0, "recovery_time": 5.0},
        security_envelope={"max_consequence_level": 3},
    )
