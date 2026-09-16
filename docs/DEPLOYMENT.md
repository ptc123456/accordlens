# Deployment

AccordLens is deployed on GenLayer Studio Devnet, chain ID `61997`.

- Contract: `0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7`
- Deployment transaction: `0xc13aaf59455cf92fb15b0b218793df174fb7a67131c3433c449b0a2f56784902`
- Deployer: `0x91E97c32289af6c135f025ad9957f8b2830daea1`
- Public source snapshot: `5d85cda60bbf8184d68f406d061e1caa4f329166`
- Source SHA-256: `cc7f5310024e23ed20174a233364f62ed78113997587aa4a272e0ac2bd097c45`
- Source size: `47,300` bytes, LF line endings
- Runtime: GenVM Manager `v0.6.0-rc5`; `py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng`

The deployment finalized with `MAJORITY_AGREE`, leader execution `SUCCESS`, and byte-identical deployed code. The contract is intentionally frozen: any source defect requires a new deployment and complete replacement evidence.

## Public application

- URL: `https://accordlens.vercel.app`
- Public source snapshot: `5d85cda60bbf8184d68f406d061e1caa4f329166`
- Current production deployment: `dpl_6qsBEmRvFgT61z7CfWxfuZ1vYcQ1`
- Current immutable deployment URL: `https://accordlens-f88gu30et-shingg.vercel.app`
- Status: `READY`
- Runtime bundle: `/assets/index-BIbCgchR.js`
- Bundle SHA-256: `B8EF0D287EAAF50B1F801197CEB07EB9D06369C2A0F4BD517491A6824F28FDF6`

The stable URL is the public judge-facing entry point. The immutable deployment URL identifies the current production deployment and may be subject to the owner's Vercel access policy. The wallet E2E was executed on deployment `dpl_C56ZYEUeeyp93P7JrkbWVGDSwvqq`; its application bundle is byte-identical to the current deployment, as recorded in [VERCEL-E2E.md](VERCEL-E2E.md).
