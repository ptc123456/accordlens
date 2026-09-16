"""Deterministic transport/coverage experiment. NOT an LLM adjudicator."""
from hashlib import sha1, sha256

MAX_BYTES = 65536
CORE_BYTES = 8192


def git_blob_id(raw):
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def checked_text(raw, expected_blob, expected_size, status=200,
                 content_type="text/plain", encoding="identity"):
    if status != 200 or content_type.split(";")[0].strip().lower() not in (
        "text/plain", "text/markdown", "text/x-markdown"
    ) or encoding != "identity":
        raise ValueError("SOURCE_UNSUPPORTED")
    if not 0 < len(raw) <= MAX_BYTES or len(raw) != expected_size:
        raise ValueError("SOURCE_SIZE_OR_COMPLETENESS")
    if git_blob_id(raw) != expected_blob:
        raise ValueError("SOURCE_IDENTITY")
    text = raw.decode("utf-8", errors="strict")
    if "\x00" in text:
        raise ValueError("SOURCE_BINARY")
    return text


def segments(raw):
    """UTF-8-safe, non-overlapping partition; offsets address RAW bytes."""
    raw.decode("utf-8", errors="strict")
    out = []
    start = 0
    while start < len(raw):
        end = min(start + CORE_BYTES, len(raw))
        while end < len(raw) and raw[end] & 0xC0 == 0x80:
            end -= 1
        body = raw[start:end]
        out.append({"index": len(out), "start": start, "end": end,
                    "sha256": sha256(body).hexdigest(), "text": body.decode("utf-8")})
        start = end
    return out


def verify_cover(raw, parts):
    # Exact partition verification, not a model's self-reported complete flag.
    if parts != segments(raw):
        raise ValueError("COVERAGE_INCOMPLETE")
    return True


def global_input(raw, parts, budget_bytes):
    verify_cover(raw, parts)
    # No summary-only global pass. All original bytes must fit the global input.
    if len(raw) > budget_bytes:
        raise ValueError("GLOBAL_CONTEXT_INCOMPLETE")
    return raw.decode("utf-8")
