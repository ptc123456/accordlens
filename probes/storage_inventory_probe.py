# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
from dataclasses import dataclass, asdict
import json

# Pre-release storage and ABI validation harness.
@allow_storage
@dataclass
class Proposal:
    maintainer: Address
    revision: str
    uri: str
    deadline: u64
    state: str
    graph_digest: str
    dependency_count: u16
    attempt_count: u16
    acknowledged: u16
    event_count: u32


@allow_storage
@dataclass
class Dependency:
    owner: Address
    consumer_id: str
    uri: str
    source_digest: str


@allow_storage
@dataclass
class ActionableCondition:
    action_type: str
    target: str
    required_value: str


@allow_storage
@dataclass
class ConsumerResult:
    verdict: str
    has_condition: bool
    condition: ActionableCondition
    description: str
    citations_json: str
    attempt: u16


@allow_storage
@dataclass
class SourceProjection:
    uri: str
    raw_sha256: str
    blob_oid: str
    byte_length: u32
    core_count: u16
    policy_version: str
    complete: bool
    reason: str


@allow_storage
@dataclass
class CoverageCore:
    index: u16
    start: u32
    end: u32
    sha256: str


@allow_storage
@dataclass
class Attempt:
    outcome: str
    reason: str
    graph_digest: str
    evidence_digest: str
    timestamp: u64


@allow_storage
@dataclass
class Remediation:
    acknowledged: bool
    uri: str
    evidence_digest: str
    constraint_digest: str
    condition_digest: str


@allow_storage
@dataclass
class Event:
    kind: str
    actor: Address
    timestamp: u64
    payload_json: str


class StorageInventoryProbe(gl.Contract):
    proposal_count: u256
    proposals: TreeMap[u256, Proposal]
    dependencies: TreeMap[str, Dependency]
    results: TreeMap[str, ConsumerResult]
    sources: TreeMap[str, SourceProjection]
    cores: TreeMap[str, CoverageCore]
    attempts: TreeMap[str, Attempt]
    remediation: TreeMap[str, Remediation]
    events: TreeMap[str, Event]

    def __init__(self):
        self.proposal_count = u256(0)

    @gl.public.write
    def seed(self, identifier: int, label: str, timestamp: int, complete: bool) -> int:
        if identifier < 0 or identifier >= 2**256 or timestamp < 0 or timestamp >= 2**64:
            raise ValueError("integer bound")
        if len(label.encode("utf-8")) > 64:
            raise ValueError("label bound")
        key = str(identifier) + ":" + str(len(label.encode("utf-8"))) + ":" + label
        actor = gl.message.sender_address
        self.proposals[u256(identifier)] = Proposal(actor, "r", "u", u64(timestamp), "PROBE", "g", u16(1), u16(1), u16(0), u32(1))
        self.dependencies[key] = Dependency(actor, label, "u", "s")
        self.results[key] = ConsumerResult("PROBE", True, ActionableCondition("VERIFY", label, "yes"), "display", "[]", u16(1))
        self.sources[key] = SourceProjection("u", "s", "b", u32(65536), u16(9), "probe", complete, "")
        self.cores[key] = CoverageCore(u16(8), u32(65535), u32(65536), "s")
        self.attempts[key] = Attempt("PROBE", "", "g", "s", u64(timestamp))
        self.remediation[key] = Remediation(False, "u", "e", "s", "c")
        self.events[key] = Event("PROBE", actor, u64(timestamp), "{}")
        self.proposal_count += u256(1)
        return int(self.proposal_count)

    @gl.public.view
    def snapshot(self, identifier: int, label: str) -> str:
        key = str(identifier) + ":" + str(len(label.encode("utf-8"))) + ":" + label
        # Whole record inventory copied out of storage before dataclass projection.
        values = {
            "proposal": asdict(gl.storage.copy_to_memory(self.proposals[u256(identifier)])),
            "dependency": asdict(gl.storage.copy_to_memory(self.dependencies[key])),
            "result": asdict(gl.storage.copy_to_memory(self.results[key])),
            "source": asdict(gl.storage.copy_to_memory(self.sources[key])),
            "core": asdict(gl.storage.copy_to_memory(self.cores[key])),
            "attempt": asdict(gl.storage.copy_to_memory(self.attempts[key])),
            "remediation": asdict(gl.storage.copy_to_memory(self.remediation[key])),
            "event": asdict(gl.storage.copy_to_memory(self.events[key])),
        }
        values["proposal"]["maintainer"] = values["proposal"]["maintainer"].as_hex
        values["dependency"]["owner"] = values["dependency"]["owner"].as_hex
        values["event"]["actor"] = values["event"]["actor"].as_hex
        return json.dumps({"id": str(identifier), "count": str(self.proposal_count), "records": values})

    @gl.public.write
    def intentional_error(self) -> None:
        # Deliberate diagnostic; do not treat manual fixture revert as VM atomicity.
        self.proposal_count += u256(1)
        raise ValueError("after mutation")
