"""Evolution Decision Log, Rejection Log, and Inconclusive Log systems.

Immutable/tamper-evident logging for baseline updates, candidate rejections,
and inconclusive results.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import hashlib


class DecisionOutcome(Enum):
    """Candidate validation outcomes."""
    PROMOTION_CANDIDATE = "PROMOTION_CANDIDATE"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


@dataclass
class EvolutionDecisionRecord:
    """Immutable record of a baseline update decision.
    
    Fields:
        timestamp: When the approval was granted (ISO 8601)
        approving_authority: Who approved the baseline change
        quantitative_reason: Why the change was necessary (with metrics)
        evidence_references: Pointers to validation tests/measurements
        previous_baseline_snapshot: Full state before change (JSON-serializable)
        candidate_baseline_snapshot: Full state after change
        rollback_boundary_definition: How far back can we revert?
        cryptographic_signature: Authority signature (if deployed)
        re_evaluation_trigger: When should this baseline be re-evaluated?
    """
    timestamp: str  # ISO 8601
    approving_authority: str
    quantitative_reason: str
    evidence_references: List[str]
    previous_baseline_snapshot: Dict[str, Any]
    candidate_baseline_snapshot: Dict[str, Any]
    rollback_boundary_definition: str
    cryptographic_signature: Optional[str] = None
    re_evaluation_trigger: Optional[str] = None
    record_id: str = field(default_factory=lambda: hashlib.sha256(
        datetime.utcnow().isoformat().encode()).hexdigest()[:16])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)


@dataclass
class RejectionRecord:
    """Record of a rejected or inconclusive candidate.
    
    Fields:
        candidate_id: Unique identifier for the candidate
        outcome: REJECTED or UNKNOWN
        reason: Which check/stage failed
        v_layer_trace: Which V-layers were evaluated and result
        quantitative_evidence: Measurements, thresholds, actual vs. expected
        timestamp: When rejection was recorded
        requesting_authority: Who submitted the candidate
        re_evaluation_criteria: What would be needed to retry
    """
    candidate_id: str
    outcome: DecisionOutcome
    reason: str
    v_layer_trace: Dict[str, str]  # {"V1": "PASS", "V2": "FAIL", ...}
    quantitative_evidence: Dict[str, Any]
    timestamp: str  # ISO 8601
    requesting_authority: str
    re_evaluation_criteria: str
    record_id: str = field(default_factory=lambda: hashlib.sha256(
        datetime.utcnow().isoformat().encode()).hexdigest()[:16])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["outcome"] = self.outcome.value
        return data
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class EvolutionDecisionLog:
    """Immutable/append-only log for baseline updates.
    
    Provides audit trail for all baseline changes with full provenance.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the decision log.
        
        Args:
            storage_path: Optional path to persistent storage file (append-only)
        """
        self.storage_path = storage_path
        self.records: List[EvolutionDecisionRecord] = []
    
    def record_baseline_update(self, decision: EvolutionDecisionRecord) -> str:
        """Record a baseline update decision.
        
        Args:
            decision: The update decision record
            
        Returns:
            Record ID for reference
        """
        self.records.append(decision)
        
        if self.storage_path:
            with open(self.storage_path, "a") as f:
                f.write(decision.to_json() + "\n---\n")
        
        return decision.record_id
    
    def get_all_records(self) -> List[EvolutionDecisionRecord]:
        """Retrieve all baseline update records."""
        return self.records.copy()
    
    def get_latest_baseline_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent approved baseline snapshot."""
        if self.records:
            return self.records[-1].candidate_baseline_snapshot
        return None


class RejectionLog:
    """Log for rejected and inconclusive candidates.
    
    Provides quantitative evidence for all candidate failures.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the rejection log.
        
        Args:
            storage_path: Optional path to persistent storage file
        """
        self.storage_path = storage_path
        self.rejected_records: List[RejectionRecord] = []
        self.inconclusive_records: List[RejectionRecord] = []
    
    def record_rejection(self, record: RejectionRecord) -> str:
        """Record a rejected candidate.
        
        Args:
            record: The rejection record
            
        Returns:
            Record ID for reference
        """
        if record.outcome == DecisionOutcome.REJECTED:
            self.rejected_records.append(record)
        elif record.outcome == DecisionOutcome.UNKNOWN:
            self.inconclusive_records.append(record)
        
        if self.storage_path:
            with open(self.storage_path, "a") as f:
                f.write(f"[{record.outcome.value}] {record.candidate_id}\n")
                f.write(record.to_json() + "\n---\n")
        
        return record.record_id
    
    def get_rejected_records(self) -> List[RejectionRecord]:
        """Get all rejected candidates."""
        return self.rejected_records.copy()
    
    def get_inconclusive_records(self) -> List[RejectionRecord]:
        """Get all inconclusive candidates."""
        return self.inconclusive_records.copy()
    
    def get_candidate_history(self, candidate_id: str) -> List[RejectionRecord]:
        """Get all records for a specific candidate."""
        all_records = self.rejected_records + self.inconclusive_records
        return [r for r in all_records if r.candidate_id == candidate_id]
