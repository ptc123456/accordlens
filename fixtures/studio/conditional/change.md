ACCORDLENS-EVIDENCE/1
# Endpoint configuration {#change normative}
The protocol moves requests from /v1/check to /v2/check. The old endpoint is retired. Consumers remain supported after a CONFIG_UPDATE setting endpoint=/v2/check.
Endpoint selection remains a consumer-local configuration value. The same request format and consumer ownership account remain valid after applying the new endpoint; this endpoint change does not grant a new signing permission.
# Response mode {#mode normative}
The default response mode changes from compact to strict. Consumers that require compact responses remain supported after setting response_mode to compact.
