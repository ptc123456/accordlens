ACCORDLENS-EVIDENCE/1
# Complete consumer capability and current state {#constraint normative}
This is the complete constraint for consumer c-b. It sends UTF-8 JSON {"artifact":"string"} and requires UTF-8 JSON {"compatible":"boolean"}. It supports a configurable HTTPS endpoint and is currently configured as /v1/check. It is capable of setting endpoint to /v2/check without code, schema, authentication, authorization, transport, or error-handling changes.

Therefore the protocol change preserves every consumer requirement after exactly one action: CONFIG_UPDATE, target endpoint, required value /v2/check. No requirement, reference, or dependency is omitted.
