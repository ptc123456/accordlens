import json
from pathlib import Path
import pytest
import importlib.util
import ast
from types import SimpleNamespace
from runtime_source import deploy_exact

source = Path(__file__).parents[1] / "contracts" / "accordlens.py"
tree = ast.parse(source.read_text(encoding="utf-8"))
tree.body = [node for node in tree.body if not isinstance(node, ast.ClassDef) and not (isinstance(node, ast.Import) and any(alias.name == "genlayer" for alias in node.names)) and not (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "allow_storage" for target in node.targets))]
ns = {"gl": SimpleNamespace(vm=SimpleNamespace(UserError=ValueError))}
exec(compile(tree, str(source), "exec"), ns)


def test_remediation_is_bound_to_owner_and_fails_closed(direct_vm, direct_deploy, tmp_path):
    contract = deploy_exact(direct_deploy, tmp_path)
    uri = "https://raw.githubusercontent.com/o/r/" + "a" * 40 + "/a.md"
    contract.create_change(uri, "a" * 40, 2**64)
    contract.register_dependency(0, "consumer", uri)
    owner = direct_vm.sender
    contract.lock_dependency_graph(0)
    # No accepted conditional attempt exists; no evidence can authorize a write.
    with pytest.raises(Exception, match="WRONG_STATE"):
        contract.acknowledge_condition(0, "consumer", uri)
    assert json.loads(contract.get_change(0))["state"] == "LOCKED"
    assert owner == direct_vm.sender
    assert json.loads(contract.get_remediation_attempts(0, "consumer", 0, 20))["items"] == []
    with pytest.raises(Exception, match="DEPENDENCY_NOT_FOUND"):
        contract.get_remediation_attempts(0, "unknown", 0, 20)


def test_remediation_result_is_exact_and_fail_closed():
    assert ns["_remediation_result"]({"verified": True, "reason": "VERIFIED"})["verified"] is True
    assert ns["_remediation_result"]({"verified": False, "reason": "NOT_SATISFIED"})["verified"] is False
    for value in ({"verified": True, "reason": "NOT_SATISFIED"}, {"verified": False, "reason": "VERIFIED"}, {"verified": True, "reason": "x"}, {"verified": 1, "reason": "VERIFIED"}):
        with pytest.raises(ValueError, match="MODEL_SCHEMA"):
            ns["_remediation_result"](value)
    with pytest.raises(ValueError, match="MODEL_SCHEMA"):
        ns["_remediation_result"]({"verified": False, "reason": "NOT_SATISFIED", "padding": "x" * 300})


def test_malformed_remediation_reply_stays_false_and_false_reason_variance_converges():
    safe = ns["_remediation_safe_result"]
    equal = ns["_remediation_consensus_equal"]
    assert safe({"unexpected": "reply"}) == {"verified": False, "reason": "INSUFFICIENT_EVIDENCE"}
    assert safe({"verified": True, "reason": "NOT_SATISFIED"})["verified"] is False
    assert safe({"verified": 1, "reason": "VERIFIED"})["verified"] is False
    assert safe({"verified": True, "reason": "VERIFIED"})["verified"] is True
    malformed = {**safe({"unexpected": "reply"}), "evidence_digest": "a" * 64}
    other_false = {"verified": False, "reason": "NOT_SATISFIED", "evidence_digest": "a" * 64}
    assert equal(malformed, other_false)
    assert not equal(malformed, {"verified": True, "reason": "VERIFIED", "evidence_digest": "a" * 64})
    assert not equal(malformed, {**other_false, "evidence_digest": "b" * 64})
