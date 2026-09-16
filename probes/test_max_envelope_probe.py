import json
from pathlib import Path
from time import perf_counter
import pytest


def test_max_envelope(direct_vm, direct_deploy):
    source = Path(__file__).with_name("max_envelope_probe.py")
    contract = direct_deploy(str(source), sdk_version="v0.3.0-rc7")
    started = perf_counter()
    first = json.loads(contract.exercise(0, 2**256 - 2))
    assert {k: first[k] for k in ("sources", "anchors", "ranges", "cores", "results", "selected")} == {"sources": 9, "anchors": 1161, "ranges": 1161, "cores": 81, "results": 8, "selected": 8000}
    assert first["version"] == str(2**256 - 1)
    assert contract.verify_all() is True
    padding = 262144 - first["size"]
    assert padding >= 0
    exact = json.loads(contract.exercise(padding, 2**256 - 2))
    assert exact["size"] == 262144
    assert contract.verify_all() is True
    unchanged = contract.inspect()
    with pytest.raises(ValueError, match="storage budget"):
        contract.exercise(padding + 1, 2**256 - 2)
    assert contract.inspect() == unchanged
    with pytest.raises(ValueError, match="counter overflow"):
        contract.exercise(0, 2**256 - 1)
    assert contract.inspect() == unchanged
    print(json.dumps({"base": first, "boundary": exact, "padding": padding, "elapsed_seconds": perf_counter() - started, "mode": "Direct Mode: storage/serialization execution, NOT GenVM fuel or live consensus proof"}))
