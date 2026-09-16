# Submission scorecard

Category: **PROJECT**
Validity gate: **PASS**

## GenLayer fit — 5/5

GenLayer validator consensus is central to deciding whether an immutable protocol revision is compatible with independently registered consumer constraints. Consequential `COMPATIBLE`, `CONDITIONAL`, `INCOMPATIBLE`, and retryable `UNRESOLVED` outcomes are recorded on-chain and verified through the complete Studio Dev matrix and public Vercel journey.

Limitation: external GitHub availability can delay a conclusive result, intentionally leaving the proposal safely retryable.

## Contract quality — 5/5

The contract implements exact Git object and complete decoded-byte verification, a bounded relevant-evidence closure, independent validator re-fetch and consequence comparison, consumer-bound remediation, canonical graph locking, authorization checks, safe terminal states, and bounded projections. Evidence includes 74 passing contract/pure tests and 45 finalized Studio transactions.

Limitation: the intentionally frozen contract requires replacement deployment and complete retesting for any source defect.

## Engineering — 4/5

The public release includes reproducible version bindings, transaction recovery, bounded RPC scheduling, 38 passing frontend tests, 74 passing contract/pure tests, lint/schema/type/build/dependency checks, exact source/deployment parity, and public verification evidence.

Limitation: four Windows Direct Mode lifecycle tests remain blocked by the disclosed installed-harness loader incompatibility; the same behavior is covered by the current contract's live Studio matrix.

## Frontend / UX — 4/5

The two-layer responsive product provides a public landing page and guide, open proposal reads, explicit MetaMask/OKX/Rabby selection, disconnected reload, real transaction hashes and Explorer links, lifecycle-specific progress, same-hash recovery without replay, and authoritative result display. A fresh OKX journey completed proposal creation through `ACTIVATED / COMPATIBLE`.

Limitation: the lazily loaded SDK contract chunk remains above 500 kB uncompressed, while the first public layer stays lightweight.

## Overall assessment

AccordLens is a complete, independently verifiable GenLayer product with a substantive consensus trust problem, rigorous fail-closed contract behavior, and a tested public experience.

Submission recommendation: **READY**
