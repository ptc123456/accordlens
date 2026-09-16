import copy
import pytest
from coverage_probe import checked_text, git_blob_id, segments, verify_cover, global_input


@pytest.mark.parametrize("placement", ["beginning", "middle", "end"])
def test_full_prompt_contains_every_byte(placement):
    marker = "DECISIVE CLAUSE: NOT COMPATIBLE"
    filler = "a" * 20000
    text = {"beginning": marker + filler, "middle": filler[:10000] + marker + filler[10000:],
            "end": filler + marker}[placement]
    raw = text.encode()
    assert checked_text(raw, git_blob_id(raw), len(raw)) == text
    parts = segments(raw)
    assert global_input(raw, parts, 65536) == text
    assert marker in global_input(raw, parts, 65536)


def test_distant_exception_and_contradiction_preserved_not_judged():
    raw = ("MUST support v1. " + "x" * 20000 +
           "Exception to first clause: MUST NOT support v1.").encode()
    assert global_input(raw, segments(raw), 65536).encode() == raw


@pytest.mark.parametrize("raw", [b"a" * 8191 + "😀é漢".encode() * 20,
                                  b"\xef\xbb\xbf" + b"a\r\nb\n", b"a" * 65536],
                         ids=["unicode-boundary", "bom-line-endings", "64k-boundary"])
def test_unicode_and_exact_bytes(raw):
    parts = segments(raw)
    assert b"".join(p["text"].encode() for p in parts) == raw
    assert verify_cover(raw, parts)


@pytest.mark.parametrize("mutation", ["missing", "duplicated", "reordered", "tampered"])
def test_incomplete_cover_rejected(mutation):
    raw = b"a" * 20000
    parts = copy.deepcopy(segments(raw))
    if mutation == "missing": parts.pop()
    if mutation == "duplicated": parts.append(parts[-1])
    if mutation == "reordered": parts.reverse()
    if mutation == "tampered": parts[0]["text"] = "other"
    with pytest.raises(ValueError, match="COVERAGE_INCOMPLETE"):
        verify_cover(raw, parts)


def test_truncation_and_identity():
    raw = b"complete immutable source"
    with pytest.raises(ValueError): checked_text(raw[:-1], git_blob_id(raw), len(raw))
    with pytest.raises(ValueError): checked_text(raw[:-1], git_blob_id(raw), len(raw)-1)
    with pytest.raises(ValueError): checked_text(b"x"*65537, git_blob_id(b"x"*65537), 65537)
    with pytest.raises(ValueError): checked_text(raw, git_blob_id(raw), len(raw), status=206)
    with pytest.raises(ValueError): checked_text(raw, git_blob_id(raw), len(raw), content_type="text/html")
    with pytest.raises(ValueError): checked_text(raw, git_blob_id(raw), len(raw), encoding="gzip")
    with pytest.raises(UnicodeError): checked_text(b"\xff", git_blob_id(b"\xff"), 1)


def test_global_budget_is_not_a_truncation_permission():
    raw = b"x" * 20000
    with pytest.raises(ValueError, match="GLOBAL_CONTEXT_INCOMPLETE"):
        global_input(raw, segments(raw), 19999)
