---
name: codex-issue-graph-executor
description: "Execute GitHub issue graphs toward agreed outcomes with accepted decisions, ticket revisions, artifacts, and merged PRs. Use GPT-6.1 Sol-only delegation by default, provisional dependent work, conservative concurrency, and current-head PR gates. Use for graph execution, not requests to review or edit this skill."
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

## GPT-6.1 Sol Execution Guidance

Use the [official GPT-6.1 Sol guidance](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
and [Codex subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents)
(checked 2026-10-01), with the runtime-specific routing below:

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
- The coordinator may revise the remaining graph and create or explicitly
  adopt necessary nodes within that scope as evidence changes. Map them to the
  agreed parent outcome and preserve acceptance criteria, guardrails, ownership,
  and history; necessary issue maintenance needs no repeated permission.
- Execution includes deleting released local worktrees and verified disposable
  outputs owned by this graph after merge or retirement, under **Asynchronous
  Disk Cleanup**. Local cleanup is required; archiving or moving a disposable
  worktree does not satisfy it.
  Editing this skill does not itself authorize a disk cleanup run.
- The coordinator may merge after all gates pass; workers may not merge unless
  the coordinator explicitly delegates that action for a specific PR.
- Do not merge PRs outside the selected graph, even if they are nearby.
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

## Compose With

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
- Keep at most one implementation worker per node. Reuse that worker for its
  fix loop; do not launch parallel implementer, benchmark, and review agents for
  the same PR.
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
- Do not keep an agent pending for model capacity. After one capacity error or
  two minutes without starting useful work, stop its work and perform the task
  locally when possible. Do not automatically substitute another model; record
  unavailable independent review as an outstanding gate, not self-review.
- Time-box delegated read/review work to about 10 minutes. Treat about 25
  minutes without visible implementation progress as a checkpoint, not a
  push, review, or handoff boundary. Request a concise status once; stop only
  when the worker is blocked, outside scope, or no longer useful.
- Prefer sequential depth on the critical path over keeping every slot busy.

## Asynchronous Disk Cleanup

After a PR merges, delete its local worktree and disposable test/benchmark DBs,
datasets, binaries, and run-local caches as soon as their writers and consumers
release them. Do not save, archive, move to Trash, or copy the complete worktree
or disposable outputs for possible future use. Keep only explicitly required
evidence and unique work, with a verified durable location and a retention reason;
pushed source refs and reproducible input recipes normally suffice for recovery.
Active descendants, dirty or unpushed work, primary checkouts, and required
scientific/review evidence remain protected. A blocked remote-branch deletion
does not block eligible local worktree or output deletion.

Use one direct-child `gpt-6.1-sol` cleanup agent for sizeable released batches
while useful graph work continues. Read
[references/disk-cleanup.md](references/disk-cleanup.md) before assigning it and
use the cleanup template in `references/worker-prompts.md`. It counts toward the
existing concurrency budget; queue cleanup when slots are occupied. Batch and
reuse this role instead of spawning a cleaner after every command. If delegation
is unavailable or only cleanup remains, finish the eligible batch locally.

Start after a resolved merge, retired candidate, or completed test/benchmark
stage releases its worktree or generated outputs. The coordinator assigns exact
paths and sole deletion ownership; keep active/provisional lanes and retained
evidence protected. Hand helper-skill post-merge cleanup to that owner rather
than running two cleaners. Releasing or queuing a path is not completed cleanup;
verify actual deletion and removal of its worktree registration. Async means an
exposed subagent running alongside
execution, not a detached daemon or invented spawn flag. Collect its outcome
before the final report; never claim cleanup will continue after the turn ends.

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

After transfer, the main thread owns the continuous readiness loop. Ordinary
pending CI/review is not a reason to end the turn or require the user to say
"resume" again. Use one native watch/event mechanism when available, or repeated
bounded status polling with waits. Keep tool output compact and updates brief;
avoid duplicate monitors, fresh reviews, pushes or tests just because time passed.
The delegated-owner polling cadence does not prohibit monitoring external CI
after reclaiming ownership. Keep individual blocking waits within harness limits.

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
Do not invent automatic wake or create a goal just to wait. Continuous monitoring
does not waive predecessor merges, required exact-head reviews, required
current-head CI or landed-source evidence requirements, or grant new merge authority.

## Agent and Model Routing

Inspect the runtime's exposed model catalog, spawn schema, and concurrency
limit once. Record unavailable facts as unknown; do not change global config.
The preferred execution mode is **GPT-6.1 Sol only**: use the exact model ID
`gpt-6.1-sol` for every delegated worker, finalizer, adviser, support agent, and
independent reviewer. Adjust effort for the task instead of switching models.
Do not automatically route to Astra, Terra, Luna, or an older Sol model.
Explicit user model/effort choices and required repository reviewer identities
override this preference; record any deviation rather than silently relabeling it.

Prefer `gpt-6.1-sol` for the coordinator when the session model can be selected.
Keep the current coordinator and its effective supported effort; never spawn a
replacement coordinator or edit global config to enforce the preference. If it
uses another model, record that retained-session exception while keeping new
delegation on `gpt-6.1-sol`.

| Role | Preferred route when available | Use for |
| --- | --- | --- |
| Coordinator and final gate | `gpt-6.1-sol`, current supported effort | Graph, integration, blockers, and merge-authority decisions; retain an existing session as described above. |
| Complex implementation or specialist | `gpt-6.1-sol`, `high` | Ambiguous multi-file work, architecture, persistence/concurrency, security, or disputed evidence. |
| Routine implementation | `gpt-6.1-sol`, `medium` | A bounded issue with a clear contract, focused tests, and its fix loop. |
| PR finalization owner | `gpt-6.1-sol`, `medium` | One mature PR's mutable review/CI repair loop; use `high` for a demonstrated correctness, concurrency, or security risk. |
| Post-execution cleanup | `gpt-6.1-sol`, `medium` | A bounded batch of released worktrees and disposable generated outputs; sole owner of assigned deletion paths. |
| Fast support | `gpt-6.1-sol`, `low` | A substantial independent inventory or triage task that saves elapsed time. |
| Independent review or adviser | `gpt-6.1-sol`, `high` | A mature high-risk candidate or disputed finding, read-only in fresh context. Required reviewer identity is governed by repo policy. |

If `gpt-6.1-sol` is unavailable or cannot be selected, execute locally and record
the actual route. Do not silently spawn a different model. A mandatory independent
review still needs an available, policy-compliant independent reviewer.

### GPT-6.1 Sol Compatibility

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
Here, request `model="gpt-6.1-sol"`, the role's `reasoning_effort`, and
`fork_turns="none"` or supported bounded history, supplying the task context.
Full-history forks inherit model/effort and cannot take overrides here; use
them only when the parent already has the intended model and effort.
A model name in the prompt alone does not select it. An independent reviewer
gets fresh context, the exact candidate, requirements, and raw evidence,
without the implementer's conclusions.
Record requested versus actual routing only when observable. Never invent model
selection, async flags, lifecycle tools, or capacity that the harness lacks.

Delegate only work with a clear outcome, ownership boundary, base SHA, non-goals,
required evidence, stop conditions, time box, and handoff format. Prefer a
single implementation worker in an isolated worktree. Serialize shared
contract and conflict surfaces, and leave the second slot unused unless a
specific independent assignment justifies it.

If subagent tools are unavailable or no task has a safe delegation boundary,
execute locally and record why. Do not pretend work was delegated.

### Bounded GPT-6.1 Sol Advisers

Use `gpt-6.1-sol` at `high` as a read-only adviser, not a shadow implementer:

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
- An issue worker owns the total issue completion packet through a stable
  `dependency-ready` PR candidate, accepted non-PR output, or real blocker. A plan
  is a handoff boundary only when the assigned packet is an evidence-backed
  plan/issue revision; an opened PR, first test, or isolated code change is not
  implementation completion.
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
- Keep one writer per contract/conflict surface. A named `contract_owner`
  resolves cross-node decisions before parallel workers continue.
- Do not declare a dependent PR mergeable or merge it until predecessor PRs are merged,
  required non-PR outputs are accepted, conditional eligibility is satisfied, and
  the dependent branch has been updated/revalidated on the final base.
- `dependency-ready` unblocks provisional descendants by default. Start them
  while predecessors finalize, within ownership and concurrency limits;
  preserve final-base, mergeability, and scientific authority gates.
- Audit policy for every node from that PR's actual worktree or head commit, not only from the coordinator checkout. Enumerate all root/nested `AGENTS.md` files at that head and map every changed path to its applicable policy chain, including policy files added by the PR. Record local review-round caps and scientific acceptance/stop rules in graph state before review.
- Avoid review-credit churn: do not request Codex, Copilot, CodeRabbit, or other AI reviews until the PR is mature. Mature means coherent code pushed, focused tests and required benchmarks run or explicitly justified, PR body/status is current, no known local blockers remain, and latest-head CI is running or green.
- Before every `@codex review`, run the `github-pr-mergeable` Codex gate classifier. An exact-head no-findings issue comment is a completed clean result even without a formal review object. Stop requesting immediately when clean; any later unresolved Codex finding supersedes it. Keep the three-request exact-head anti-spam cap. PR-lifetime counts are advisory by default: six requests or three finding-bearing heads emit `review_churn_warning`, but a resolved, mature new head may continue.
- A new repair SHA does not erase review history, but advisory history does not change node state. Enter `review-scope-reset` only for an exhausted explicit repository/user hard cap or a coordinator-confirmed recurring material contract/architecture failure. Provider exhaustion is reviewer unavailability. Continue independent nodes; only the affected node and actual descendants wait when its required review is unavailable.
- Record hosted Codex quota, usage-limit, rate-limit, capacity, or service
  unavailability as `CODEX_REVIEW_UNAVAILABLE_QUOTA`: the review did not run.
  Prefer an independent read-only `gpt-6.1-sol` review only when repo policy
  permits that reviewer identity, bound to the exact candidate. Record
  paths/claims, checks, findings, `ACCEPT` or `REJECT`, and no candidate edits.
  Later scientific edits invalidate it. A named GPT-5.6 Pro or
  `LOCAL_GPT56_REVIEW` policy fallback remains that specific identity: a Sol
  review does not satisfy it unless policy explicitly permits substitution.
  Use a different model only for an explicit user model exception or a
  repository-required reviewer identity, recording the reason. Otherwise keep
  the gate outstanding until a compliant independent review is available.
  Self-review is not independent; hosted review model selection is external
  and must not be reported as a pinned `gpt-6.1-sol` subagent.
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
4. Record a conflict/contract and routing table for every node:
   `contract_surface`, `conflict_surface`, `execution_mode`, `contract_owner`,
   `agent_role`, `requested_model`, `requested_effort`, and routing rationale.
5. Post or update durable graph state before implementation. Prefer a parent
   issue comment with marker `<!-- codex-issue-graph-executor:state -->`;
   otherwise use a local manifest and report the fallback. Record large generated
   paths in existing node notes as they are created, with host, owner, purpose,
   and disposable/retained status; carry them into worker handoffs.
6. Present a concise graph snapshot and proceed immediately. Do not wait for
   plan approval because this skill defaults to execute-and-merge.
7. Start ready nodes, including provisional descendants of `dependency-ready`
   predecessors. Delegate one when useful local work can proceed alongside it;
   otherwise implement locally. Add a second worker only when the conservative
   budget permits it. Keep inventory, graph state, integration, and merge
   authority allocation with the coordinator. Use a bounded GPT-6.1 Sol adviser
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
    material failure category and return one named question for bounded GPT-6.1 Sol
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
12. Delete eligible worktrees and generated outputs through **Asynchronous Disk
    Cleanup** as consumers finish; do not accumulate them until graph closeout.
    Preserve `github-pr-mergeable` branch-cleanup policy and one cleanup owner.
    Before reporting completion, collect cleanup results or finish locally;
    verify removed paths are absent and worktrees unregistered. Record every
    retained path's concrete blocker or explicit retention requirement; do not
    replace deletion with a local archive.

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
- Disk cleanup owner, removed/retained generated paths with reasons, and measured
  free-space change per affected filesystem; distinguish size estimates from
  observed recovery.
- Durable graph-state location and whether any fallback execution path was used.

Read `references/worker-prompts.md` before dispatching workers. Read
`references/dependency-execution.md` when constructing or updating the DAG,
manifest, sync log, or merge gate.
