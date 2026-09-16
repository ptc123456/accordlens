# Live Vercel E2E

AccordLens was tested from the public production application against the frozen Studio Dev contract.

## Release identity

- Public application: `https://accordlens.vercel.app`
- E2E-tested deployment: `dpl_C56ZYEUeeyp93P7JrkbWVGDSwvqq`
- E2E-tested deployment URL: `https://accordlens-64qcm0ws6-shingg.vercel.app`
- Current production deployment: `dpl_6qsBEmRvFgT61z7CfWxfuZ1vYcQ1`
- Current production URL: `https://accordlens-f88gu30et-shingg.vercel.app`
- Public source snapshot: `5d85cda60bbf8184d68f406d061e1caa4f329166`
- Source tree: `e2ed9716af24c9cb43088e02f5d1fa0b2a8eb723`
- Live bundle: `/assets/index-BIbCgchR.js`
- Live/local bundle SHA-256: `B8EF0D287EAAF50B1F801197CEB07EB9D06369C2A0F4BD517491A6824F28FDF6`
- Contract: `0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7`
- Network: GenLayer Studio Dev, chain ID `61997`

## User journey

The journey started disconnected, selected the injected OKX Wallet provider, and signed each write from `0x896Ef52d620eA3CCdA34B4E72a8E197974e4e39E`. The application never replayed a write while waiting for finality or after reload.

| Step | Transaction | Verified result |
|---|---|---|
| Create proposal 7 | `0xe17ca4304428fa6c2c623c0898d7c0ede4fb80455c9c0940faaac4ed3f70deb7` | `DRAFT` authoritative readback |
| Register `judge-okx` | `0x4ef8b7649da3521fa8f306f39d130609cbd5a638553de903a02a88ba4e554f69` | Consumer and immutable constraint recorded |
| Lock dependency graph | `0xb18ccef654d943926db40961b0704a3bbf3afedac8da60e8f6c328547c6513a1` | `LOCKED`; graph digest `68d701765e2f831e24d296a37911576433ba2f327a257b1351464e89a2406fbe` |
| Evaluate compatibility | `0x57786b10d43432a4e95f500e41bc334020458fb4487e72d64a6ef691d26f717b` | `ACTIVATABLE / COMPATIBLE`; one attempt |
| Activate proposal | `0x45c21a5d1c66df69412a44d15b2414705c0f4d9091f4c3ea2959e476099fa99f` | `ACTIVATED / COMPATIBLE`; snapshot 5; event count 5 |

Every transaction above finalized with semantic execution success and consensus acceptance before its authoritative contract readback was accepted. The evaluation remained tied to revision `be4f0812c0b8b163270206f9aa37ecdaec614f55` and the immutable compatible fixture.

## Browser acceptance

- Reload returned the application to disconnected state.
- Proposal 7 remained publicly readable after reload and returned `ACTIVATED / COMPATIBLE` without reconnecting a wallet.
- Pending-hash recovery displayed the retained hash and reconciled it automatically without a duplicate submission control.
- `/`, `/council`, and `/how-it-works` loaded from the public alias with coherent navigation and only the current contract identity.
- The wallet chooser used the selected EIP-6963 OKX provider; application writes came from the independent wallet account, not the Studio deployer.
- Production returned HTTP `200`; the deployment was independently reported `READY` by Vercel.
- The current production deployment serves the same `/assets/index-BIbCgchR.js` bundle; both the E2E-tested and current public bundles have SHA-256 `B8EF0D287EAAF50B1F801197CEB07EB9D06369C2A0F4BD517491A6824F28FDF6`.

## Fresh release checks

- Frontend tests: `38/38` passed.
- TypeScript: passed.
- Production build: passed.
- Production dependency audit: zero vulnerabilities.
- `py -3.13 -m pytest tests -q -p no:cacheprovider`: `74` passed and four disclosed Windows Direct Mode loader failures. The four failures are excluded from the passing count and covered by the complete live Studio matrix for the current contract.
- `py -3.13 -m pytest probes -q -p no:cacheprovider`: `33` passed.
- Python dependency check: no broken requirements.
