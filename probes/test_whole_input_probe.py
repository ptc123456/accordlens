import copy
import ast
import inspect
import json
import pickle
from pathlib import Path

import cloudpickle
import pytest
from semantic_cases import cases


def test_evaluate_is_a_consensus_write():
    tree = ast.parse(Path(__file__).with_name("whole_input_probe.py").read_text(encoding="utf-8"))
    contract = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    method = next(node for node in contract.body if isinstance(node, ast.FunctionDef) and node.name == "evaluate")
    assert [ast.unparse(item) for item in method.decorator_list] == ["gl.public.write"]


def test_probe_upgrade_lifecycle(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy(str(Path(__file__).with_name("whole_input_probe.py")), sdk_version="v0.3.0-rc7")
    gl = inspect.unwrap(contract.evaluate).__globals__["gl"]
    root = gl.storage.Root.get()
    upgraders = root.upgraders.get()
    assert len(upgraders) == 1 and upgraders[0].as_bytes == bytes(direct_vm.sender)
    assert contract.get_upgrader() == upgraders[0].as_hex
    root.lock_default()
    replacement = b"# probe replacement"
    contract.upgrade(replacement)
    assert bytes(root.code.get()) == replacement
    direct_vm.sender = direct_alice
    with pytest.raises(Exception):
        contract.upgrade(b"unauthorized")
    assert bytes(root.code.get()) == replacement


def test_whole_input_boundary_and_independent_validator(direct_vm, direct_deploy):
    contract = direct_deploy(str(Path(__file__).with_name("whole_input_probe.py")), sdk_version="v0.3.0-rc7")
    helpers = inspect.unwrap(contract.evaluate).__globals__
    # The installed proxy uses functools.wraps; unwrap without private mutation.
    prepare = helpers["prepare"]
    validate = helpers["validate_answer"]
    change = "Protocol sets mode=strict."
    constraint = "Consumer requires mode=strict."
    prompt, template, cores = prepare(change, constraint)
    assert change in prompt and constraint in prompt and len(cores) == 2
    answer = copy.deepcopy(template)
    answer["consumers"][0].update(verdict="COMPATIBLE", citations=[{"source_id": "change", "start": 0, "end": len(change)}])
    direct_vm.mock_llm("ACCORDLENS WHOLE INPUT FEASIBILITY", json.dumps(answer))
    actual = json.loads(contract.evaluate(change, constraint))
    assert actual["result"] == answer
    assert direct_vm.run_validator()
    for key, value in (("graph_digest", "tampered"), ("coverage_complete", False)):
        modified = copy.deepcopy(answer)
        modified[key] = value
        assert not direct_vm.run_validator(leader_result=modified)
    modified = copy.deepcopy(answer)
    modified["consumers"][0]["verdict"] = "INCOMPATIBLE"
    assert not direct_vm.run_validator(leader_result=modified)
    assert not direct_vm.run_validator(leader_error=ValueError("transport"))
    _, leader, validator = direct_vm._captured_validators[-1]
    for function in (leader, validator):
        assert callable(pickle.loads(cloudpickle.dumps(function)))
    for invalid in ("not-json", "x" * 16385, "{}"):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            validate(invalid, template)
    with pytest.raises(ValueError, match="INPUT_BOUND"):
        contract.evaluate("x" * 65537, constraint)
    near = "a" * 65536
    near_prompt, near_template, near_cores = prepare(near, near)
    assert len(near_prompt.encode()) <= 196608
    assert sum(row["byte_length"] for row in near_template["sources"]) == 131072
    assert len(near_cores) == 16
    unicode_prompt, unicode_template, unicode_cores = prepare("ề" * 21000, "文" * 21000)
    assert len(unicode_template["sources"]) == 2 and len(unicode_cores) == 16
    assert "ề" * 21000 in unicode_prompt and "文" * 21000 in unicode_prompt


def test_condition_fields_are_independently_agreed(direct_vm, direct_deploy):
    contract = direct_deploy(str(Path(__file__).with_name("whole_input_probe.py")), sdk_version="v0.3.0-rc7")
    helpers = inspect.unwrap(contract.evaluate).__globals__
    change = "Mode is legacy; consumer may set mode=strict to migrate."
    constraint = "Mode must be strict."
    _, answer, _ = helpers["prepare"](change, constraint)
    answer["consumers"][0].update(
        verdict="CONDITIONAL",
        condition={"action_type": "CONFIG_UPDATE", "target": "mode", "required_value": "strict"},
        citations=[{"source_id": "change", "start": 0, "end": len(change)}],
    )
    direct_vm.mock_llm("ACCORDLENS WHOLE INPUT FEASIBILITY", json.dumps(answer))
    contract.evaluate(change, constraint)
    assert direct_vm.run_validator()
    for key, value in (("action_type", "VERSION_PIN"), ("target", "other"), ("required_value", "legacy")):
        altered = copy.deepcopy(answer)
        altered["consumers"][0]["condition"][key] = value
        assert not direct_vm.run_validator(leader_result=altered)
    for key, value in (("target", 42), ("required_value", ""), ("action_type", "EXECUTE_CODE")):
        altered = copy.deepcopy(answer)
        altered["consumers"][0]["condition"][key] = value
        with pytest.raises(ValueError):
            helpers["validate_answer"](altered, answer)


def test_missing_reference_and_citation_guards(direct_deploy):
    contract = direct_deploy(str(Path(__file__).with_name("whole_input_probe.py")), sdk_version="v0.3.0-rc7")
    helpers = inspect.unwrap(contract.evaluate).__globals__
    _, template, _ = helpers["prepare"]("See absent annex A.", "Must satisfy annex A.")
    answer = copy.deepcopy(template)
    answer.update(missing_references=["annex A"], unresolved_reason="MISSING_REFERENCE")
    assert helpers["validate_answer"](answer, template) == answer
    invalid = copy.deepcopy(answer)
    invalid["consumers"][0]["verdict"] = "COMPATIBLE"
    with pytest.raises(ValueError, match="MISSING_REFERENCE"):
        helpers["validate_answer"](invalid, template)
    invalid = copy.deepcopy(answer)
    invalid["sources"] = invalid["sources"] + [invalid["sources"][0]]
    with pytest.raises(ValueError, match="SOURCE_BINDING"):
        helpers["validate_answer"](invalid, template)
    for start, end in ((True, 2), (0, 99999), (-1, 2), (2, 2)):
        invalid = copy.deepcopy(answer)
        invalid["consumers"][0]["citations"] = [{"source_id": "change", "start": start, "end": end}]
        with pytest.raises(ValueError, match="CITATION_BOUND"):
            helpers["validate_answer"](invalid, template)


def test_real_model_fixture_inputs_are_complete_and_oracle_separate(direct_deploy):
    contract = direct_deploy(str(Path(__file__).with_name("whole_input_probe.py")), sdk_version="v0.3.0-rc7")
    prepare = inspect.unwrap(contract.evaluate).__globals__["prepare"]
    fixtures = cases()
    assert len(fixtures) == 11 and len({case["id"] for case in fixtures}) == 11
    for case in fixtures:
        prompt, _, _ = prepare(case["change"], case["constraint"])
        embedded = prompt.split("\nBEGIN_UNTRUSTED_JSON_DOCUMENTS\n", 1)[1].split("\nEND_UNTRUSTED_JSON_DOCUMENTS\n", 1)[0]
        assert json.loads(embedded) == {"change": case["change"], "constraint": case["constraint"]}
        assert '"expected"' not in prompt
    for case in fixtures[1:4]:
        assert len(case["change"].encode()) == len(case["constraint"].encode()) == 65536
