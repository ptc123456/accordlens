import json
from pathlib import Path
from runtime_source import deploy_exact
import pytest


def test_state_authority_deadline_and_pagination(direct_vm, direct_deploy, direct_alice, tmp_path):
    direct_vm.warp("2030-01-01T00:00:00Z")
    contract = deploy_exact(direct_deploy, tmp_path)
    uri = "https://raw.githubusercontent.com/o/r/" + "a" * 40 + "/a.md"
    deadline = 1893456060
    owner = direct_vm.sender
    assert contract.create_change(uri, "a" * 40, deadline) == 0
    assert contract.register_dependency(0, "consumer", uri)
    before = contract.get_change(0)
    direct_vm.sender = direct_alice
    with pytest.raises(Exception, match="NOT_MAINTAINER"):
        contract.lock_dependency_graph(0)
    assert contract.get_change(0) == before
    direct_vm.sender = owner
    direct_vm.warp("2030-01-01T00:01:00Z")
    assert len(contract.lock_dependency_graph(0)) == 64
    before = contract.get_change(0)
    with pytest.raises(Exception, match="WRONG_STATE"):
        contract.register_dependency(0, "late", uri)
    with pytest.raises(Exception, match="WRONG_STATE"):
        contract.activate_change(0)
    assert contract.get_change(0) == before
    assert json.loads(contract.get_events(0, 999, 20))["items"] == []
    with pytest.raises(Exception, match="PAGE_LIMIT"):
        contract.get_events(0, 0, 21)
    assert contract.create_change(uri, "a" * 40, deadline + 1) == 1
    direct_vm.warp("2030-01-01T00:01:01Z")
    with pytest.raises(Exception, match="DEADLINE_OPEN"):
        contract.expire_change(1)
    direct_vm.warp("2030-01-01T00:01:02Z")
    assert contract.expire_change(1)
    assert json.loads(contract.get_change(1))["state"] == "EXPIRED"
