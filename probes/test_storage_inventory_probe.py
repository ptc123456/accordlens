import ast
import json
from pathlib import Path
import pytest

SOURCE = Path(__file__).with_name("storage_inventory_probe.py")


def test_inventory_roundtrip_and_harness_revert(direct_vm, direct_deploy):
    contract = direct_deploy(str(SOURCE), sdk_version="v0.3.0-rc7")
    identifier = 2**255 + 1
    timestamp = 2**64 - 1
    assert contract.seed(identifier, "a:b:é", timestamp, True) == 1
    original = contract.snapshot(identifier, "a:b:é")
    data = json.loads(original)
    assert data["id"] == str(identifier)
    assert data["count"] == "1"
    records = data["records"]
    assert len(records) == 8
    assert records["proposal"]["deadline"] == timestamp
    assert records["dependency"]["consumer_id"] == "a:b:é"
    assert records["result"]["condition"] == {"action_type": "VERIFY", "target": "a:b:é", "required_value": "yes"}
    assert records["source"]["byte_length"] == 65536
    assert records["source"]["complete"] is True
    assert records["core"]["end"] == 65536
    assert records["attempt"]["timestamp"] == timestamp
    assert records["remediation"]["acknowledged"] is False
    assert records["event"]["actor"] == records["proposal"]["maintainer"]
    # Assert exact field inventory, not just a representative field per record.
    classes = {n.name: n for n in ast.parse(SOURCE.read_text()).body if isinstance(n, ast.ClassDef)}
    names = {"proposal": "Proposal", "dependency": "Dependency", "result": "ConsumerResult", "source": "SourceProjection", "core": "CoverageCore", "attempt": "Attempt", "remediation": "Remediation", "event": "Event"}
    for label, name in names.items():
        expected = {n.target.id for n in classes[name].body if isinstance(n, ast.AnnAssign)}
        assert set(records[label]) == expected
    with pytest.raises(ValueError, match="integer bound"):
        contract.seed(2**256, "bad", timestamp, False)
    assert contract.snapshot(identifier, "a:b:é") == original
    with pytest.raises(ValueError, match="label bound"):
        contract.seed(0, "é" * 33, 0, False)
    assert contract.snapshot(identifier, "a:b:é") == original
    saved = direct_vm.snapshot()
    with pytest.raises(ValueError, match="after mutation"):
        contract.intentional_error()
    # Installed Direct Mode does NOT automatically roll back this Python call.
    assert int(contract.proposal_count) == 2
    direct_vm.revert(saved)
    assert contract.snapshot(identifier, "a:b:é") == original
