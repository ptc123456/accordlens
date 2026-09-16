# Source policy

AccordLens accepts HTTPS GitHub or raw GitHub Markdown/text documents pinned to a lowercase 40-character commit. Credentials, fragments, ports, traversal, encoded separators, unsupported extensions and revision mismatches are rejected.

Each file is acquired through GitHub's Contents API at the exact requested commit and path before parsing. The response must identify one regular file and contain canonical base64 whose complete decoded bytes match both its declared size and recomputed Git blob SHA-1. Requests use the required application identity and pinned REST API version. Every distinct source requires one request per evaluator; validators acquire and verify sources independently, with no cache shared across consensus participants.

The supported evidence profile preserves UTF-8 bytes and recognizes normative sections, informative sections, fenced examples and explicit references. Normative sections and required ancestors are mandatory. Missing references, unsupported syntax and evidence exceeding the bounded envelope return `UNRESOLVED`; the contract never silently truncates a document or treats a summary as the whole source.
