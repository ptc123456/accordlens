# AccordLens

AccordLens is a GenLayer compatibility council that binds a protocol change to immutable source evidence and records a fail-closed verdict for every dependent consumer.

## Verified release

- **Contract:** [`0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7`](https://explorer-studio-dev.genlayer.com/address/0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7)
- **Network:** GenLayer Studio Devnet, chain ID `61997`
- **Deployment:** [`0xc13aaf…84902`](https://explorer-studio-dev.genlayer.com/transactions/0xc13aaf59455cf92fb15b0b218793df174fb7a67131c3433c449b0a2f56784902)
- **Application:** [accordlens.vercel.app](https://accordlens.vercel.app)
- **Evidence:** [verification record](docs/VERIFICATION.md) · [deployment identity](docs/DEPLOYMENT.md) · [live Vercel E2E](docs/VERCEL-E2E.md) · [submission scorecard](docs/SCORECARD.md)

## The trust problem

A protocol maintainer can claim a change is safe while consumers depend on different constraints, source revisions or remediation requirements. A browser or centralized API could also omit evidence, truncate a document or present a verdict that was never accepted on-chain. AccordLens makes the exact revision, dependency graph, evidence identity, verdict and state transition independently reproducible.

## Why GenLayer

Compatibility is not a simple deterministic lookup. Validators fetch the same immutable GitHub Contents API objects, verify complete decoded bytes and Git blob identity, build the declared evidence closure, and independently evaluate each consumer constraint. They agree on consequential fields—not free-form prose—before the contract records `COMPATIBLE`, `CONDITIONAL`, `INCOMPATIBLE` or retryable `UNRESOLVED`. Only an agreed on-chain result can unlock remediation or activation.

## Product journeys

1. A maintainer creates a proposal with an exact 40-character commit, source URL and deadline.
2. Consumer wallets register constraints while the proposal is `DRAFT`.
3. The maintainer locks the dependency graph; its canonical digest cannot change.
4. Anyone can trigger evaluation. Missing, malformed, ambiguous or over-limit evidence fails closed as `UNRESOLVED`.
5. `COMPATIBLE` becomes activatable. `CONDITIONAL` requires evidence from each bound consumer wallet. `INCOMPATIBLE` is rejected.
6. Activation and expiry are permissionless once their exact preconditions hold.

The frontend has two layers: `/` explains the evidence boundary without requiring a wallet; `/council` provides public reads and wallet-authorized actions; `/how-it-works` explains consensus and recovery.

## Architecture and source of truth

- **Intelligent Contract:** owns proposals, consumer authorization, graph locking, evaluation attempts, remediation acknowledgements, terminal states and paginated views.
- **GenLayer validators:** independently acquire and interpret bounded, byte-verified evidence under the contract's equivalence rule.
- **Frontend:** discovers MetaMask, OKX Wallet and Rabby through EIP-6963, starts disconnected after reload, submits writes through the selected provider and reconciles finality before readback.
- **Same-origin RPC proxy:** forwards bounded public requests to Studio Devnet; it is transport only and never invents proposal state.

The contract is the authoritative state. Local storage retains only a narrowly validated pending-write journal for recovery; it cannot create a verdict or mark a write successful.

## Intelligent Contract

The state machine is `DRAFT → LOCKED → ACTIVATABLE/REMEDIATION/REJECTED`, with terminal `ACTIVATED` and `EXPIRED`; `UNRESOLVED` remains safely retryable in `LOCKED`. Seven write methods cover creation, dependency registration, graph lock, evaluation, remediation, activation and expiry. Eleven bounded views expose proposals, attempts, results, remediation and events. Validators independently refetch evidence and compare source identity, decision and remediation consequence fields. No value is transferred.

The contract is **intentionally frozen**. A defect requires a new deployment, complete Studio retesting, frontend rewiring and replacement evidence.

## Transaction lifecycle and recovery

The UI separates wallet approval, submission, finality, semantic execution and authoritative readback. A signature or hash is never called success. A pending write is keyed by chain, contract, account, method and typed arguments; reload resumes the same hash rather than replaying it. Deterministic errors remain errors, ambiguous operations are reconciled, and expected rejections must leave authoritative state unchanged.

## Run locally

Requirements: Node.js 22+, npm, Python 3.13 and the GenLayer testing/lint toolchain described in [deployment identity](docs/DEPLOYMENT.md).

```bash
npm ci
npm run dev
```

No environment variable is required for the verified contract. `VITE_CONTRACT_ADDRESS` may override it only for an explicitly separate development deployment. The Vite and production same-origin `/api` proxy target `https://studio-dev.genlayer.com/api`.

## Tests and verification

```bash
npm test
npm run typecheck
npm run build
npm audit --omit=dev
python -m pytest tests -q -p no:cacheprovider
genvm-lint check contracts/accordlens.py
```

Current exact-release results: frontend `38/38` PASS; contract/pure suite `74` PASS with four disclosed Direct Mode lifecycle tests not counted as passing; TypeScript, production build, lint/schema, pip check and npm production audit PASS. The four harness-blocked lifecycle cases are covered by the current contract's live Studio matrix: 45 unique finalized transactions across compatible, conditional remediation, incompatible, unresolved/retry, expiry, authorization, replay and bounded-read paths. A separate public Vercel journey completed proposal 7 from creation through `ACTIVATED / COMPATIBLE`. See [verification evidence](docs/VERIFICATION.md).

## Security boundaries

- Only HTTPS GitHub API URLs pinned to the declared owner/repository/commit/path profile are accepted.
- Complete decoded bytes, declared size and Git blob SHA-1 must agree before interpretation.
- Source material is untrusted data, never prompt instructions.
- Validators compare every field that can change contract state; descriptive prose cannot change remediation acceptance.
- Missing or excessive evidence returns `UNRESOLVED`; it cannot authorize activation.
- Wallet state is never restored as connected after reload, and unsupported providers are not silently selected.

## Known limitations

- The supported evidence profile is deliberately bounded: at most 9 unique source files, 64 KiB per file, 128 KiB total and 8,000 selected evidence bytes. Larger or unprovable closures return `UNRESOLVED`.
- GitHub availability and rate limits can delay a conclusive result; the proposal remains safely retryable.
- The frozen contract cannot be patched in place.
- The production SDK chunk is larger than 500 kB uncompressed; it is lazy-loaded and does not block the public first layer.

Further detail: [source policy](docs/SOURCE-POLICY.md) · [how it works](docs/HOW-IT-WORKS.md) · [contract source](contracts/accordlens.py).
