ACCORDLENS-EVIDENCE/1
# Exhaustive compatibility change {#change normative}
This document is the complete normative change for consumers c-b and c-c. No other protocol behavior, requirement, permission, request field, response field, or dependency changes.

Consumer c-b remains supported after exactly one CONFIG_UPDATE: set endpoint to /v2/check. Its request and response requirements otherwise remain satisfied.

Consumer c-c remains supported after exactly one CONFIG_UPDATE: set response_mode to compact. Its endpoint, request, and response requirements otherwise remain satisfied.

Neither consumer has an unremediated conflict. These two explicit configuration updates are the complete set of required actions.
