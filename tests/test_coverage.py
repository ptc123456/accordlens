import importlib.util
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import pytest
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location("accordlens_source", Path(__file__).parents[1] / "contracts" / "accordlens.py")
m = importlib.util.module_from_spec(spec)
tree = ast.parse(Path(spec.origin).read_text(encoding="utf-8"))
# Pure helper tests compile the actual functions without registering a contract.
tree.body = [node for node in tree.body if not isinstance(node, ast.ClassDef) and not (isinstance(node, ast.Import) and any(alias.name == "genlayer" for alias in node.names)) and not (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "allow_storage" for target in node.targets))]
m.gl = SimpleNamespace(vm=SimpleNamespace(UserError=ValueError))
exec(compile(tree, spec.origin, "exec"), m.__dict__)
PROFILE = b"ACCORDLENS-EVIDENCE/1\n"


def test_normative_sibling_and_ancestors_are_mandatory():
    raw = PROFILE + b"# Parent {#parent informative}\nQualification.\n## Rule {#rule normative}\nKeep field.\n# Exception {#exception normative}\nPin v2.\n# History {#history informative}\nOld.\n"
    result = m._closure([m._parse_source(raw)], {"change": 0})[0]
    assert b"Qualification." in result["selected"]
    assert b"Pin v2." in result["selected"]
    assert result["omitted"] == ["history"]
    assert result["selected"] == raw[:raw.index(b"# History")]


def test_transitive_subtree_cycle_and_exact_crlf_bom():
    a = b"\xef\xbb\xbf" + PROFILE.replace(b"\n", b"\r\n") + b"# A {#a normative}\r\n@requires consumer:c#b\r\n"
    b = PROFILE + b"# B {#b informative}\n@requires change#a\n## Child {#child informative}\nImportant.\n"
    docs = [m._parse_source(a), m._parse_source(b)]
    out = m._closure(docs, {"change": 0, "consumer:c": 1})
    assert out[0]["selected"] == a
    assert out[1]["selected"] == b


def test_fenced_fake_declarations_not_structure():
    raw = PROFILE + b"# A {#a normative}\n```md\n# invalid\n@requires bad\n```\n"
    doc = m._parse_source(raw)
    assert len(doc["sections"]) == 2
    assert m._closure([doc], {"change": 0})[0]["selected"] == raw


@pytest.mark.parametrize("body", [b"# Bad\n", b"## Skip {#skip normative}\n", b"# A {#a normative}\n# A {#a informative}\n", b"```\nunclosed", b"@requires invalid\n", b"~~~\n", b"  ```\n"])
def test_unsupported_profile_fails_closed(body):
    with pytest.raises(ValueError):
        m._parse_source(PROFILE + body)


def test_missing_reference_and_overflow_never_crop():
    doc = m._parse_source(PROFILE + b"# A {#a normative}\n@requires change#missing\n")
    with pytest.raises(ValueError, match="MISSING_REFERENCE"):
        m._closure([doc], {"change": 0})
    for size in (4001, 65536):
        with pytest.raises(ValueError, match="EVIDENCE_CLOSURE"):
            m._closure([m._parse_source(b"a" * size)], {"change": 0})
    with pytest.raises(ValueError, match="EVIDENCE_CLOSURE"):
        m._closure([m._parse_source(b"x" * 3000) for _ in range(3)], {})


def test_exact_plain_boundaries_and_byte_identity():
    raw = "é".encode() * 2000
    out = m._closure([m._parse_source(raw)], {})[0]
    assert out["selected"] == raw
    assert out["ranges"] == [[0, 4000]]
    with pytest.raises(ValueError):
        m._parse_source(b"a\rb")
    with pytest.raises(UnicodeDecodeError):
        m._parse_source(b"\xff")


def test_studio_fixtures_have_complete_deterministic_closures():
    root = Path(__file__).parents[1] / "fixtures" / "studio"
    expected = {
        "compatible/change.md": "ok",
        **{f"compatible/constraint-{i:02}.md": "ok" for i in range(1, 9)},
        "conditional/change.md": "ok",
        "conditional/constraint-b.md": "ok",
        "conditional/constraint-c.md": "ok",
        "conditional/remediation-b.md": "ok",
        "conditional/remediation-c.md": "ok",
        "conditional/remediation-incomplete.md": "ok",
        "incompatible/change.md": "ok",
        "incompatible/constraint.md": "ok",
        "unresolved/change.md": "ok",
        "unresolved/constraint.md": "ok",
        "expiry/change.md": "ok",
        "closure-exception/change.md": "ok",
        "closure-overflow/constraint.md": "ok",
    }
    for relative in expected:
        raw = (root / relative).read_bytes()
        closure = m._closure([m._parse_source(raw)], {"change": 0, "consumer:c-b": 0})[0]
        assert closure["selected"]

    overflow = (root / "closure-overflow" / "change.md").read_bytes()
    assert len(overflow) > m.MAX_SELECTED_SOURCE
    with pytest.raises(ValueError, match="EVIDENCE_CLOSURE"):
        m._closure([m._parse_source(overflow)], {"change": 0})

    change = m._parse_source((root / "closure-exception" / "change.md").read_bytes())
    constraint = m._parse_source((root / "closure-exception" / "constraint.md").read_bytes())
    selected = m._closure([change, constraint], {"change": 0, "consumer:c-b": 1})
    assert b"Mandatory exception" in selected[0]["selected"]
    assert b"opaque strings" in selected[0]["selected"]


def test_studio_fixture_manifest_binds_exact_git_blobs_and_all_intents():
    manifest = json.loads((Path(__file__).parents[1] / "fixtures" / "studio" / "fixture-manifest.json").read_text(encoding="utf-8"))
    assert [row["id"] for row in manifest["operations"]] == [f"T{i:02}" for i in range(1, 50)]
    assert manifest["network"]["chainId"] == 61997
    assert manifest["conditionOracle"]["c-b"]["action_type"] == "CONFIG_UPDATE"
    assert manifest["conditionOracle"]["c-c"]["action_type"] == "CONFIG_UPDATE"
    intents = {row["id"]: row["oracle"] for row in manifest["operations"]}
    assert intents["T22"] == "ERROR NOT_CONSUMER_OWNER; unchanged"
    assert intents["T25"] == "ERROR REPLAY_REJECTED; acknowledgement count 1 unchanged"
    for row in manifest["files"]:
        raw = subprocess.check_output(["git", "cat-file", "blob", row["blobOid"]])
        assert len(raw) == row["bytes"]
        assert hashlib.sha256(raw).hexdigest() == row["sha256"]
        assert manifest["immutableFixtureRevision"] in row["url"]
    by_path = {row["path"]: row for row in manifest["files"]}
    paths = [f"fixtures/studio/conditional/{name}.md" for name in ("change", "constraint-b", "constraint-c")]
    documents = [m._parse_source(subprocess.check_output(["git", "cat-file", "blob", by_path[path]["blobOid"]])) for path in paths]
    selected = m._closure(documents, {"change": 0, "consumer:c-b": 1, "consumer:c-c": 2})
    assert sum(len(row["selected"]) for row in selected) > 1024
