# Verification

Runtime release commit: `fa9168369d06e9bfa696f04c3028ceaf3bd266c6`; tree `c8f5be2e690871437055749880cd6b81fb256302`. Later commits add public documentation and Explorer assets without changing the contract, frontend runtime, dependencies, configuration, or production bundle.

The release contract passed a fresh Studio Dev matrix on chain `61997`. All 45 retained transactions have unique hashes, finalized with `MAJORITY_AGREE`, and match their expected semantic execution result.

## Verified journeys

- Compatible: eight-consumer bounded graph, authorization failures, lock, evaluation, activation and replay rejection.
- Conditional: consumer-bound remediation, incomplete evidence without state advance, complete evidence, activation and replay rejection.
- Incompatible: deterministic rejection and wrong-state activation rejection.
- Unresolved: unavailable evidence retry and oversized closure fail closed in `LOCKED / UNRESOLVED`.
- Evidence boundary: revision mismatch rejection, full-source identity, bounded event/dependency pagination and expiry.

Expected execution errors were limited to authorization, wrong-state, replay and revision-mismatch cases; authoritative readbacks proved unchanged state after each rejection. The final live proposals cover `ACTIVATED / COMPATIBLE`, `ACTIVATED / CONDITIONAL`, `REJECTED / INCOMPATIBLE`, retryable `LOCKED / UNRESOLVED`, and `EXPIRED`.

The public application is bound only to `0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7`. Local unit, contract, type, build and dependency checks were rerun on the runtime release: frontend 38/38 PASS; contract/pure 74 PASS with four disclosed stale Direct Mode lifecycle tests not counted as passing; TypeScript, build, lint/schema, pip check and npm production audit PASS.

The public Vercel journey is recorded in [VERCEL-E2E.md](VERCEL-E2E.md). Proposal 7 completed a fresh independent-wallet compatible lifecycle through activation, retained every consequential transaction hash, reconciled pending state without replay, returned to disconnected state after reload and remained publicly readable.

Known limitations are the bounded evidence envelope, external GitHub availability, intentional contract immutability and a non-blocking lazy SDK chunk-size warning. Four Direct Mode tests fail before contract initialization because of the installed testing-harness fd0/namespace incompatibility; their lifecycle behavior is proven by the current contract's live Studio matrix.
