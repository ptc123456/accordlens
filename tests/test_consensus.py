from test_coverage import m
from runtime_source import deploy_exact
import json
import pytest
import hashlib
import base64
from pathlib import Path
import copy


def install_source(vm, raw=b"Retain payload field."):
    sha = "a" * 40
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
    payload = {"name":"a.md","path":"a.md","type":"file","encoding":"base64","sha":blob,"size":len(raw),"content":base64.b64encode(raw).decode()}
    vm.mock_web("/contents/a.md", {"method":"GET", "response":{"status":200,"headers":{"content-type":b"application/json"},"body":json.dumps(payload).encode()}})
    return f"https://raw.githubusercontent.com/o/r/{sha}/a.md"


def row(verdict="COMPATIBLE"):
    return dict(verdict=verdict, action_type="", target="", required_value="", unresolved_reason="", missing_reference="")


def test_eight_conditions_and_aggregation():
    vector = [dict(row("CONDITIONAL"), action_type="VERSION_PIN", target=f"client-{i}", required_value="2") for i in range(8)]
    assert m._decision_vector(json.dumps(vector),8,[]) == vector
    assert m._aggregate(vector) == "CONDITIONAL"
    vector[0] = row("INCOMPATIBLE")
    assert m._aggregate(vector) == "INCOMPATIBLE"
    vector[1] = dict(row("UNRESOLVED"), unresolved_reason="INSUFFICIENT_EVIDENCE")
    assert m._aggregate(vector) == "UNRESOLVED"


@pytest.mark.parametrize("value", ["{}", "null", "[true]", "[]", json.dumps([dict(row(), target="hidden")]), json.dumps([dict(row(), extra="field")]), json.dumps([row(),row()]), json.dumps([dict(row("CONDITIONAL"), action_type="VERSION_PIN", target="x", required_value="")])])
def test_malformed_vectors(value):
    with pytest.raises(ValueError):
        m._decision_vector(value,1,[])


def test_duplicate_keys_and_oversize_rejected():
    with pytest.raises(ValueError):
        m._unique_json('{"verdict":"COMPATIBLE","verdict":"INCOMPATIBLE"}')
    with pytest.raises(ValueError):
        m._decision_vector(" " * 4097,1,[])
    conditions = [dict(row("CONDITIONAL"), action_type="VERSION_PIN", target="client", required_value="v" * 1024) for _ in range(8)]
    with pytest.raises(ValueError, match="MODEL_SCHEMA"):
        m._decision_vector({"decisions": conditions}, 8, [])


def test_evidence_envelope_rejects_incomplete_metadata_before_mutation():
    uri = "https://raw.githubusercontent.com/o/r/" + "a" * 40 + "/a.md"
    binding = {"graph_digest": "a" * 64, "uri": uri, "consumers": [["consumer", "owner", uri]]}
    base = {"graph_digest": "a" * 64, "outcome": "COMPATIBLE", "reason": "", "vector": [row()], "sources": [[uri, "a" * 40, "b" * 40, "c" * 64, 10, "full"]], "closure_digests": ["d" * 64], "anchors": [[['', 0, 'normative', -1, 0, 10, 10]]], "ranges": [[]], "cores": [[[0, 10, "e" * 64]]], "selected": "", "selected_digest": m._sha(b""), "selected_length": 0, "mapping": [["change", 0], ["consumer:consumer", 0]]}
    assert m._validate_evidence_envelope(base, binding)["graph_digest"] == binding["graph_digest"]
    for key, bad in (("anchors", [[]]), ("ranges", [[[0, 4, 1, 4]]]), ("cores", [[[0, 4, "bad"]]]), ("selected", "zz")):
        candidate = copy.deepcopy(base)
        candidate[key] = bad
        with pytest.raises(ValueError, match="EVIDENCE_ENVELOPE"):
            m._validate_evidence_envelope(candidate, binding)


def test_evidence_envelope_uses_one_contiguous_buffer_across_sources():
    revision = "a" * 40
    change_uri = f"https://raw.githubusercontent.com/o/r/{revision}/change.md"
    constraint_uri = f"https://raw.githubusercontent.com/o/r/{revision}/constraint.md"
    binding = {"graph_digest": "a" * 64, "uri": change_uri, "consumers": [["consumer", "owner", constraint_uri]]}
    answer = {
        "graph_digest": binding["graph_digest"], "outcome": "COMPATIBLE", "reason": "", "vector": [row()],
        "sources": [[change_uri, revision, "b" * 40, "c" * 64, 5, "full"], [constraint_uri, revision, "d" * 40, "e" * 64, 6, "full"]],
        "closure_digests": ["f" * 64, "1" * 64],
        "anchors": [[['', 0, 'normative', -1, 0, 5, 5]], [['', 0, 'normative', -1, 0, 6, 6]]],
        "ranges": [[[0, 5, 0, 5]], [[0, 6, 5, 11]]],
        "cores": [[[0, 5, "2" * 64]], [[0, 6, "3" * 64]]],
        "selected": "", "selected_digest": m._sha(b""), "selected_length": 0,
        "mapping": [["change", 0], ["consumer:consumer", 1]], "evidence_digest": "4" * 64,
    }
    assert m._validate_evidence_envelope(answer, binding)["selected_length"] == 0
    answer["ranges"][1][0][2] = 0
    with pytest.raises(ValueError, match="EVIDENCE_ENVELOPE"):
        m._validate_evidence_envelope(answer, binding)


def test_evaluation_prompt_treats_normative_scope_as_bounded_authority(monkeypatch):
    revision = "a" * 40
    uri = f"https://raw.githubusercontent.com/o/r/{revision}/change.md"
    binding = {"graph_digest": "a" * 64, "uri": uri, "consumers": [["consumer", "owner", uri]]}
    prompts = []

    def acquire(*_args, **_kwargs):
        raw = b"A complete normative compatibility statement."
        return {"raw": raw, "mode": "full", "sections": [{"id": "", "level": 0, "role": "normative", "parent": -1, "start": 0, "end": len(raw), "subtree_end": len(raw), "refs": []}], "uri": uri, "revision": revision, "blob": "b" * 40, "sha256": m._sha(raw)}

    def llm(prompt, **_kwargs):
        prompts.append(prompt)
        return {"decisions": [dict(row("CONDITIONAL"), action_type="CONFIG_UPDATE", target="endpoint", required_value="/v2/check")]}

    monkeypatch.setattr(m, "_acquire", acquire)
    answer = m._evaluate_graph(binding, lambda *_args, **_kwargs: None, llm)
    assert answer["outcome"] == "CONDITIONAL"
    assert "authoritative requirements and facts for this bounded review" in prompts[0]
    assert "do not demand outside corroboration" in prompts[0]
    assert "absent or contradictory inside the selected scope" in prompts[0]


def test_source_failure_is_a_strict_retryable_unresolved_envelope():
    uri = "https://raw.githubusercontent.com/o/r/" + "a" * 40 + "/a.md"
    binding = {"graph_digest": "a" * 64, "uri": uri, "consumers": [["consumer", "owner", uri]]}

    def unavailable(*_args, **_kwargs):
        raise RuntimeError("offline")

    answer = m._evaluate_graph(binding, unavailable, lambda *_args, **_kwargs: None)

    assert answer == m._failed_evaluation(binding, "SOURCE_UNAVAILABLE")
    assert answer["vector"] == [dict(row("UNRESOLVED"), unresolved_reason="INSUFFICIENT_EVIDENCE")]
    assert m._aggregate(answer["vector"]) == "UNRESOLVED"
    assert m._validate_evidence_envelope(answer, binding)["graph_digest"] == binding["graph_digest"]

    for key, bad in (
        ("reason", "UNKNOWN_FAILURE"),
        ("vector", []),
        ("sources", [[uri, "a" * 40, "b" * 40, "c" * 64, 10, "full"]]),
        ("selected", "00"),
    ):
        candidate = copy.deepcopy(answer)
        candidate[key] = bad
        with pytest.raises(ValueError):
            m._validate_evidence_envelope(candidate, binding)


def test_runtime_evaluation_validator_and_activation(direct_vm, direct_deploy, tmp_path):
    contract = deploy_exact(direct_deploy, tmp_path)
    uri = install_source(direct_vm)
    # gltest 0.30.0rc2 decodes mocked JSON one layer before the v0.6 runner.
    direct_vm.mock_llm("ACCORDLENS COMPATIBILITY VECTOR", json.dumps(json.dumps({"decisions": [row()]})))
    contract.create_change(uri,"a"*40,2**64)
    contract.register_dependency(0,"consumer",uri)
    contract.lock_dependency_graph(0)
    assert contract.evaluate_compatibility(0) == "COMPATIBLE"
    assert direct_vm.run_validator()
    _, leader, validator = direct_vm._captured_validators[-1]
    import cloudpickle
    cloudpickle.dumps(leader)
    cloudpickle.dumps(validator)
    answer = leader()
    for key in ("graph_digest","outcome"):
        bad = copy.deepcopy(answer)
        bad[key] = "tampered"
        assert not direct_vm.run_validator(leader_result=bad)
    # Non-authoritative presentation metadata may vary between independent
    # evaluators; it must not change the decision or immutable source binding.
    varied = copy.deepcopy(answer)
    varied["anchors"] = []
    assert direct_vm.run_validator(leader_result=varied)
    bad = copy.deepcopy(answer)
    bad["sources"][0][2] = "b" * 40
    assert not direct_vm.run_validator(leader_result=bad)
    bad = copy.deepcopy(answer)
    bad["vector"][0]["verdict"] = "INCOMPATIBLE"
    assert not direct_vm.run_validator(leader_result=bad)
    assert not direct_vm.run_validator(leader_error=ValueError("error"))
    assert json.loads(contract.get_attempt(0,0))["source_count"] == "1"
    assert contract.activate_change(0)
    with pytest.raises(Exception,match="WRONG_STATE"):
        contract.activate_change(0)


def test_runtime_source_failure_records_unresolved_and_remains_retryable(direct_vm, direct_deploy, tmp_path):
    contract = deploy_exact(direct_deploy, tmp_path)
    sha = "a" * 40
    uri = f"https://raw.githubusercontent.com/o/r/{sha}/a.md"
    direct_vm.mock_web("/contents/a.md", {"method":"GET", "response":{"status":503, "headers":{"content-type":b"application/json"}, "body":b"unavailable"}})
    contract.create_change(uri, sha, 2**64)
    contract.register_dependency(0, "consumer", uri)
    contract.lock_dependency_graph(0)

    assert contract.evaluate_compatibility(0) == "UNRESOLVED"
    assert direct_vm.run_validator()
    proposal = json.loads(contract.get_change(0))
    attempt = json.loads(contract.get_attempt(0, 0))
    result = json.loads(contract.get_consumer_result(0, 0, "consumer"))
    assert proposal["state"] == "LOCKED"
    assert proposal["attempt_count"] == "1"
    assert attempt["reason"] == "SOURCE_UNAVAILABLE"
    assert attempt["source_count"] == "0"
    assert result["result"]["verdict"] == "UNRESOLVED"
    assert result["result"]["unresolved_reason"] == "INSUFFICIENT_EVIDENCE"
    assert contract.evaluate_compatibility(0) == "UNRESOLVED"
    assert json.loads(contract.get_change(0))["attempt_count"] == "2"
