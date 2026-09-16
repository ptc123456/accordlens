import copy
import inspect
import json
from pathlib import Path

import pytest


SOURCE = str(Path(__file__).with_name("narrowed_evidence_probe.py"))


def answer(verdict="COMPATIBLE"):
    return {
        "verdict": verdict, "action_type": "", "target": "", "required_value": "",
        "missing_reference": "", "unresolved_reason": "", "change_start": 0, "change_end": 1,
        "constraint_start": 0, "constraint_end": 1,
    }


def test_minimal_decision_schema_and_independent_agreement(direct_vm, direct_deploy):
    contract = direct_deploy(SOURCE, sdk_version="v0.3.0-rc7")
    helpers = inspect.unwrap(contract.evaluate).__globals__
    expected = answer()
    direct_vm.mock_llm("ACCORDLENS BOUNDED EVIDENCE DECISION", json.dumps(expected))
    result = json.loads(contract.evaluate("x", "y"))
    assert result["decision"] == expected
    assert result["evidence"]["change_bytes"] == result["evidence"]["constraint_bytes"] == 1
    assert direct_vm.run_validator()
    changed = copy.deepcopy(expected)
    changed["verdict"] = "INCOMPATIBLE"
    assert not direct_vm.run_validator(leader_result=changed)


def test_fail_closed_envelope_schema_condition_and_citations(direct_deploy):
    contract = direct_deploy(SOURCE, sdk_version="v0.3.0-rc7")
    helpers = inspect.unwrap(contract.evaluate).__globals__
    _, meta = helpers["prepare"]("x" * 4000, "y" * 4000)
    with pytest.raises(Exception, match="EVIDENCE_ENVELOPE"):
        contract.evaluate("x" * 4001, "y")
    for invalid in ({}, {**answer(), "extra": 1}, {**answer(), "change_end": 4001}):
        with pytest.raises(ValueError):
            helpers["validate"](invalid, meta)
    conditional = answer("CONDITIONAL")
    conditional.update(action_type="CONFIG_UPDATE", target="mode", required_value="strict")
    assert helpers["validate"](conditional, meta) == conditional
    unresolved = answer("UNRESOLVED")
    unresolved["missing_reference"] = "Annex Z"
    unresolved["unresolved_reason"] = "MISSING_REFERENCE"
    assert helpers["validate"](unresolved, meta) == unresolved
    ambiguous = answer("UNRESOLVED")
    ambiguous["unresolved_reason"] = "AMBIGUOUS_EVIDENCE"
    assert helpers["validate"](ambiguous, meta) == ambiguous


def test_exact_source_hashes_are_contract_owned(direct_deploy):
    contract = direct_deploy(SOURCE, sdk_version="v0.3.0-rc7")
    prepare = inspect.unwrap(contract.evaluate).__globals__["prepare"]
    _, first = prepare("mode=strict", "requires strict")
    _, second = prepare("mode=legacy", "requires strict")
    assert first["change_sha256"] != second["change_sha256"]
    assert first["constraint_sha256"] == second["constraint_sha256"]
