from test_coverage import m
import pytest
import base64
import hashlib
import json
from types import SimpleNamespace

SHA = "a" * 40


def test_immutable_url_canonicalization():
    expected = f"https://raw.githubusercontent.com/owner/repo/{SHA}/docs/change.md"
    assert m._source_url(f"https://github.com/owner/repo/blob/{SHA}/docs/change.md", SHA)["uri"] == expected
    assert m._source_url(expected)["revision"] == SHA


@pytest.mark.parametrize("tail", ["main/a.md", "a" * 39 + "/a.md", SHA + "/../a.md", SHA + "//a.md", SHA + "/%2e/a.md", SHA + "/a.pdf", SHA + "/a.md#x", SHA + "/a.md?q=x"])
def test_invalid_path(tail):
    with pytest.raises(ValueError):
        m._source_url("https://raw.githubusercontent.com/o/r/" + tail)


@pytest.mark.parametrize("host", ["http://github.com", "https://github.com.evil", "https://user@github.com", "https://github.com:443"])
def test_invalid_origin(host):
    with pytest.raises(ValueError):
        m._source_url(host + "/o/r/blob/" + SHA + "/a.md")


def test_revision_mismatch():
    with pytest.raises(ValueError, match="REVISION_MISMATCH"):
        m._source_url(f"https://raw.githubusercontent.com/o/r/{SHA}/a.md", "b" * 40)


def source_server(raw=b"Complete source.", mutate=None):
    oid = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
    payload = {"name": "a.md", "path": "a.md", "type": "file", "encoding": "base64", "sha": oid, "size": len(raw), "content": base64.b64encode(raw).decode()}
    if mutate:
        mutate(payload)
    calls = []
    def get(url, headers):
        calls.append(url)
        assert url == f"https://api.github.com/repos/o/r/contents/a.md?ref={SHA}"
        return SimpleNamespace(status=200, body=json.dumps(payload).encode(), headers={"content-type": b"application/json"})
    return get, calls


def test_full_git_blob_identity_and_call_count():
    raw = b"\xef\xbb\xbfExact\r\nbytes."
    get, calls = source_server(raw)
    doc = m._acquire(f"https://raw.githubusercontent.com/o/r/{SHA}/a.md", get)
    assert doc["raw"] == raw and doc["sha256"] == hashlib.sha256(raw).hexdigest()
    assert len(calls) == 1


def test_each_distinct_source_uses_one_contents_request():
    sources = {f"{index}.md": f"Source {index}.".encode() for index in range(8)}
    calls = []
    def get(url, headers):
        calls.append(url)
        assert headers["User-Agent"] == "AccordLens-Contract"
        assert headers["X-GitHub-Api-Version"] == "2022-11-28"
        path = url.split("/contents/", 1)[1].split("?", 1)[0]
        raw = sources[path]
        oid = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
        payload = {"name": path, "path": path, "type": "file", "encoding": "base64", "sha": oid, "size": len(raw), "content": base64.b64encode(raw).decode()}
        return SimpleNamespace(status=200, body=json.dumps(payload).encode(), headers={"content-type": b"application/json"})

    cache = {}
    for path, raw in sources.items():
        doc = m._acquire(f"https://raw.githubusercontent.com/o/r/{SHA}/{path}", get, cache)
        assert doc["raw"] == raw
    assert len(calls) == 8
    assert all("/contents/" in url and url.endswith("?ref=" + SHA) for url in calls)


@pytest.mark.parametrize("mutation", [lambda p: p.update(type="dir"), lambda p: p.update(encoding="utf-8"), lambda p: p.update(path="other.md"), lambda p: p.update(name="other.md"), lambda p: p.update(sha="d" * 40), lambda p: p.update(size=True), lambda p: p.update(content="***")])
def test_provenance_rejects_ambiguous_and_wrong_blob(mutation):
    get, _ = source_server(mutate=mutation)
    with pytest.raises(ValueError):
        m._acquire(f"https://raw.githubusercontent.com/o/r/{SHA}/a.md", get)


@pytest.mark.parametrize("content", ["Y Q==", "YQ==\r\n", "YQ=", "YQ===", ""])
def test_noncanonical_base64_rejected(content):
    get, _ = source_server(b"a", lambda payload: payload.update(content=content))
    with pytest.raises(ValueError):
        m._acquire(f"https://raw.githubusercontent.com/o/r/{SHA}/a.md", get)


def test_github_wrapped_base64_is_accepted():
    raw = b"a" * 80
    encoded = base64.b64encode(raw).decode()
    get, _ = source_server(raw, lambda payload: payload.update(content=encoded[:60] + "\n" + encoded[60:] + "\n"))
    assert m._acquire(f"https://raw.githubusercontent.com/o/r/{SHA}/a.md", get)["raw"] == raw


@pytest.mark.parametrize("body", [b"[]", b"{}", b"null", b'{"type":"file","type":"dir"}'])
def test_contents_requires_one_unambiguous_file_object(body):
    def get(_url, headers):
        return SimpleNamespace(status=200, body=body, headers={"content-type": b"application/json"})
    with pytest.raises(ValueError):
        m._acquire(f"https://raw.githubusercontent.com/o/r/{SHA}/a.md", get)


@pytest.mark.parametrize("status", [404, 410, 429, 500, 503])
def test_contents_non_200_is_unavailable(status):
    def get(_url, headers):
        return SimpleNamespace(status=status, body=b"unavailable", headers={"content-type": b"application/json"})
    with pytest.raises(ValueError, match="SOURCE_UNAVAILABLE"):
        m._acquire(f"https://raw.githubusercontent.com/o/r/{SHA}/a.md", get)


def test_same_exact_source_reuses_only_evaluator_local_verified_payload():
    get, calls = source_server()
    cache = {}
    uri = f"https://raw.githubusercontent.com/o/r/{SHA}/a.md"
    assert m._acquire(uri, get, cache)["raw"] == m._acquire(uri, get, cache)["raw"]
    assert len(calls) == 1


@pytest.mark.parametrize("status,mime,encoding", [(404,b"text/plain",b"identity"),(429,b"text/plain",b"identity"),(500,b"text/plain",b"identity"),(200,b"text/html",b"identity"),(200,b"text/plain",b"gzip")])
def test_http_rejects(status,mime,encoding):
    with pytest.raises(ValueError):
        m._response_bytes(SimpleNamespace(status=status, body=b"body", headers={"content-type":mime,"content-encoding":encoding}))
