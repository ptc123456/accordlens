# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
from dataclasses import dataclass
import json

# LOCAL FEASIBILITY ONLY. Not a release contract or product implementation.
@allow_storage
@dataclass
class ActionableCondition:
    action_type: str
    target: str
    required_value: str


@allow_storage
@dataclass
class Projection:
    actor: Address
    source_digest: str
    byte_count: u32
    count: u16
    complete: bool
    condition: ActionableCondition
    description: str


class RuntimeProbe(gl.Contract):
    records: TreeMap[str, Projection]
    history: DynArray[str]
    sequence: u256
    numeric_keys: TreeMap[u256, u64]

    def __init__(self):
        self.sequence = u256(0)

    @gl.public.write
    def roundtrip(self, key: str, raw: bytes, count: int) -> int:
        if len(key) > 64 or len(raw) > 65536 or count < 0 or count > 8:
            raise ValueError("probe bound")
        self.records[key] = Projection(
            gl.message.sender_address, raw.hex(), u32(len(raw)), u16(count),
            True, ActionableCondition("VERIFY", "probe", "yes"), "display only",
        )
        self.history.append(key)
        self.numeric_keys[self.sequence] = u64(count)
        self.sequence += u256(1)
        return int(self.sequence)

    @gl.public.view
    def snapshot(self, key: str, offset: int, limit: int) -> dict[str, str]:
        if offset < 0 or limit < 1 or limit > 8:
            raise ValueError("page bound")
        record = self.records[key]
        return {"actor": record.actor.as_hex,
                "bytes": str(record.byte_count),
                "action": record.condition.action_type,
                "description": record.description,
                "numeric": str(self.numeric_keys[u256(0)]),
                "page": json.dumps([self.history[i] for i in range(offset, min(offset + limit, len(self.history)))])}

    @gl.public.write
    def consensus_probe(self, key: str) -> str:
        # Explicit primitive copy: closures never capture self or storage proxies.
        record = self.records[key]
        binding = (record.condition.action_type, record.condition.target,
                   record.condition.required_value, record.source_digest)

        def leader():
            # Actual LLM transport is mocked in local tests, never contacted here.
            answer = gl.nondet.exec_prompt("PROBE only: return yes")
            return {"binding": list(binding), "answer": answer}

        def validator(result):
            if not isinstance(result, gl.vm.Return):
                return False
            return result.calldata == leader()

        result = gl.vm.run_nondet_unsafe(leader, validator)
        return json.dumps(result)
