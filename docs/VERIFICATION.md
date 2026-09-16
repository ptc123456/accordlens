# Verification

Public source snapshot: `5d85cda60bbf8184d68f406d061e1caa4f329166`; tree `e2ed9716af24c9cb43088e02f5d1fa0b2a8eb723`. The release contract, frontend source, fixtures, documentation and Explorer assets are available from this clean public history.

The release contract passed a fresh Studio Dev matrix on chain `61997`. All 45 retained transactions have unique hashes, finalized with `MAJORITY_AGREE`, and match their expected semantic execution result. The complete public transaction, actor, execution and readback ledger is available in [STUDIO-MATRIX.md](STUDIO-MATRIX.md).

## Verified journeys

- Compatible: eight-consumer bounded graph, authorization failures, lock, evaluation, activation and replay rejection.
- Conditional: consumer-bound remediation, incomplete evidence without state advance, complete evidence, activation and replay rejection.
- Incompatible: deterministic rejection and wrong-state activation rejection.
- Unresolved: unavailable evidence retry and oversized closure fail closed in `LOCKED / UNRESOLVED`.
- Evidence boundary: revision mismatch rejection, full-source identity, bounded event/dependency pagination and expiry.

Expected execution errors were limited to authorization, wrong-state, replay and revision-mismatch cases; authoritative readbacks proved unchanged state after each rejection. The final live proposals cover `ACTIVATED / COMPATIBLE`, `ACTIVATED / CONDITIONAL`, `REJECTED / INCOMPATIBLE`, retryable `LOCKED / UNRESOLVED`, and `EXPIRED`.

The public application is bound only to `0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7`. Exact local results are: `npm test -- --run` — 38/38 PASS; `py -3.13 -m pytest tests -q -p no:cacheprovider` — 74 PASS and four disclosed Direct Mode loader failures; `py -3.13 -m pytest probes -q -p no:cacheprovider` — 33/33 PASS. The four failures are not counted as passing. TypeScript, build, lint/schema, pip check and npm production audit PASS.

The public Vercel journey is recorded in [VERCEL-E2E.md](VERCEL-E2E.md). Proposal 7 completed a fresh independent-wallet compatible lifecycle through activation, retained every consequential transaction hash, reconciled pending state without replay, returned to disconnected state after reload and remained publicly readable.

Known limitations are the bounded evidence envelope, external GitHub availability, intentional contract immutability and a non-blocking lazy SDK chunk-size warning. Four Direct Mode tests fail before contract initialization because of the installed testing-harness fd0/namespace incompatibility; their lifecycle behavior is proven by the current contract's live Studio matrix.
