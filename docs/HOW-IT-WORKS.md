# How AccordLens works

1. A maintainer pins a change to a full 40-character Git commit and registers a bounded dependency graph.
2. Each source is fetched once from GitHub's Contents API at its exact commit and path, then its complete decoded bytes are checked against the declared size and Git blob identity before full parsing and evidence-closure construction.
3. GenLayer validators independently reconstruct the same source set and compare the consequential decision vector for every consumer.
4. Any missing, conflicting or over-limit evidence produces `UNRESOLVED` and leaves the proposal retryable. Only an agreed compatible result can become activatable.
5. Conditional results require the bound consumer wallet and independently verified remediation evidence. Failed or replayed remediation does not mutate authorization.

The UI distinguishes transaction submission, finality, execution result and authoritative contract readback. A wallet signature alone is never presented as a completed compatibility decision.

AccordLens runs on GenLayer Studio Devnet, chain ID `61997`. Public reads require no wallet. MetaMask, OKX Wallet and Rabby are discovered explicitly; each reload begins disconnected, and the selected provider is used only after the user chooses it.
