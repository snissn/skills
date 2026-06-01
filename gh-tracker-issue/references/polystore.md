# Polynomialstore/polystore Tracker Extension

Use this extension when the target repository is `Polynomialstore/polystore`.

## Repo Policy

Read `AGENTS.md` before drafting. Current PolyStore policy requires:

- no direct pushes to `main`;
- work lands on topic branches;
- push with `git push origin <branch>`;
- open or update a PR for review;
- agents must not self-merge;
- human approval is required before merge;
- run relevant local tests before pushing non-trivial changes.

Every implementation tracker and child issue that expects code changes should include these constraints.

## Workstream Fit

For browser/WASM KZG optimization work, separate:

- no-local-helper browser path optimization;
- benchmark/report harness work;
- Rust/WASM implementation changes;
- web worker scheduling and upload-pipeline changes;
- speculative research spikes such as SIMD backend changes or WebGPU.

Do not include native/local-helper acceleration as an optimization path unless the user explicitly broadens scope.

## Benchmark Requirements

For browser/WASM KZG upload work, require before/after evidence with:

- baseline branch/commit and candidate branch/commit;
- exact command and script;
- runtime/browser engine or Node/V8 version;
- hardware, core count, memory, and OS when known;
- file size and MDU count;
- RS profile and commitment count;
- worker count and scheduling mode;
- total prepare wall time;
- user-stage wall time;
- per-blob KZG commitment time;
- per-MDU KZG commitment time;
- witness/meta/manifest stage timing when relevant;
- memory footprint or allocation/GC observations where available;
- correctness verification against existing commitment/proof tests.

Treat material regressions in wall time, per-blob commit time, memory footprint, correctness, or browser responsiveness as blocking until optimized away or explicitly accepted by the coordinator/user.

## Labels

Run `gh label list --repo Polynomialstore/polystore` before creating issues.

Prefer existing labels. If the user explicitly authorizes label management, create missing labels needed by the workstream before creating or updating issues.

Reasonable PolyStore tracker labels include:

- `enhancement`
- `performance`
- `tracking`
- `wasm`
- `frontend`
- `research`

Suggested label meanings:

- `performance`: benchmarked runtime, throughput, memory, latency, or responsiveness work.
- `tracking`: umbrella or coordination issues for multi-PR workstreams.
- `wasm`: Rust/WASM, browser runtime, or WASM build/toolchain work.
- `frontend`: website, worker, browser upload, or client-side UX work.
- `research`: bounded feasibility spikes or protocol/math investigations that may close without implementation.
