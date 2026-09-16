# Studio Dev verification matrix

The frozen AccordLens contract was exercised on GenLayer Studio Dev, chain ID `61997`. The matrix contains 45 unique transactions. Every transaction reached `FINALIZED` with `MAJORITY_AGREE`; `SUCCESS` and `ERROR` below are the expected semantic leader outcomes. Readbacks were taken from the contract after finality. Expected errors preserved the listed state and snapshot.

Contract: [`0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7`](https://explorer-studio-dev.genlayer.com/address/0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7)

Actors:

- **A** — `0x91E97c32289af6c135f025Ad9957F8b2830daeA1`
- **B** — `0x17375DbD58B93746C7fa7693F93c7Beb75364161`
- **C** — `0xA6c02a3d7D429629FaCd23A07b8A3d731628Ee99`

| Case | Method | Actor | Transaction | Execution | Authoritative readback |
|---|---|---|---|---|---|
| T02 | `create_change` | A | `0xa4c8c3c08fe73661f36905720845d67b76389681ecd89f03296c9026ba8b4f98` | SUCCESS | Proposal 0 · DRAFT · snapshot 1 |
| T03 | `register_dependency` | B | `0x4c5847248c173ec31d1158064c20a44a451a0ea006d083c1e0852ab5f4b2fbe8` | SUCCESS | Proposal 0 · DRAFT · snapshot 2 |
| T04 | `register_dependency` | C | `0x2237efaca24ee2950b385ad754a9a658016f9187ddb67029ef158010cda1e8e9` | SUCCESS | Proposal 0 · DRAFT · snapshot 3 |
| T05 | `register_dependency` | B | `0xfc7fce2f088b9cbf38f209ccf3964f6eeb18a961674fd3a11742403a3484eccb` | SUCCESS | Proposal 0 · DRAFT · snapshot 4 |
| T06 | `register_dependency` | C | `0x29d0df4a3fe23b1d72faca9fae1950cd5d2ecb64dfd682f9e7de1ccdb1be0875` | SUCCESS | Proposal 0 · DRAFT · snapshot 5 |
| T07 | `register_dependency` | B | `0xc19225619e3734135ed69ae567931c0433f879b0423fcde3394f39d4b34cece0` | SUCCESS | Proposal 0 · DRAFT · snapshot 6 |
| T08 | `register_dependency` | C | `0xe327bc7b8cbc915c19c3269b5e55bd62428a232bd604fc47f557a11c58a12a4c` | SUCCESS | Proposal 0 · DRAFT · snapshot 7 |
| T09 | `register_dependency` | B | `0x07f205271f34a553c011f857b72afb5045128a2f62d19aa07e861c714f2f7fc2` | SUCCESS | Proposal 0 · DRAFT · snapshot 8 |
| T10R1 | `register_dependency` | C | `0x4f79616d959144cbb5dbc5065e8eeef8186d23840da96e1cb2138ae5ef626c85` | SUCCESS | Proposal 0 · DRAFT · snapshot 9 |
| T11 | `lock_dependency_graph` | B | `0x8cc42c38473bc86162427814322db1fc4b4349366a100fcd7dee87c4b631828c` | ERROR | Unauthorized; DRAFT unchanged · snapshot 9 |
| T12 | `lock_dependency_graph` | A | `0x127730c3306c2e2cf6015a6d9e1fe3a73011bb9875a37db620e34ac72d0be964` | SUCCESS | Proposal 0 · LOCKED · snapshot 10 |
| T13 | `register_dependency` | C | `0x572b911006e54e319f5a65c8a0d116dcfdd4eea296d872b4f856d8323f0dc1ef` | ERROR | Post-lock write rejected; LOCKED · snapshot 10 |
| T14 | `evaluate_compatibility` | A | `0x644d239b3a029d0b903afd448f9d5ac7e779fb0e26d9a3c5300f7e9b05f74f1b` | SUCCESS | Proposal 0 · ACTIVATABLE / COMPATIBLE · snapshot 11 |
| T15 | `activate_change` | A | `0x0c1e47f1283805fe453c84d7fd56d16cf22bac453692e4807ffbce225ff694ce` | SUCCESS | Proposal 0 · ACTIVATED / COMPATIBLE · snapshot 12 |
| T16 | `activate_change` | A | `0x37d4476ea54acd9345466bf73b9f78006c3188bb08839d7ff81d5e3d6351b750` | ERROR | Replay rejected; ACTIVATED · snapshot 12 |
| T17 | `create_change` | A | `0x327ae470b6b37c2e8a849400655b61443d8420438a4a63421d5420e58fdadad5` | SUCCESS | Proposal 1 · DRAFT · snapshot 1 |
| T18 | `register_dependency` | B | `0x41d5e9242b165ae4b62820515f53df6e475ccbb45d6ebe7a52e8743454c83244` | SUCCESS | Proposal 1 · DRAFT · snapshot 2 |
| T19 | `lock_dependency_graph` | A | `0xcd374197b0a3a77f9b5b9eb4e16fcd9d0fb3406e4d91c4cf5b6fa80e675979c2` | SUCCESS | Proposal 1 · LOCKED · snapshot 3 |
| T20 | `evaluate_compatibility` | A | `0x3e8015d4a0921680c900313d1718e246d7ab01c4bba62bc1d5f20783e1ed724b` | SUCCESS | Proposal 1 · REMEDIATION / CONDITIONAL · snapshot 4 |
| T21 | `acknowledge_condition` | A | `0xc688be3bb037ce5fd874a719bfb4cd487ba93f23262ab20e48c424fdbeeffb74` | ERROR | Unauthorized; REMEDIATION · snapshot 4 |
| T22 | `acknowledge_condition` | B | `0x31ff26ee3b33c4c6ee59f2e38df33a8adb3fb0d35bb29769b652678861996512` | SUCCESS | Incomplete evidence; REMEDIATION · snapshot 5 |
| T23 | `acknowledge_condition` | B | `0x595d03993963a48e02a2730b1466b8e46d460f28f5f6993b41d20d5be73aae8c` | SUCCESS | Proposal 1 · ACTIVATABLE / CONDITIONAL · snapshot 6 |
| T24 | `acknowledge_condition` | B | `0xf07c8a8453ee99766fbd9bc1bdd1bc323c6e0f08f631994ac76c86752f323b74` | ERROR | Replay rejected; ACTIVATABLE · snapshot 6 |
| T25 | `activate_change` | A | `0xd89ae7dfa759fc84271612562853eea0e0edc68e280ac6817fb6305c236de494` | SUCCESS | Proposal 1 · ACTIVATED / CONDITIONAL · snapshot 7 |
| T26 | `create_change` | A | `0x7d63e3972bb9a4248f209790e6bff75e1221ea2ad118361d7e1c8222a7001892` | SUCCESS | Proposal 2 · DRAFT · snapshot 1 |
| T27 | `register_dependency` | B | `0x876de634fdd8e388485e5deaedabac6a11c2c5a6138f90d135869e2335eda3f6` | SUCCESS | Proposal 2 · DRAFT · snapshot 2 |
| T28 | `lock_dependency_graph` | A | `0x3ef19892d5786ccef702c4f99baf8911148ac1602e0824458b4ce0a88ba111d4` | SUCCESS | Proposal 2 · LOCKED · snapshot 3 |
| T29 | `evaluate_compatibility` | A | `0x0e5bd39265df24e4155d79fb98b3651dda1983c5d746f0a44656c57446f00e44` | SUCCESS | Proposal 2 · REJECTED / INCOMPATIBLE · snapshot 4 |
| T30 | `activate_change` | A | `0x32c979c4d58da47768e9e531c80334f3f57d1de5e25f2c4185b3428cffac0416` | ERROR | Wrong-state activation rejected; REJECTED · snapshot 4 |
| T31 | `create_change` | A | `0x6d02482a73cc0554b7bb3e282e1be1420d9ee0d7b58cb60a1fdf14615438838b` | SUCCESS | Proposal 3 · DRAFT · snapshot 1 |
| T32 | `register_dependency` | B | `0x9ea0ab16f99f55766aca7a79a5d9faebc490d477dbd97a98cf2143ddeb044b31` | SUCCESS | Proposal 3 · DRAFT · snapshot 2 |
| T33 | `lock_dependency_graph` | A | `0xbc92ed9b66367e0a45c669fcadc8081ca21a0cd4026b283227717693f1a038b6` | SUCCESS | Proposal 3 · LOCKED · snapshot 3 |
| T34 | `evaluate_compatibility` | A | `0x4e91e13f33b21aa067f8746fcc46709022ca169327ca06fe1f11b7c4fa61a31d` | SUCCESS | Proposal 3 · LOCKED / UNRESOLVED · snapshot 4 |
| T35 | `evaluate_compatibility` | B | `0xa88925dc64e1eb9a265e18acb9179e1d461b0fb55834bcdab757991fdefe7b26` | SUCCESS | Retry remains LOCKED / UNRESOLVED · snapshot 5 |
| T36 | `create_change` | A | `0x370af44a39e06972c90e67fda4674b764b30224755faaa9f766cc498701288da` | ERROR | Revision mismatch rejected; change count remains 4 |
| T37 | `create_change` | A | `0x67d8ca9509b1bf8f18bb5088e18501cb93a4346828811408bf97831212ebdd08` | SUCCESS | Proposal 4 · DRAFT · snapshot 1 |
| T38 | `create_change` | A | `0x52a19d4644e3e0075c56d57dc415ede64b2de7c0b92b17a8dbe76484a6a6db9e` | SUCCESS | Proposal 5 · DRAFT · snapshot 1 |
| T39 | `register_dependency` | B | `0x0b496d77bd420501ec0d28b501b8120f6264329d22b56945ab27f8390d795bf6` | SUCCESS | Proposal 5 · DRAFT · snapshot 2 |
| T40 | `lock_dependency_graph` | A | `0x77477a890a1bedc03398eb84d62f2f35b0a195991c963ff65f537949b30daaf1` | SUCCESS | Proposal 5 · LOCKED · snapshot 3 |
| T41 | `evaluate_compatibility` | A | `0x3799aa1bf41752ea68f9c55472d067f836912d73418e85d0f2f3c0ed360c936a` | SUCCESS | Proposal 5 · REJECTED / INCOMPATIBLE · snapshot 4 |
| T42 | `create_change` | A | `0x25c356d39e32b8e957baa65379581ce714c66eefc10e2e6e61c9237ab26d00b3` | SUCCESS | Proposal 6 · DRAFT · snapshot 1 |
| T43 | `register_dependency` | B | `0xf3b35d5d1a62342dd739edbd904fa3c380feb560e305fe61d7511d982757a174` | SUCCESS | Proposal 6 · DRAFT · snapshot 2 |
| T44 | `lock_dependency_graph` | A | `0xc966562dcd7701c85555be114b3de2b8fccc9c196038ce87721a56dbbd153e31` | SUCCESS | Proposal 6 · LOCKED · snapshot 3 |
| T45 | `evaluate_compatibility` | A | `0xa9b82149b216882d8a26517006991be91b9f30e25486760545de19753a3b4552` | SUCCESS | Proposal 6 · LOCKED / UNRESOLVED · snapshot 4 |
| T46 | `expire_change` | B | `0x0a8bc81a406a904248c4ef2871dc82aaf263a7a889bca596ea78029314be33cd` | SUCCESS | Proposal 4 · EXPIRED · snapshot 2 |

## Bounded read checks

After the writes, `get_counts` returned `change_count = 7`. Event pagination for proposal 0 returned `total = 12`, `limit = 2`, and advancing offsets `0 → 2 → 4`. Dependency pagination returned `total = 8`, `limit = 3`, and advancing offsets `0 → 3 → 6`. These read-only checks require no transaction hash.

The detailed source fixtures, byte identities and operation arguments are published in [`fixtures/studio/fixture-manifest.json`](../fixtures/studio/fixture-manifest.json).
