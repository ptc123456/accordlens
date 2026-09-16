import json
import pickle
from pathlib import Path
import pytest


def test_runtime_roundtrip_and_validator(direct_vm, direct_deploy):
    contract = direct_deploy(str(Path(__file__).with_name("runtime_probe.py")), sdk_version="v0.3.0-rc7")
    assert contract.roundtrip("one", b"full source", 2) == 1
    snapshot = contract.snapshot("one", 0, 8)
    assert snapshot["bytes"] == "11"
    assert snapshot["action"] == "VERIFY"
    assert snapshot["numeric"] == "2"
    assert json.loads(snapshot["page"]) == ["one"]
    with pytest.raises(ValueError, match="page bound"):
        contract.snapshot("one", 0, 9)
    with pytest.raises(ValueError, match="probe bound"):
        contract.roundtrip("two", b"x", 9)
    direct_vm.check_pickling = True
    direct_vm.mock_llm("PROBE", "yes")
    result = json.loads(contract.consensus_probe("one"))
    assert direct_vm.run_validator()
    # Direct storage mutation is a local probe control, not a public method.
    original_description = contract.records["one"].description
    contract.records["one"].description = "different display prose"
    assert json.loads(contract.consensus_probe("one")) == result
    assert direct_vm.run_validator()
    contract.records["one"].description = original_description
    for position in range(4):
        altered = {"binding": list(result["binding"]), "answer": "yes"}
        altered["binding"][position] = "tampered"
        assert not direct_vm.run_validator(leader_result=altered)
    assert not direct_vm.run_validator(leader_error=ValueError("missing"))
    # Installed unsafe Direct Mode bypasses automatic pickling. Check both
    # captured functions explicitly; inspection here does not mutate harness.
    import cloudpickle
    _, leader, validator = direct_vm._captured_validators[-1]
    for function in (leader, validator):
        encoded = cloudpickle.dumps(function)
        assert callable(pickle.loads(encoded))
    assert contract.snapshot("one", 0, 8) == snapshot
