ACCORDLENS-EVIDENCE/1
# Complete protocol interface delta {#change normative}
This is the complete protocol change. Before revision, the request endpoint is /v1/check. After revision, the request endpoint is /v2/check. In both revisions the request body is UTF-8 JSON {"artifact":"string"}; the response is UTF-8 JSON {"compatible":"boolean"}; authentication, authorization, transport, and error semantics are unchanged. The old endpoint is removed.

Any consumer capable of sending the same request to /v2/check remains compatible after changing only its configured endpoint from /v1/check to /v2/check. The required action is CONFIG_UPDATE, target endpoint, required value /v2/check. No other protocol behavior or requirement changes.
