---
name: codex-issue-graph-executor
description: "Execute GitHub issue graphs toward agreed outcomes with accepted decisions, ticket revisions, artifacts, and merged PRs. Use GPT-6.2 Sol-only delegation by default, provisional dependent work, conservative concurrency, and current-head PR gates. Use for graph execution, not requests to review or edit this skill."
---

# Codex Issue Graph Executor

Use this skill when the user asks Codex to execute a dependency graph of GitHub
issues, tickets, or PRs and drive them to completion. This is the Codex-native
counterpart to Orca graph execution: do not use Orca or Pi commands. Use Codex
subagent tools for bounded work that benefits from delegation, with this rollout
remaining the graph coordinator and owner of merge-authority allocation.

For a graph execution request, invocation means `execute-and-merge`: inspect live state,
delegate safe independent work, deliver and verify each node's intended output,
drive PRs through readiness gates, and merge in topological order after gates pass.
A plan, report, or ticket revision completes a node only when it is that node's
accepted deliverable; it does not complete an unmet parent product outcome. Do not
stop at an opened PR or ordinary pending CI/review. Follow **Critical-Path Finalization
and Monitoring** below; keep monitoring until the gate resolves.
Do not ask for separate merge approval unless the user
explicitly narrowed the request to planning or no-merge execution.

## GPT-6.2 Sol Execution Guidance

Execution routing was upgraded to `gpt-6.2-sol` on 2026-11-17 after the local
Codex catalog confirmed availability and supported efforts. The workflow guidance
below was originally checked against [GPT-6.1 Sol guidance](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
and [Codex subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents)
on 2026-10-01; it is not a claim that 6.2 API details were independently reverified.
Use the runtime catalog for current compatibility and the routing below:

- Resolve routine choices and finish authorized work. Clarify only consequential
  unknowns; keep independent work moving. Preserve prior authorization.
- User direction overrides skill defaults. If a rule blocks progress, cite its
  exact file and wording; distinguish a requirement from your interpretation.
- Treat new messages as steering; propagate corrections to affected workers.
  Answer status questions briefly and resume unless the user cancels the task.
- Delegate a bounded task when useful coordinator work can proceed alongside it.
  Otherwise work locally. The budget below governs every reference/template.
- Keep delegation prompts as small routers: provide the outcome, boundaries,
  evidence, and stop conditions; load only the references needed for that role.
- Run required and risk-relevant checks. After they pass, repeat or broaden them
  only for changed code, failures, or unresolved risks. Avoid redundant tests.
- Keep updates and handoffs concise, readable, and evidence-linked. On resume,
  recover scope, authorization, heads, completed checks, and next actions from
  durable state, then refresh live facts that may have changed.

## Default Authorization

- Merge authorization is granted by default for PRs in the selected graph.
- Always start dependent nodes provisionally as soon as their predecessors have
  usable recorded contract snapshots and decision dependencies/conditional
  eligibility are satisfied. Do not wait for predecessor PR CI, review,
  or merge, and do not ask the user to opt into work-ahead. Respect the execution
  budget and actual repository restrictions; record concrete blockers rather
  than asking the user to choose this default again.
- Authorization is scoped to the target repo, parent tracker, child issues, and
  PRs created or explicitly adopted during this execution.
- **Proactive asynchronous flake repair is authorized by default within the same
  repository:** whenever CI exposes an unrelated flaky test or noisy CI gate
  with no active repair PR/owner, the coordinator is authorized to adopt or open
  one focused flake-repair issue, dispatch an asynchronous background worker in
  an isolated worktree off `origin/main`, open a focused maintenance PR, and
  drive it through normal review, CI, and authorized merge gates without asking
  for separate permission or blocking the primary product PR.
- The coordinator may revise the remaining graph and create or explicitly
  adopt necessary nodes within that scope as evidence changes. Map them to the
  agreed parent outcome and preserve acceptance criteria, guardrails, ownership,
  and history; necessary issue maintenance needs no repeated permission.
- Execution includes reclaiming released local worktrees, verified disposable
  outputs, and graph-owned Go build caches for the selected repository under
  **Asynchronous Disk Cleanup**. Complete eligible cleanup on the execution host.
  Editing this skill does not itself authorize a disk cleanup run.
- The coordinator may merge after all gates pass; workers may not merge unless
  the coordinator explicitly delegates that action for a specific PR.
- Do not merge unrelated non-flake PRs outside the selected graph, even if they are nearby.
- Do not merge if repo policy or branch protection requires missing human
  approval.
- Do not merge with stale, missing, red, or inconclusive latest-head CI unless
  repo policy has no CI requirement and the coordinator records the rationale.
- Do not merge with unresolved requested changes, material review findings,
  missing required tests/benchmarks, or unaccepted material performance
  regressions.
- If a hard blocker prevents completion, update durable graph state with the
  blocker, owner, and next action before reporting.

## Node Deliverable Contract

Use the planner's completion-packet rules. Record each node's primary deliverable
(`pr`, `issue-update`, `decision`, or `artifact`), target location, acceptance
criteria/evidence, and acceptance owner. Supporting outputs belong in the same
packet; a report stored through a PR still follows that PR's gates. Do not create
a PR solely to represent completion of an accepted non-code output.

For an inquiry, preserve the question/hypothesis, discriminating evidence, conclusion
(including negative or inconclusive findings), and resulting plan changes. For an
issue update, verify the actual live revision, ownership/edges, preserved acceptance,
and remaining obligations. The coordinator accepts the output and records its link,
version/source binding, evidence, and next action before setting `completed`.
Negative findings can complete an inquiry but cannot pass a product improvement gate.
Code, harness, and documentation changes still follow applicable repository PR policy;
non-PR completion never substitutes for required review, CI, or scientific authority.

Build out the next consequential inquiry and justified implementation, then revise
the unexecuted graph at the planner's decision boundaries. Retain useful findings,
retire disproven mechanisms, and select successors from evidence. Keep primary and
secondary objectives distinct from guardrails; a measurement budget or resource cap
is not proof of optimization. Parent completion requires its agreed outcome gates,
not merely accepted child outputs or linked follow-ups.

## Bug Reproduction And RED/GREEN Evidence

For a bug repair, distinguish retained error evidence, a runnable recipe and an
actually observed baseline RED. Before a production repair, verify the recipe
against the selected source/public entry/backend/profile; run and preserve RED on
the unfixed source with exact build/configuration, assertions, errors and cleanup
evidence. Source inspection, an old log or an unexecuted test is not RED. If the
trigger is uncertain, execute the issue's bounded reproduction/diagnosis gate
first, record inconclusive outcomes, and leave patch mechanics undecided until
causal evidence supports them. Do not fabricate RED by injecting an unrelated
failure or weakening checks.

Demonstrate GREEN on the identical intended public path, workload and assertions;
a legacy fixture is not COW proof. Storage repairs include acknowledged-value
read-back, checkpoint, checked close, fresh reopen/profile-appropriate recovery
and error propagation, with actual backend activation. Preserve all original
failures and meaningful assertions. Keep reproduction, fix and coverage in one
integrated change instead of separate proof-only delivery cycles. When the user
requires a coordinator/ROOT graph or skill readiness review before implementation,
keep implementation pending until that actual review is recorded; ticket clarity
review or publication is not a substitute or new execution authority.

Assert the public boundary's actual error representation separately from internal
causal errors. Retry grouped mutations only with proof of no prior publication;
exercise prepublication fallback and ambiguous/postpublication no-retry outcomes.
Observe the original Close/Flush return at its producer, propagate errors and
validate an injected close failure even when operation totals pass; a shadow
flush cannot recover a discarded return. Keep random-workload persistence checks
distinct from deterministic exact-value fixtures with retained expected state.

When performance is the primary outcome, apply the sequencing in the planner's
[performance-sensitive feature contract](../gh-issue-planner/SKILL.md#performance-sensitive-feature-contract).
For optimizations, carry its public-entry red/green regression or justified exception,
activation proof, and relevant eligibility cases into the assigned completion packet.
Carry that order into implementation and finalization assignments: focused changed-seam
checks before bounded public-path comparisons and short profiles, then exhaustive
qualification after a stable, viable performance candidate exists. Preserve required
per-PR merge gates and final graph qualification; diagnostic runs are not retained
qualification evidence.

## Simplification Within The Completion Packet

At implementation start, inspect the affected existing code and verify any planner
simplification findings against the assigned source snapshot. Look for reuse,
duplicate logic, redundant layers, obsolete branches/options, and avoidable custom
machinery. If planning omitted this audit, do it locally within the node's scope;
do not wait for a separate planning pass or ponytail invocation.

Choose the simplest maintainable implementation that meets the full completion
packet. Consolidate shared logic and remove verified unnecessary code in the same
PR when it directly helps the change and fits the ownership boundary. Judge the
resulting code's responsibilities and maintenance burden, not just added lines or
diff size. A necessary abstraction or larger coherent refactor can be the simpler
solution. Do not replace the agreed outcome with a reduced feature or stop at a
partial fix in the name of minimalism.

Before calling the candidate mature, inspect the diff together with its affected
callers for duplication or layers the change adds or leaves unnecessary. Preserve
applicable behavior, validation, error handling, ownership/lifetime, concurrency,
durability, and performance gates. Use existing characterization evidence when it
adequately protects a refactor; add or run checks for actual changed risks under
the node's test policy. Simplification does not impose a one-test ceiling or a
new review/benchmark cycle when existing evidence still applies.

Record consequential simplifications or reasons to retain complexity briefly in
the normal PR evidence/handoff. Finding no useful simplification is acceptable;
do not invent cleanup to satisfy this pass. Route discoveries that materially
change scope, contracts, or ownership through Graph Reassessment; keep unrelated cleanup off
the critical path. Carry this policy into implementation and finalization prompts;
it needs no separate audit node, agent, report, or ponytail dependency.
When composing simplification helpers such as ponytail, the full completion
packet governs scope, validation, and reporting.

## Outcome And Algorithm Checkpoints

For uncertain, architectural, or performance work, name the next public-path
proof or decision that advances the parent outcome before assigning more code.
For an uncertain optimization, carry the observed cost, causal hypothesis, smallest
intervention, discriminator, and failure action into the assignment. Select the
cheapest inquiry that can change the decision; reuse existing source/profile evidence
and maintained primitives before speculative implementation. Apply the
[efficient experiment loop](../go-performance-optimization/references/efficient-experiments.md)
for performance work: prove natural activation, check focused safety and ordinary
costs, then obtain an early public result before broad qualification. Zero activation
or adverse ordinary-path cost stops promotion until its cause is resolved. Once a
candidate has worthwhile public benefit, prioritize its remaining gates and delivery
over opening another optimization branch.

Use the tracker's evidence boundaries alongside a backstop: reassess after two
coherent implementation/repair batches without that advance, or about 45 minutes
of active work without a strategic checkpoint, whichever comes first. A different
task-specific backstop needs a recorded rationale; a distant milestone alone does
not replace it. This is a short coordinator decision in existing state, not a
requirement for another report, review agent, or test campaign; existing adviser
triggers still apply. Concrete work with a known solution remains event-driven.

Passing helper tests, new commits, more precise accounting, and a growing check
suite are supporting evidence, not substitutes for the named outcome. Count local
repair attempts too; changing file, branch, failure wording, or session does not
reset a recurring blocker. User concern about churn triggers reassessment now.

Apply [Graph Reassessment](references/dependency-execution.md#graph-reassessment)
before another affected batch. Compare continuing, simplifying the existing seam,
and a materially different algorithm/representation/integration order. Choose one
bounded next proof and record continue, simplify, replace, split, or defer with
evidence and preserved obligations. Sunk implementation cost is not a reason to
keep an unsuitable approach. Do not weaken correctness or performance gates.

Bound provisional work by that proof. Reopen `dependency-ready` when new evidence
changes its contract; stop speculative helper expansion until the common path is
proven. Coordinator unavailability permits finishing the already assigned bounded
batch and preserving it, not an unlimited sequence of new shared-contract changes.
Independent authorized work can continue. Reassessment steers continued execution;
it is not completion of the unmet parent goal or a reason for repeated permission.

## Productive Work While Experiments Run

When a benchmark, profile, build, or CI check is pending, proactively advance the
highest-value independent in-scope question instead of only polling. Reuse existing
evidence to form the next hypothesis, inspect its source route, build a small
isolated prototype, and run a cheap discriminator on noncompeting resources. Use
[productive experiment waits](../go-performance-optimization/references/efficient-experiments.md#use-experiment-waits-productively)
to choose overlap and protect the running candidate. Do this locally when delegation
is unavailable; otherwise reuse permitted workers within the existing budget.
Keep one measurement owner per host and do not consume its CPU, memory, disk, or
network with competing tests/builds. Queue those runs or use independent resources.
Collect the pending result promptly, revise the ranking, and return to its next
critical action. If no safe useful overlap exists, wait and state that constraint
briefly; do not create work or expand scope just to occupy capacity.

## Orthogonal Performance Workstreams

For a measured material performance/allocation gap beside a correctness blocker,
apply the planner's [orthogonal workstream policy](../gh-issue-planner/SKILL.md#orthogonal-performance-workstreams).
Revise or adopt profile-ranked implementation packets with explicit owners and a
path-and-contract conflict map; separate shared contract decisions from independent
construction. Start justified independent optimization and eligible follow-ups
provisionally from a pinned canonical source and usable contract while the unrelated
repair proceeds. Source integration order and runtime grants must not become global
construction barriers. Keep one integration owner for the shared candidate and
reconcile changed contracts before affected integration.

Use early public-path A/B throughput, `B/op`, and `allocs/op` to redirect allocation
work; apply the Go skill's reuse/lifetime rules and reconsider structure when the
measured ceiling is inadequate. Measurement isolation has its own resource gate.
The benchmark host remains under the measurement owner's custody until timed work,
profiling, and host-side artifact reads or transfers have all stopped. A CPU-only
quiet check does not establish disk or network isolation. Do not start the next
measurement while a previous lane is copying artifacts from that host; record and
disposition any overlap against the original isolation contract.
When the user explicitly revises an impractical measurement qualification rule,
implement the authorized general rule and continue execution. Preserve the old
result under its original criteria, document the new criteria and their limits,
and obtain the applicable new-head CI and comparable evidence; do not treat the
superseded rule as an immutable blocker or relabel an old failure as a pass.
Known unsafe execution stays blocked; provisional construction does not certify a
broken workload or waive applicable correctness, merge, or final qualification
gates. Fan out only justified work within the user's concurrency/resource budget;
do not substitute report-only machinery for the implementation outcome.

## Integrated Product Feedback

When shared layers and their production callers repeatedly change together,
consolidate them onto one canonical integration candidate with one integration
owner. Keep issue ownership and acceptance criteria, but do not turn every layer,
helper extraction or contract freeze into a separate delivery barrier. A coherent
PR may satisfy several coupled issues; split by independently useful public
behavior and stable boundaries when that improves delivery and review.

Fork successors from the nearest selected canonical contract. Before an expensive
public proof, compare their ancestry and production diff with that candidate for
inherited experiments, unselected retirements, or stale shared APIs. If present,
project the selected feature patches into the canonical candidate as one coherent
batch, preserving its current behavior and ownership contracts. Qualify that
result directly; do not first certify an obsolete branch or merge unrelated
experimental ancestry. This is source preflight, not another delivery gate.

When a mechanism is stopped or deselected, identify and remove its production
delta and coupled fixture/docs assumptions from the selected candidate before
further promotion, preserving independent accepted fixes. Retain any part only
when explicitly selected for an independent requirement; record that selection
in the existing checkpoint.

Start developmental integration checks while implementation is underway, using
the intended public capability matrix and existing lifecycle tests. Final retained
qualification still needs its declared landed authority. Do not postpone all
engine-level feedback until a final Q node, or require exhaustive helper accounting
before a safe, reversible public-path development check. Known execution hazards
must be addressed; incomplete acceptance obligations remain explicit and open.

Changes to default dispatch, profiles or shared ownership need early feedback
from the whole owning package and affected public compatibility paths, beyond
named new-feature controls. After repairing a panic or other first failure that
hid the tail, finish that package before another repair push. Group failures by
their common production or fixture cause and fix them as one coherent batch;
avoid discovering the same migration one CI shard at a time. Reuse unchanged
evidence; this does not require running the entire repository after every edit.

Before broad structural work or the first public probe, reuse maintained fixtures
and codecs and trace the actual factory, resolved profile, write placement/backing
paths, returned representation, codec/version dispatch, registration/eligibility,
durability boundary, and terminal Close/reopen cleanup against source. Include
this preflight in the implementation batch; apply the Go skill's workload-to-seam
and affected fraction check for performance work. Helper names do not prove these
contracts. It requires no separate review gate or helper-test campaign.

Composition must carry each feature's maintained registration and naming inventories,
not only generated CI digests. Order independent public capability checks before
auxiliary inventories, or isolate their invocations, so bookkeeping drift cannot
hide the product tail. All required inventories must still pass before delivery.

An authorized bounded verification batch includes routine compiler and fixture
corrections that preserve the original contract and assertions. Workers may freeze
the correction and continue within the assigned runtime budget without another
coordinator permission handoff. Preserve each failed attempt and distinguish setup
failure from an exercised product failure. Check maintained signatures and input
shapes before lengthy fixture review; use the first focused run to reach the
public boundary promptly. Production contract changes and repeated nonadvancing
batches still trigger review and reassessment; this is not a blind-retry allowance.

At an outcome checkpoint, compare public capabilities delivered and qualified,
unlanded coupled changes, and the next missing product behavior. If local green
checks keep growing without that behavior, change the integration boundary or
assignment before adding another supporting proof campaign. Record this in the
existing tracker state; no additional audit artifact or reviewer is required.

Keep the current candidate, results, failures and next proof in one rolling tracker
checkpoint when the repository workflow permits. Link stable parent and qualification
bodies to it instead of copying status after each control. Update it for changed
source, contracts, decisions, or next consequential actions; batch routine status
maintenance. Reuse applicable evidence and unchanged artifact producers: fix a faulty
checker/decoder and replay the original artifact rather than rerunning its producer.
Preserve source-bound history and acceptance criteria.

For suspected recurring CI flakes or noisy CI gates, apply the merge skill's
[bounded repair and parallel progress policy](../github-pr-mergeable/references/recurring-ci-flakes.md).
Capture the failing run/job/attempt and failure log excerpt *before* any
`gh run rerun --failed`, search the exact test's historical issues and merged
fixes, and **proactively dispatch one asynchronous flake-repair worker** in an
isolated worktree off `origin/main` (using the **Async CI Flake-Repair Worker**
template in `references/worker-prompts.md`) instead of sitting idle waiting to
rerun failed jobs. Initiate or adopt the `gh-issue-planner` →
`codex-issue-graph-executor` → `github-pr-mergeable` completion loop within the
existing coordinator; do not stop at filing a ticket. Continue independent engine
work and eligible merges. Make the repair a dependency only where an actual
shared-code or required gate relationship needs it, and preserve the failed
evidence and normal final gates.

## Compose With

- [Go Performance Optimization](../go-performance-optimization/SKILL.md) when Go
  runtime performance is material, for public-path activation, comparable measurements,
  profiling diagnosis, ownership/lifetime checks, and scoped evidence reuse. For
  material allocation work, require its maintained-arena/pool/buffer reuse decision
  and lifetime/retention evidence in the completion packet.
- `github-pr-mergeable` for PR readiness, review, latest-head CI, and merge execution. Use its bundled `scripts/codex_review_gate.py` for Codex state; never infer Codex completion from formal reviews alone. Repository-local proportionality and review-stop rules override that skill's default Codex cadence.
- `github:gh-fix-ci` when GitHub Actions failures need targeted diagnosis.
- `github:gh-address-comments` when unresolved PR review threads must be
  inspected and fixed.
- `scientific-portfolio-governance` for scientific lanes: owner direction or a
  clear issue assignment, one writer per issue branch, and overlap checks. No
  scheduler, slot pool, activation PR, or workflow-authored scientific/governance
  authority. One scientific decision per PR; unrelated main changes do not
  invalidate a lane. Scientific successors need merged predecessor authority
  and their own owner direction or assignment; merging does not activate them.
- `gh-issue-planner` when a graph needs a durable parent tracker, issue body
  updates, or revision during execution. Carry existing execution authorization
  into its apply mode; preserve narrower user restrictions.

When composing helper skills, apply this skill's post-push evidence discretion
instead of a blanket fresh-evidence reset. Required repository and branch
protection gates still apply.

At startup, verify which helper skills/tools are available and record any
fallback in the graph state. Missing helper skills do not stop execution unless
their absence makes a required gate impossible to verify.

## Retained Evidence Nodes

- Apply the canonical Retained Evidence Velocity policy linked from `github-pr-mergeable`.
- Where dependency policy permits, model `product -> reviewed/landed harness or schema -> artifact-only evidence`. Focused pre-review MUST cover provenance, concurrency/isolation, fail-closed validation, and wording; freeze exact runtime and harness subtree/blob identities before expensive collection.
- Prefer a dedicated high-capacity runner with persistent build cache and durable artifact storage. Otherwise record `INFRASTRUCTURE_UNAVAILABLE: <runner|cache|storage>: <reason>` and the actual fallback; never invent infrastructure.
- Classify candidate failures separately from proven unrelated CI flakes, rerun only affected gates, and require current-head merge gates. Artifact-only descendants preserve evidence only under exact runtime/harness subtree and implementation-blob identity; product or harness drift invalidates affected evidence.

## Storage And Build Cache Defaults

Before allocating a lane, resolve the repository's existing Git common directory
and reusable host cache paths; record them in existing graph notes and handoffs.
Prefer registered `git worktree add` checkouts from that repository at the pinned
source snapshot. Reuse an assigned lane across its fix loop; create a separate
clone only when independent repository state is required or no suitable local
repository exists. Worktrees share Git objects, but still materialize working
files and generated outputs.

Inspect `go env GOCACHE GOMODCACHE GOCACHEPROG`. Honor cache settings supplied
in the environment or `GOENV`, external cache programs, and benchmark cache
contracts. Reuse the shared `GOMODCACHE` within the same user/trust boundary.

Go's `DiskCache` is concurrency-safe across parallel `go build`/`go vet`/`go test`
invocations (`*-d` outputs are content-addressed with hash/size checks and `*-a`
entries are written idempotently), **but** its built-in trim uses a 5-day idle
TTL with **no byte cap** — so `-race` archives (`100–350 MB` each), cross-OS
builds, and ad-hoc per-worker caches can silently consume `20–50+ GiB` within
hours. Therefore, for ordinary local and remote-host Go builds where the
executor chooses the build cache:

- **Use ONE persistent host-level shared `GOCACHE` per `(execution host, user)`**
  rather than allocating ephemeral per-graph or per-worker `/tmp/*-gocache`
  directories that start 100% cold and multiply disk usage:
  - macOS default: `$HOME/Library/Caches/agent-go-build` (or the user's default
    `$HOME/Library/Caches/go-build` if the user explicitly opts into sharing
    their personal cache).
  - Linux / remote-host default: preferred verified high-capacity mount when
    available (for example `/mnt/fast4tb/.cache/agent-go-build`), otherwise
    `${XDG_CACHE_HOME:-$HOME/.cache}/agent-go-build`.
  - Record the resolved absolute `GOCACHE`, `GOMODCACHE`, and toolchain in graph
    state and pass them explicitly to every worker and remote-host command. Never
    let workers invent ad-hoc `/tmp/*-gocache` directories.
- **Pass `-trimpath` explicitly across worktrees** on every `go build`, `go vet`,
  and compile-only cross-OS check (for example `go vet -trimpath <pkgs>` and
  `CGO_ENABLED=0 GOOS=windows go test -trimpath -vet=off -exec=true -run=^$ ...`),
  and on `go test` / `go test -race` whenever tests are `-trimpath`-safe. Without
  `-trimpath`, Go embeds each worktree's absolute path into compiled `.a`
  archives and drops cross-worktree cache hits on module-local packages to 0%;
  with `-trimpath`, unchanged local packages hit 100% across worktrees. Pass
  `-trimpath` as an explicit CLI flag rather than exporting global `GOFLAGS`
  when repository benchmark or receipt harnesses assert `GOFLAGS=""`. Keep
  `GOROOT`, `GOTOOLCHAIN=local`, `CGO_ENABLED`, and `-trimpath` uniform across
  worktrees so action IDs match.
- **Keep `TMPDIR` and `GOTMPDIR` strictly lane-local** (always export **both**)
  along with DBs, mutable datasets, binaries, and benchmark output in a
  **per-lane scratch root** separate from the shared `GOCACHE`, and delete each
  lane's scratch root together with its worktree as soon as the lane releases.
- **Bound local compile concurrency on laptop-class hosts** (`<= 8` CPUs or
  `<= 16 GiB` RAM): when `>= 2` local worktrees are active, pass `-p=2` or
  `-p=3` on heavy `go test`/`go vet`/`go build` commands (`-p` does not alter
  `GOCACHE` keys), avoid running multiple parallel `go test -race` commands in
  one worker, and keep pre-push `go vet` scoped to affected packages.
- **Enforce a live-safe byte cap with `scripts/gocache_prune.py` (never live
  `go clean -cache`):** at coordinator startup, wave/sprint boundaries, and lane
  closeout, run:
  `python3 <SKILLS_ROOT>/codex-issue-graph-executor/scripts/gocache_prune.py --cache-dir "<SHARED_GOCACHE>" --max-gb 10 --target-gb 6 --min-age-seconds 7200`
  (use `--max-gb 8 --target-gb 5` on laptops with `< 50 GiB` free; `--max-gb 20
  --target-gb 12` on high-capacity hosts such as `/mnt/fast4tb`). Because Go's
  `DiskCache` bumps `mtime` on cache hits (`1h` interval) and treats missing
  entries as benign misses, pruning entries `>= 2h` old oldest-first is safe even
  while concurrent builds run and keeps hot stdlib/`-race`/dependency caches warm
  while shedding superseded `300 MB` `-race` `.a` archives. Use `go test -count=1`
  when fresh test execution is required without invalidating compiled packages.
  Reserve isolated temporary caches strictly for explicit cold-cache or
  dependency-acquisition checks (record reason, exact paths, and disposal owner),
  and force `-a` on affected packages if external C libraries change under CGO.

For required file copies, prefer verified same-filesystem copy-on-write support
(APFS cloning on macOS or reflinks on a supporting Linux filesystem). Record an
unsupported fallback as a full copy; do not assume savings from the OS name or
`--reflink=auto`. Directory copies or hardlinked writable files do not replace
registered Git worktrees. Partial clones such as `--filter=blob:none` are optional
for new repositories when on-demand history access is acceptable; they do not
reduce materialized checkout files or build output.

## Checkpoint And Evidence Pushes

Before pushing a durable checkpoint or evidence packet, refresh live open-PR head
repository/branch mappings for the destination and relevant upstream repositories,
including fork, draft, and stacked PRs. Classify the actual diff and destination;
an evidence-only commit on an open PR's head
still advances that PR. If PR-head status is uncertain, preserve the ordinary CI
path. Branch names and the absence of a local PR record do not establish that a
push is outside a PR.

For a non-PR checkpoint or evidence publication, prefer a repository-supported
CI-skip mechanism when policy permits and no required validation depends on that
push. Check the relevant workflow triggers: a skip trailer may not suppress every
workflow. Batch related evidence rather than launching duplicate validation for
each checkpoint, and record the classification, skip mechanism, and original
runtime/harness/source bindings in the handoff. This does not waive required
checks on implementation PRs or artifact-only PRs. If the branch later becomes
a PR head, obtain the required current-head CI; a skipped run is not a passing
gate. Do not change workflows or cancel other lanes' runs merely to enable this.

## Hosted CI Capacity And Push Batching

Treat scarce hosted runners as a shared resource separate from agent and local
test concurrency. When a graph has overlapping PRs or CI queues are material,
inspect push and PR triggers, platform matrices, run attempts and required
checks before choosing an intervention. Use the read-only timing inventory and
the cancellation/coverage safeguards in [CI capacity](references/ci-capacity.md).
Measure job creation-to-start separately from execution and verify dependencies;
queued work is pending, not a failure or proof of a particular account limit.

When an independently useful patch is stable, its focused behavior test passes,
and the local pre-push gate is green (formatting clean via `gofmt -l`, `go vet`
or linter clean, affected package tests passing, and doc-contract checks clean
when docs/specs changed), push that commit and open or update its
PR (keeping incomplete iterations in Draft PRs to avoid burning heavy CI
matrices, holding non-urgent pushes/rebases while `@codex review` is pending,
and opting into `[ci full]` / `ci:full` when touching high-risk
OS/mmap/durability/format internals or final qualification).
PR promptly. Verify that CI started on the intended SHA. Run the broader suite
and workload qualification alongside CI and post the results on the same PR.
Merge each qualified increment as soon as its own dependencies and gates clear.
When delivery stalls, compare commit-to-PR time with CI queue and run time.

Give workers their normal provisional construction grants. Coordinate graph-owned
pushes: batch compatible fixes, evidence and base syncs into a coherent candidate,
and avoid redundant intermediate pushes whose only purpose is a fresh CI cycle.
Do not delay a needed durable checkpoint, usable predecessor snapshot, mature
critical-path head, or required current-head qualification merely to wait for an
idle runner or another PR. Continue independent local work while CI runs. A draft
PR or non-PR branch can still trigger push workflows; verify, do not assume it is
free. Apply existing safe CI-skip rules only to eligible non-PR checkpoints.

An owned run may be canceled only when its exact candidate is confirmed
superseded, it is not needed as evidence, and its verified replacement and scope
satisfy the safeguards in the reference. Never cancel another lane's work or
protected-branch/merge-queue qualification to create capacity. For an authorized
CI improvement, prefer workflow-specific, event- and branch-scoped cancellation
of superseded work, with protected events isolated and current-head checks
preserved. Review coverage, existing CI-optimization owners, and source-bound
timing before changing platform matrices, caches, triggers, or runner capacity.

## Conservative Execution Budget

Optimize for verified progress toward the agreed parent outcome per usage window.

- Default to **one active subagent when useful work can run in parallel**,
  otherwise zero. The coordinator handles live inventory, DAG/state updates,
  straightforward diagnosis, integration, and merge-authority allocation. A
  delegated PR finalizer owns its assigned PR's active readiness loop and may
  merge it only when given explicit per-PR authority.
- Raise to **two active subagents** only when two ready assignments are independent,
  use isolated worktrees for writes, have disjoint contract/conflict surfaces, and each is
  expected to save substantial elapsed time. Two is the normal hard ceiling.
- Never use three or more concurrent subagents unless the user explicitly opts
  into high-concurrency execution for the current graph.
  An explicit request to fan out across more than two safe independent workstreams
  supplies that opt-in; use only the justified lanes and available resource budget.
  Preserve the one/two-worker defaults when no such direction exists.
- Choose ready assignments by their dependencies and conflict surfaces, not the
  number of issues. Several workers may own independent slices of one node
  within this budget; keep one integration and acceptance owner for the node.
  Follow **Parallel Slices Within A Node** below. Reuse slice workers for their
  fix loops; do not duplicate implementation, expensive runs, or evidence.
- Do not delegate inventory, status polling, simple CI log extraction, tracker
  edits, branch synchronization, or merge commands as standalone work. PR
  finalization is active ownership, not an agent assigned only to wait for CI;
  a merge may be the final action of an explicitly authorized end-to-end
  finalization assignment.
- Start the highest-priority dependent node provisionally against recorded
  exact predecessor snapshots once their contracts are `dependency-ready`.
  Pending predecessor CI/review or an unmerged PR is not a start blocker.
  Mark the lane provisional,
  keep it unmergeable, and separate reusable construction/implementation from
  merge-identity-bound evidence. Resync and revalidate after the predecessor
  merges; discard or rerun candidate-bound outputs that cannot survive the new
  identity.
- Do not duplicate evidence. If exact-head CI or a worker already ran a broad
  suite, reviewers run only bounded tests that target a concrete risk.
- Reuse completed workers for their fix loops. Stop blocked, capacity-starved,
  or unnecessary work through the available lifecycle tools. Close/release agents
  when supported; interruption alone does not prove a runtime slot was freed.
  In Codex, restart an idle or completed worker with `followup_task`;
  `send_message` alone does not restart it. Record a runtime grant as queued
  until the worker confirms execution started; sending the grant is not evidence
  that a test or implementation is running.
- Do not keep an agent pending for model capacity. After one capacity error or
  two minutes without starting useful work, stop its work and perform the task
  locally when possible. Do not automatically substitute another model. For
  an internal review gate, use the documented mock subagent fallback below.
  If target policy explicitly requires a separately independent reviewer,
  keep that gate outstanding until such a reviewer is available.
- Time-box delegated read/review work to about 10 minutes. Treat about 25
  minutes without visible implementation progress as a checkpoint, not a
  push, review, or handoff boundary. Request a concise status once; stop only
  when the worker is blocked, outside scope, or no longer useful.
- Prioritize the critical path; use its unavoidable waits for useful independent
  research, prototypes, and tests within these limits. Available slots alone do
  not justify work, and measurement exclusivity does not serialize all exploration.

## Parallel Slices Within A Node

Split a node when genuinely independent work can advance its outcome concurrently.
In existing graph state and worker handoffs, name each slice's deliverable,
source/contract snapshot, prerequisites, owned files and worktree, required
evidence, integration owner, and acceptance boundary. Each writer uses an isolated
worktree; the integration owner alone changes the canonical candidate and accepts
the combined packet. Coordinate shared seams before conflicting edits.

Source/causal review, reproduction narrowing, test design, and independent client
or harness preparation may run alongside one another or a repair. An unresolved
cause permits bounded diagnosis and reusable preparation, not a speculative
causal production fix before the issue's reproduction/decision gate. Start usable
downstream preparation without waiting for unrelated repair merges; retain actual
contract dependencies and final qualification/merge gates. A reviewer consumes a
pinned candidate; later relevant edits require reassessing that review.

Separate source ownership from runtime ownership. Give each expensive reproduction,
benchmark, or retained-evidence run one execution owner and share its artifacts;
parallel slices do not authorize duplicate runs or waive resource/isolation rules.
Integrate useful slices into the coherent issue packet rather than creating a PR
or delivery gate for every worker. A slice handoff does not complete the node.
Apply the concurrency budget and stricter repository/scientific restrictions;
intra-ticket parallelism is not unlimited fanout or new execution authority.

## Asynchronous Disk Cleanup

**Delete released local worktrees and disposable outputs during execution.**
Make the release decision when a test or benchmark stage ends, a candidate is
retired or superseded, a PR merges, or a lane stops. Assign exact paths to one
owner and reclaim each released path in that batch, even while related evidence
review, CI, or merge is pending. Apply this to disposable DBs, generated datasets,
binaries, and staging. Keep only required evidence and unique work. Verify the
durable location and record why it must be retained. Pushed source refs and
reproducible input recipes normally suffice for recovery.
Delete disposable outputs in place after verification of their release.
Active descendants, dirty or unpushed work, primary checkouts, and required
scientific/review evidence remain protected. A blocked remote-branch deletion
does not block eligible local worktree or output deletion.

Use one direct-child `gpt-6.2-sol` cleanup agent for sizeable released batches
while useful graph work continues. Read
[references/disk-cleanup.md](references/disk-cleanup.md) before assigning it and
use the cleanup template in `references/worker-prompts.md`. It counts toward the
existing concurrency budget; queue cleanup when slots are occupied. Batch and
reuse this role instead of spawning a cleaner after every command. If delegation
is unavailable or only cleanup remains, finish the eligible batch locally.

Register large paths and their expected release events when allocating them.
At each release event (stage completion, PR merge, candidate retirement, or
stopped worker), immediately delete no-longer-needed checkouts/worktrees (and
close/release finished worker runtimes that hold harness-managed worktrees),
delete their per-lane `TMPDIR`/`GOTMPDIR` roots and verified disposable DBs
(including remote benchmark host data directories such as `treedb_data/` after
reopen/evidence checks), and run live-safe LRU pruning on the persistent shared
agent `GOCACHE` via `scripts/gocache_prune.py` (default `--max-gb 10
--target-gb 6 --min-age-seconds 7200`, or `--max-gb 8 --target-gb 5` on laptops
with `< 50 GiB` free) so hot stdlib/`-race`/dependency artifacts stay warm while
superseded large `.a` archives are bounded. Sweep remaining released paths and
any orphaned ad-hoc `/tmp/*-gocache` directories at closeout (only wipe an
entire cache with `go clean -cache` when zero consumers are active and an
explicit exception or full reset is needed).
Record a concrete consumer, evidence requirement, or blocker for any large
path still present. Route helper-skill post-merge cleanup to the same owner.
Verify deletion, worktree deregistration, or cleared build entries before
marking cleanup complete. Use an exposed subagent for cleanup that runs
alongside execution. Collect its outcome before the final report.

## Critical-Path Finalization and Monitoring

Keep finalization in the main thread when it is the only critical-path work.
Delegate a finalizer only when concrete useful authorized work can run alongside
it, not merely because a PR is mature. When a mature PR has a stable exact head
and a successor can start provisionally, delegate its complete readiness loop and
explicitly decide whether that assignment includes merge authority; then begin
the highest-priority safe successor immediately in an isolated worktree. Do not
duplicate the finalizer's polling or gate work in the coordinator. If that
parallel work finishes and the
coordinator is only waiting on the delegated reviewer/finalizer, reclaim ownership:

- Obtain one compact checkpoint (head, findings, checks/retries, dirty files,
  in-flight commands and merge authority), then stop/release the worker before
  taking over writes or merge execution. If a command was in flight, establish
  its outcome first. There must be exactly one active readiness/writer owner.
- Reuse completed reviews and tests that still apply; refresh outstanding facts once.
  Continue the same PR locally without another review, push, implementer or
  approval request unless changed code, a real finding or policy requires it.

The active readiness owner owns the continuous readiness loop from the first
push, including when no ownership transfer occurred. Ordinary
pending CI/review is not a reason to end the turn or require the user to say
"resume" again. Before waiting, inspect the remaining graph for meaningful
authorized work: implement an independent ready node, start an eligible
provisional successor from its recorded predecessor contract, **proactively
dispatch an async flake-repair worker off `origin/main` for any newly observed
unrelated CI flake or noisy gate** (rather than idling until `gh run rerun --failed`
can run), resolve existing review findings, or prepare the merge packet (policy,
description, evidence applicability, predecessor state, and cleanup ownership).
If delegation is unavailable during a long CI wait, start the isolated flake
diagnosis/repair locally while the watcher monitors the primary PR. Choose work that
advances an acceptance criterion or removes a known merge blocker; do not
manufacture tests, reports, tracker edits, or repeated inventories to fill time.
Preserve one writer per surface, measurement isolation, and final-base gates.
Record the concrete reason if no useful independent work can proceed.

Start one quiet, fail-fast watch/event mechanism for the sole readiness owner and
continue useful work while it waits. Prefer [scripts/watch_ci.py](scripts/watch_ci.py)
(with `--poll-interval 20` or `30` for fast runs) when its scope fits; read
[references/ci-watcher.md](references/ci-watcher.md) for exact head/base and
workflow-attempt bindings, exit events, bounded foreground invocations, and the
asynchronous harness continuation pattern. The watcher fails fast—surfacing a
failed job on the next snapshot while sibling jobs are still running—distinguishes
required from advisory PR checks, and reports observed failures without rerunning
or merging. Its CI-success notification still requires the full live merge gate.
When falling back to `gh pr checks --watch`, **always pass `--fail-fast`** (e.g.
`gh pr checks <PR> --watch --fail-fast -i 20`) and never sit blocked for a full
30-minute run on bare `gh pr checks --watch` after an early shard fails. On an
early failure wakeup, pull the completed failed job's log immediately via
`gh api /repos/<OWNER>/<REPO>/actions/jobs/<JOB_ID>/logs` (which works while the
workflow run is still in progress, unlike `gh run view --log-failed`), start
diagnosing/reproducing locally right away (or dispatch an async flake worker if
unrelated), and decide whether to push immediately (blocking compile/format or
clear single-cause failure) or let near-done sibling shards finish so related
failures land in one coherent batch.
Keep tool output compact and updates brief; avoid duplicate monitors, fresh
reviews, pushes or tests just because time passed.
The delegated-owner polling cadence does not prohibit monitoring external CI
after reclaiming ownership. Keep individual blocking waits within harness limits.

Keep individual blocking tool calls within 60 seconds or a shorter harness limit.
A watcher process may run longer under supported asynchronous execution; yield
control promptly so graph work continues and retain the continuation that delivers
its eventual result. A shell background PID alone does not wake the agent.
Follow the active harness's progress-update requirements; watcher liveness alone
does not call for repeated CI status messages. A bounded invocation expiring is a
monitoring checkpoint, not an execution deadline. Refresh outstanding gates after
an actionable event; an unchanged slice needs no duplicate API inventory.
Completed CI does not imply review completion, or vice versa. When nothing has
changed, continue useful work or resume the quiet wait.

If a gate appears stalled, inspect the actual run/review request, queue or runner
state, provider errors, and available policy-approved recovery before deciding
it is blocked. Ordinary queueing, slow execution, and unchanged polls alone do
not establish unavailability. Do not wait indefinitely on confirmed unavailable
infrastructure or a required reviewer: record the evidence, attempted permitted
recovery/fallback, responsible owner, and concrete unblock condition. Do not
submit duplicate review requests or cancel/restart healthy runs to manufacture
progress. Review-request caps bound requests, not monitoring of an existing one.

Persist the owner, exact head, outstanding gate and next action. On completion,
recheck live readiness status and merge/proceed immediately when
authorized. On failure, diagnose and repair or retry only the affected gate
within existing policy; waiting is not permission for unbounded retry churn.
After a push, update the recorded head/base and let the active readiness owner
decide whether fresh test, benchmark, or review evidence is needed from the
actual diff, affected contracts, base/environment changes, failures, and repo
policy. A push or new SHA alone does not require another review or full suite.
Reuse evidence that still covers the candidate when policy permits, preserving
its original SHA and a concise applicability rationale. Refresh only affected,
missing, or explicitly required gates; never relabel old evidence as a new-head
CI run or review. Before merge, recheck the live head/base, required checks,
approvals, and review threads. Before retrying CI, inspect
the exact failure logs, classify whether the failure intersects changed paths or
contracts, run the smallest useful reproduction when feasible, and retry only
failed jobs once; diagnose any repeat instead of cycling reruns.
End the turn for completion, an explicit pause, a genuine blocker requiring new
authority/input, or a harness limit—not merely an unchanged pending status.
Before an unavoidable harness exit, persist a resumable checkpoint: repository,
PR/issue URLs, branch/worktree, exact head/base, sole readiness owner, pending
run/job URLs or IDs, review request/result IDs and SHA bindings, evidence paths,
retry/request counts, last observed state/time, and next command or event to
inspect. State the actual exit limit and that acceptance remains incomplete;
an arbitrary self-imposed polling budget is not a harness limit. On continuation,
refresh live head/base and outstanding gates first, reuse applicable evidence,
and resume the existing loop without another permission or review request.
Do not claim background monitoring after exit unless an actual supported watcher
remains active and its ownership and delivery mechanism are recorded.
Do not invent automatic wake or create a goal just to wait. Continuous monitoring
does not waive predecessor merges, required exact-head reviews, required
current-head CI or landed-source evidence requirements, or grant new merge authority.

## Agent and Model Routing

Inspect the runtime's exposed model catalog, spawn schema, and concurrency
limit once. Record unavailable facts as unknown; do not change global config.
The preferred execution mode is **GPT-6.2 Sol only**: use the exact model ID
`gpt-6.2-sol` for every delegated worker, finalizer, adviser, support agent, and
independent reviewer. Adjust effort for the task instead of switching models.
Do not automatically route to Astra, Terra, Luna, or an older Sol model.
Explicit user model/effort choices and required repository reviewer identities
override this preference; record any deviation rather than silently relabeling it.

Prefer `gpt-6.2-sol` for the coordinator when the session model can be selected.
Keep the current coordinator and its effective supported effort; never spawn a
replacement coordinator or edit global config to enforce the preference. If it
uses another model, record that retained-session exception while keeping new
delegation on `gpt-6.2-sol`.

| Role | Preferred route when available | Use for |
| --- | --- | --- |
| Coordinator and final gate | `gpt-6.2-sol`, current supported effort | Graph, integration, blockers, and merge-authority decisions; retain an existing session as described above. |
| Complex implementation or specialist | `gpt-6.2-sol`, `high` | Ambiguous multi-file work, architecture, persistence/concurrency, security, or disputed evidence. |
| Routine implementation | `gpt-6.2-sol`, `medium` | A bounded issue with a clear contract, focused tests, and its fix loop. |
| PR finalization owner | `gpt-6.2-sol`, `medium` | One mature PR's mutable review/CI repair loop; use `high` for a demonstrated correctness, concurrency, or security risk. |
| Post-execution cleanup | `gpt-6.2-sol`, `medium` | A bounded batch of released worktrees and disposable generated outputs; sole owner of assigned deletion paths. |
| Fast support | `gpt-6.2-sol`, `low` | A substantial independent inventory or triage task that saves elapsed time. |
| Independent review or adviser | `gpt-6.2-sol`, `high` | A mature high-risk candidate or disputed finding, read-only in fresh context. Required reviewer identity is governed by repo policy. |

If `gpt-6.2-sol` is unavailable or cannot be selected, execute locally and record
the actual route. Do not silently spawn a different model. The internal or mock
subagent fallback below may satisfy the default internal review gate; an explicit
requirement for a separately independent reviewer still needs that reviewer.

### GPT-6.2 Sol Compatibility

- Supported API efforts are `low`, `medium`, `high`, `xhigh`, and `max`;
  `none` and `minimal` are unsupported. Use `low` for a fresh task that needs
  minimum reasoning. Preserve explicit supported effort choices; record any
  required adjustment from an unsupported effort.
- Set worker effort explicitly using the role table. The API defaults to
  `medium`, while the checked Codex catalog defaults to `low`; inspect the
  actual client rather than assuming its default matches the API.
- Use `xhigh` or `max` only for a named unresolved difficulty. `ultra` is a
  Codex runtime option only when exposed, not a documented API effort; use it
  only when explicitly requested, without waiving the concurrency/depth budget.
- Use the runtime's actual context and compaction limits, which may be smaller
  than the model's advertised API context. Keep assignment context bounded and
  recover durable graph state after compaction.
- API-backed tooling requires Responses for tool calling; Chat Completions
  does not support tools for this model. This skill uses exposed Codex
  collaboration tools; API multi-agent support does not grant recursive
  delegation, extra slots, or unsupported spawn flags.

Use actual tool fields: this collaboration runtime exposes `model` and
`reasoning_effort`; custom-agent config may use `model_reasoning_effort`.
Here, request `model="gpt-6.2-sol"`, the role's `reasoning_effort`, and
`fork_turns="none"` or supported bounded history, supplying the task context.
Full-history forks inherit model/effort and cannot take overrides here; use
them only when the parent already has the intended model and effort.
A model name in the prompt alone does not select it. An independent reviewer
gets fresh context, the exact candidate, requirements, and raw evidence,
without the implementer's conclusions.
Record requested versus actual routing only when observable. Never invent model
selection, async flags, lifecycle tools, or capacity that the harness lacks.

Delegate a whole packet or bounded intra-node slice with a clear outcome,
ownership boundary, base SHA, prerequisites, non-goals, required evidence, stop
conditions, time box, handoff format, and integration owner. Use an isolated
worktree per writer and serialize only actual shared contract/conflict surfaces.
Use additional slots only for ready independent work within the execution budget.

If subagent tools are unavailable or no task has a safe delegation boundary,
execute locally and record why. Do not pretend work was delegated.

### Bounded GPT-6.2 Sol Advisers

Use `gpt-6.2-sol` at `high` as a read-only adviser, not a shadow implementer:

- At ticket start, use at most one roughly ten-minute consultation only when
  architecture, persistence, concurrency, security, benchmark semantics, or a
  consequential unknown could change the design. Ask one concrete question.
- If the same material blocker category survives two coherent repair batches
  or repair heads, stop before a third micro-fix loop and ask the adviser one
  concrete root-cause or architecture question. Include both failed approaches
  and raw evidence.
- After the first coherent performance candidate fails a hard gate, consult
  the adviser once when the measured result contradicts the proposed mechanism,
  suggests work happened at the wrong stack boundary, or leaves the next
  causal experiment unclear. Provide the workload entrypoint, active counters,
  logical-versus-physical operation counts, and retained artifacts. This is a
  stack diagnosis, not permission for another implementation.
- The coordinator owns the decision and records whether the advice was used.
  No consultation is required when the issue is already well specified.

## Hard Invariants

- The coordinator owns the dependency graph and allocation of final merge authority.
- Honor task-specific reassessment instructions before committing to the next
  affected work. Increase reassessment when discoveries expose uncertainty;
  concrete tickets need it only on contradictory evidence. Use **Graph
  Reassessment** in `references/dependency-execution.md` to revise the approach
  while preserving the outcome and gates. Prefer necessary architecture or
  integration work over low-value micro-optimization.
- Workers may open or update PRs, but they must not merge unless explicitly
  delegated by the coordinator.
- Each node has one owner accountable for the total completion packet through a stable
  `dependency-ready` PR candidate, accepted non-PR output, or real blocker. A plan
  is a handoff boundary only when the assigned packet is an evidence-backed
  plan/issue revision; an opened PR, first test, or isolated code change is not
  implementation completion. Slice workers own their explicitly assigned outputs;
  the integration owner accepts them and remains accountable for the full packet.
- Finalize a mature issue-complete PR locally unless delegation enables concrete
  useful parallel work. A delegated direct-child finalizer may edit, test,
  commit, push, update the PR and resolve threads; merge needs explicit delegated
  authority. Reclaim sole ownership when parallel work is exhausted, as specified
  in **Critical-Path Finalization and Monitoring**. While delegation remains useful, the
  coordinator
  must not poll or message it more often than once every 15 minutes unless it
  reports completion or a blocker, and should advance a safe node meanwhile.
  Start the highest-priority safe successor provisionally from recorded
  predecessor snapshots. Starting it does not require separate user opt-in
  or delegated merge authority for the predecessor finalizer.
- Workers are direct children by default and may not delegate recursively.
- Normal subagent concurrency is at most one, may rise to two under the conservative
  budget, and may not exceed two without explicit user opt-in.
- Keep one writer per overlapping edit/conflict surface. A named `contract_owner`
  resolves cross-slice and cross-node decisions before affected parallel workers continue.
- Do not declare a dependent PR mergeable or merge it until predecessor PRs are merged,
  required non-PR outputs are accepted, conditional eligibility is satisfied, and
  the dependent branch has been updated/revalidated on the final base.
- `dependency-ready` unblocks provisional descendants by default. Start them
  while predecessors finalize, within ownership and concurrency limits;
  preserve final-base, mergeability, and scientific authority gates.
- Audit policy for every node from that PR's actual worktree or head commit, not only from the coordinator checkout. Enumerate all root/nested `AGENTS.md` files at that head and map every changed path to its applicable policy chain, including policy files added by the PR. Record local review-round caps and scientific acceptance/stop rules in graph state before review.
- Avoid review-credit churn: do not request Codex or other AI reviews until the PR is mature. Mature means coherent code pushed, focused tests and required benchmarks run or explicitly justified, PR body/status is current, no known local blockers remain, and latest-head CI is running or green.
- Before every `@codex review`, run the `github-pr-mergeable` Codex gate classifier. An exact-head no-findings issue comment is a completed clean result even without a formal review object. Stop requesting immediately when clean; any later unresolved Codex finding supersedes it. Keep the three-request exact-head anti-spam cap. PR-lifetime counts are advisory by default: six requests or three finding-bearing heads emit `review_churn_warning`, but a resolved, mature new head may continue.
- A new repair SHA does not erase review history, but advisory history does not change node state. Enter `review-scope-reset` only for an exhausted explicit repository/user hard cap or a coordinator-confirmed recurring material contract/architecture failure. Provider exhaustion is reviewer unavailability. Continue independent nodes; only the affected node and actual descendants wait when its required review is unavailable.
- Record hosted Codex quota, usage-limit, rate-limit, capacity, or service
  unavailability as `CODEX_REVIEW_UNAVAILABLE_QUOTA`: the review did not run.
  An internal read-only subagent review (`INTERNAL_SUBAGENT_REVIEW`) or, when
  delegation cannot run, a separate same-agent mock subagent review
  (`LOCAL_MOCK_SUBAGENT_REVIEW`) is an acceptable internal fallback. Follow
  [the shared contract](../github-pr-mergeable/references/internal-review-fallback.md).
  Prefer `gpt-6.2-sol` for a real review subagent; record the actual retained
  session model for a local mock review. Bind either mode to the exact candidate
  and record paths/claims, checks, findings, `ACCEPT` or `REJECT`, and no edits.
  Later scientific or review-relevant edits require renewed review. Explicit
  target-repository model identities or separately independent/hosted-only
  requirements still govern. Self-review is not independent; hosted review
  model selection is external and must not be reported as a pinned subagent.
- Treat material performance regressions as blockers unless the user or
  coordinator explicitly accepts them with evidence.
- A failed implementation candidate retires that mechanism, not automatically
  the issue or graph node. Before deferring or blocking the node, trace the
  measured workload through its real service/admission, batching, durability,
  publication, and acknowledgement boundaries; prove which layers were active
  from counters or a bounded trace; and record the smallest next causal test.
  If the evidence instead invalidates the issue premise, reconcile its scope
  with `gh-issue-planner` rather than forcing another implementation.
- Keep user changes safe. Do not revert unrelated local changes. Do not use
  destructive git commands unless explicitly requested.
- Continue until active node deliverables and the parent outcome are accepted, or
  an explicit pause, genuine blocker, harness limit, or user-accepted narrower
  endpoint stops execution. Deferral, retired hypotheses, and linked follow-ups
  leave unmet parent goals open with an owner/next action. Pause at
  `review-scope-reset` only under an explicit hard review policy or
  coordinator-confirmed recurring material scope failure, never advisory counts.

## Workflow

1. Load repo policy and relevant skills. For every adopted node, enumerate applicable root/nested policy files from its actual worktree or PR-head tree, inspect their exact bytes, and record review caps/stop rules separately. Inspect model, custom-agent, spawn, and concurrency capabilities; record routing fallbacks.
2. Inventory all issue and PR nodes from GitHub live state locally. Include title, URL,
   state, branch, base, current head SHA, CI status, linked issues, and existing
   review status.
3. Build a DAG. Use explicit dependencies first, then issue wording, PR stack
   notes, tracker order, and conflict/contract risk. Read the planner's
   reassessment instructions and identify consequential assumptions and decision
   boundaries where present.
4. Record a conflict/contract and routing table for every node and active slice:
   `contract_surface`, `conflict_surface`, `execution_mode`, `contract_owner`,
   `agent_role`, `requested_model`, `requested_effort`, and routing rationale.
   For split nodes, include slice prerequisites, owned files/worktree, integration
   owner and acceptance boundary in the existing state; no separate tracker is needed.
5. Post or update durable graph state before implementation. Prefer a parent
   issue comment with marker `<!-- codex-issue-graph-executor:state -->`;
   otherwise use a local manifest and report the fallback. Record large generated
   paths in existing node notes as they are created, with host, owner, purpose,
   and disposable/retained status; carry them into worker handoffs.
6. Present a concise graph snapshot and proceed immediately. Do not wait for
   plan approval because this skill defaults to execute-and-merge.
7. Start ready work, including independent slices within one node and provisional
   descendants of `dependency-ready` predecessors. Select assignments by usable
   contracts, prerequisites and conflict surfaces, not node count. Delegate when
   useful local or sibling work can proceed alongside it within the conservative
   budget; otherwise implement locally. Keep inventory, graph state, integration, and merge
   authority allocation with the coordinator. Use a bounded GPT-6.2 Sol adviser
   only under the triggers above.
8. Track node state transitions in durable graph state and any local manifest: `pending`, `running`, `dependency-ready`, `fix-needed`, `review-scope-reset`, `mergeable-candidate`, `merged`, `completed` (accepted non-PR output), or `blocked`. Record deliverable contracts and accepted output links/versions. Track requested and actual agent routing separately.
   A performance no-go normally leaves the node `fix-needed` while the
   failed-candidate intervention in `references/dependency-execution.md` runs;
   it is not a terminal state by itself. Apply that reference's **Graph
   Reassessment** at required boundaries or when findings undermine the plan;
   update affected issue scopes/edges before committing to further work.
9. Use sync windows instead of constant rebasing or polling: initial snapshot,
   predecessor contract change, predecessor merge, one pre-final-review sync,
   and conflict/test trigger. Advance the existing PR through ordinary repairs
   and base changes. Replace it only when repo policy permits and either its
   branch is genuinely irreparable or a recorded coordinator **Graph Reassessment**
   supersedes its obsolete completion packet. Prefer a merge queue or
   server-generated merge candidate when available instead of repeatedly
   chasing the default branch.
10. When an issue worker produces a mature, issue-complete PR, use
    `github-pr-mergeable` locally. Delegate one direct-child finalizer only when
    concrete useful parallel work exists. The active readiness owner
    inventories all current CI/review findings, repairs them in coherent
    batches, and owns the PR until `mergeable-candidate` or a named blocker.
    Do not poll a delegated owner more often than once per 15 minutes. A stable
    predecessor handoff starts the highest-priority safe successor provisionally
    without an opt-in prompt; when useful parallel work is exhausted, reclaim sole
    local ownership via **Critical-Path Finalization and Monitoring**, then
    continuously monitor the outstanding gates locally.
    The finalizer must stop before a third repair head for the same
    material failure category and return one named question for bounded GPT-6.2 Sol
    advice. The finalizer inventories all current review notes before editing,
    repairs compatible findings in one coherent batch, runs the proportional
    local checks, and then pushes once. Do not pay a CI cycle per comment unless
    a finding changes the contract or invalidates the remaining repair plan.
    The active merge owner then performs the final exact-head recheck. The
    coordinator is the normal merge owner unless it explicitly delegated merge
    authority for that PR as part of the complete finalization assignment. Apply the node's effective repository policy,
    record `review_churn_warning` as telemetry, and merge only when latest-head
    CI/reviews and required evidence are current, predecessor PRs are merged,
    required non-PR outputs are accepted, and conditional eligibility holds.
11. Merge in topological order. After each merge, update descendants to the
    final base, reassess evidence, and run affected or policy-required checks
    before declaring them mergeable. Release the merged node's local worktree
    and disposable outputs immediately after their consumers finish.
12. Reclaim eligible worktrees, generated outputs, and Go build caches through
    **Asynchronous Disk Cleanup** as consumers finish. Preserve
    `github-pr-mergeable` branch-cleanup policy and one cleanup owner. Before
    reporting completion, collect cleanup results or finish locally. Verify
    removed paths are absent, worktrees are unregistered, and cleaned cache
    entries are gone. Record every retained path's concrete blocker or explicit
    retention requirement.

## Dependency Ready

A node may be marked `dependency-ready` when:

For non-PR nodes, the required output must already be accepted and source/version
bound, with a stable downstream decision/contract and eligible successors recorded.
Such nodes finish as `completed`; never label them `merged`. An unresolved inquiry
does not select a conditional implementation. Reusable preparation can continue
without committing to its unknown decision.

For PR nodes:

- A PR exists with branch and latest head SHA.
- Implementation scope is substantially complete.
- Public contract surface is documented: APIs, formats, files, behavior, tests,
  benchmark expectations.
- Required local tests/benchmarks for that contract passed, or unrelated
  failures are documented.
- No unaccepted material performance regression remains.
- A review/fix loop or explicit self-review completed.
- Remaining work is expected to be CI, review polish, docs wording, or
  non-contract-changing cleanup.
- Known risks and possible contract churn are listed.

Do not mark dependency-ready if unresolved findings could change APIs, storage
formats, public semantics, test harness shape, or benchmark interpretation used
by descendants.

## Final Report

Lead with the outcome; summarize evidence and link detailed state. Report:

- Graph nodes and final state.
- Intended deliverables and accepted non-PR outputs, including verified ticket
  revisions and consequential plan changes. Separately state whether the parent
  goal was achieved, investigation completed, or optimization obligations remain.
- PRs merged, merge commits if available, and any issues closed/updated.
- Tests, benchmarks, CI, and review evidence used for each merge.
- Confirmation that AI reviews were requested only after mature PR heads, or not
  requested.
- Agent routing used for coordinator, implementation, inventory, and independent
  review, including any requested-versus-actual fallback.
- Any deferred nodes with blocker, owner, and next action.
- Per-node local worktree, local branch, and GitHub remote-branch cleanup status.
- Disk cleanup owner, removed or retained generated paths with reasons, cleared
  or retained Go build caches, and measured free-space change per affected
  filesystem. Distinguish size estimates from observed recovery.
- Durable graph-state location and whether any fallback execution path was used.

Read `references/worker-prompts.md` before dispatching workers. Read
`references/dependency-execution.md` when constructing or updating the DAG,
manifest, sync log, or merge gate.
