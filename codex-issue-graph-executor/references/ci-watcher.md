# Quiet CI notifications

Use `scripts/watch_ci.py` when CI is running and the readiness owner can continue
useful graph or merge preparation. It uses Python 3.10+ and authenticated `gh api`
reads. It never edits a PR, reruns/cancels a workflow, requests review, or merges.

Pin the full PR head and base SHAs already recorded in the readiness packet. Each
PR snapshot independently reads the live repository base-branch ref target:
GitHub's PR `baseRefOid` can lag an advancing branch. A changed live target emits
`superseded`, even if the PR's cached SHA is unchanged; an unavailable/deleted
base ref fails closed as `error`. Add
selected run IDs when workflow-level waiting/approval state or constituent job
failures need monitoring. PR mode observes check runs and legacy statuses at the
head commit, paginates all contexts, and uses GitHub's `isRequired` classification.
`--require-check NAME` additionally waits for an expected check to appear, and
treats it as required. It does not discover the repository's full required-check,
ruleset, test-merge, or merge-queue contract. Run-only mode cannot monitor a PR base
or branch movement: include `--pr` and `--base` when those identities matter.

```bash
python3 ~/.codex/skills/codex-issue-graph-executor/scripts/watch_ci.py \
  --repo OWNER/REPO --pr 123 --head FULL_HEAD_SHA --base FULL_BASE_SHA \
  --run-id 456 --run-attempt 456:1 --require-check 'unit tests' \
  --max-wait 50
```

The default foreground deadline is 50 seconds, including requests; each request
times out within 30 seconds. `--max-wait 0` waits until an event, and a larger
value supports asynchronous execution. Polls default to 60 seconds, minimum 15;
unchanged polls print nothing. Failures wake on the next snapshot rather than
waiting for sibling jobs or the workflow to finish. This is polling, so normal
notification latency includes the poll interval and API calls.

By default the process writes JSON lines: one start line and one terminal event line. Keep the output
with the existing readiness evidence if failures matter; the final line preserves
all observed failed checks/jobs with their original IDs and run attempts. Never
overwrite the original failure with a later retry result. A new invocation cannot
recover failures from deleted/replaced checks; retain the earlier result and pin
`--run-attempt RUN_ID:ATTEMPT` when resuming an existing run. Without that flag,
the first observed attempt is pinned for this invocation. It never switches runs.

| Exit | Event | Readiness-owner action |
| --- | --- | --- |
| 0 | `ci_success` | Selected runs succeeded; observed checks have accepted outcomes or an explicitly acknowledged advisory failure, confirmed by a second read. Refresh all live required checks, test-merge/base identity, review findings/threads, approvals and predecessor gates before any merge. Late-registering/missing unlisted checks remain possible. |
| 1 | `failure` | Diagnose the recorded required PR check or explicitly selected workflow/job. An already failed initial snapshot also exits immediately. |
| 2 | `error` | Snapshot unavailable/incomplete, permission/rate/API problem, or timeout. No success inferred; investigate before resuming. |
| 3 | `superseded` | PR head/base/base branch or selected workflow attempt changed. Preserve old evidence and refresh the candidate bindings. |
| 4 | `advisory_failure`, `intervention`, `review_changed`, `pr_closed` | Inspect the event: advisory check, draft/conflict, requested changes, review decision change, workflow approval, inconclusive/skipped result, or closed/merged PR. Advisory failure is not relabeled a required branch-protection failure. |
| 5 | `cancelled` | Inspect remote workflow/check cancellation; no automatic rerun. |
| 124 | `checkpoint` | Invocation deadline reached. Keep acceptance open and continue monitoring with the same bindings. |
| 130 / 143 | local watcher interrupted/terminated | Only the watcher stops; remote runs remain unchanged. |

For an explicit workflow's job, `required: null` means the watcher cannot map that
job to a PR check; `scope: explicit_workflow` records the user's selected watch
target without inventing branch-protection status. A failed selected workflow job
always emits actionable `failure`, including when its matching check has
`isRequired=false` because only an aggregate check is protected. PR failures carry `required`
and `scope` (`required` or `advisory`). Completed advisory checks with neutral or
skipped outcomes are normal and do not block CI success. Required or explicitly
named checks with those outcomes prompt inspection; apply repository policy in
the full gate. A neutral/skipped selected workflow result also prompts inspection.
Review-decision changes wake the watcher, but it does not monitor individual
review comments or threads and does not replace the Codex review classifier.

## Already dispositioned advisory failures

After the coordinator has inspected the actual failure and recorded its disposition
in the readiness evidence, it may pass `--acknowledge-advisory-check-id ID` for
that exact GitHub CheckRun `databaseId`. Record the ID, head/base, execution times
and workflow attempt when available, evidence, owner, and why continued monitoring
is appropriate. The flag carries that existing disposition; it neither grants
waiver authority nor changes repository checks or merge requirements. Do not
automatically generate it from a nonrequired label, familiar check name, or an
earlier flag list. Refresh the evidence before reusing it on a new invocation.

```text
--acknowledge-advisory-check-id EXACT_ALREADY_DISPOSITIONED_CHECKRUN_DATABASE_ID
```

This suppresses repeat wakeups only for the same completed, advisory `FAILURE`.
It never suppresses a GitHub-required check, an explicitly named `--require-check`,
a selected workflow/job failure, cancellation, timeout, or unknown/incomplete state.
A different CheckRun ID is never acknowledged by name. A changed execution
timestamp or workflow attempt during the invocation invalidates the acknowledgement
and wakes the owner, including changes during the final confirmation read.
An absent completion timestamp fails closed. If an app reuses a CheckRun ID
without reporting any changed execution identity, the API cannot establish that
rerun; inspect and refresh the actual disposition before a new invocation.

Acknowledged failures remain `FAILURE` in `observed_failures`, with `check_id`,
`completed_at`, and `acknowledged_advisory: true`. Final notifications and bounded
checkpoints list the effective `acknowledged_advisory_check_ids`; the start line
records requested IDs. Preserve the original failure and disposition alongside
this output. CI-success notification with an acknowledged advisory failure still
requires the complete live merge gate and cannot certify an unresolved requirement.

## Selected job completion progress

When an artifact audit can start before sibling shards finish, optionally repeat
`--notify-job-id RUN_ID:JOB_ID` for exact GitHub workflow job IDs within selected
`--run-id` runs. For example, add `--notify-job-id 456:789` to the pinned command
above. This is an observation target, not a new required check or a workflow
completion condition. A missing target produces no notification and does not
alter the existing full-watch completion rules. Discover and record the exact job
ID first; names, substrings and historical replacement IDs are not selectors.

Each completed selected job emits one `job_completed` JSON line per invocation,
including an already completed job in the first snapshot. Unchanged polls remain
quiet. The event includes exact head/base, run ID, pinned attempt, workflow ID,
job ID/name, conclusion, completion time and URL; `terminal: false` and
`merge_authorized: false` distinguish progress from the final `ci_success` event.
The watcher continues monitoring the full selected workflow and PR head/live base.
It uses the existing snapshots without extra API reads or a polling-rate change.
Pin `--run-attempt` when resuming; otherwise the first observed attempt is pinned.
Once-only delivery is local to this process: a fresh invocation may report the
same completed job again, so retain its run/attempt/job identity with the receipt.

Existing terminal outcomes take priority over progress from the same snapshot:
failure, cancellation, intervention, supersession and errors stop the watch as
before. A failed selected job uses that existing terminal failure notification;
a sibling failure can suppress a selected success notification in that snapshot.
Full CI success is still confirmed by a second read before either its final
completion progress or success event. A missing conclusion/completion time or
mismatched selected job run/attempt fails closed. Neutral/skipped completion can
be reported as progress while the run continues; it grants no acceptance and
does not suppress the existing final workflow policy.

Success means the job finished, not that its artifact's samples/provenance were
audited. Start the read-only audit under the exact reported identity while sibling
CI continues. Preserve all original failures and the full merge gate. If using
the async continuation below, forward nonempty output while the process is still
running; waiting only for process exit would hide this early notification.

## Asynchronous Codex continuation

Use this pattern only when `functions.exec`, `yield_control`, and exec sessions
are actually exposed. Replace the command's sample IDs/SHAs with recorded values;
the command is trusted fixed text, never assembled from unquoted issue content.
Keep artifacts or logs under a verified task directory on `/mnt/fast4tb` if needed.

```javascript
// @exec: {"yield_time_ms": 1000, "max_output_tokens": 1200}
const launch = await tools.exec_command({
  cmd: "python3 /home/mikers/.codex/skills/codex-issue-graph-executor/scripts/watch_ci.py --repo OWNER/REPO --pr 123 --head FULL_HEAD_SHA --base FULL_BASE_SHA --run-id 456 --run-attempt 456:1 --max-wait 3600",
  yield_time_ms: 1000,
  max_output_tokens: 1200
});
if (!launch.session_id) {
  notify({event: "ci_watcher_exit", exit_code: launch.exit_code, output: launch.output});
} else {
  const session = launch.session_id;
  store("selected-pr-ci-watcher", {session_id: session, owner: "readiness-owner", command: "same pinned command above"});
  text({event: "ci_watcher_started", session_id: session, output: launch.output});
  await yield_control();
  // This continuation stays alive while the model does useful authorized work.
  // Each tool wait is bounded; do not poll GitHub again in the model loop.
  while (true) {
    const update = await tools.write_stdin({session_id: session, chars: "", yield_time_ms: 30000, max_output_tokens: 1800});
    if (update.session_id && update.output) {
      notify({event: "ci_watcher_progress", session_id: session, output: update.output});
    }
    if (!update.session_id) {
      notify({event: "ci_watcher_exit", session_id: session, exit_code: update.exit_code, output: update.output});
      break;
    }
  }
}
```

The retained async cell delivers the exit notification. If it remains running,
use `functions.wait` with its returned cell ID when collecting the final result;
do not launch another watcher. Record the session/cell and delivery owner in the
readiness state. If the harness cannot retain this continuation, use bounded
foreground invocations instead and report that automatic wake is unavailable.
Do not describe `nohup`, `&`, a shell PID, or a discarded promise as automatic
agent wake. A watcher deadline does not complete the graph or justify ending an
otherwise executable task. Reclaim or stop owned monitoring when its candidate
is retired, and collect the actual outcome before claiming completion.

Offline validation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s ~/.codex/skills/codex-issue-graph-executor/tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  ~/.codex/skills/codex-issue-graph-executor
```

API semantics: [workflow runs and attempts](https://docs.github.com/en/rest/actions/workflow-runs),
[workflow jobs](https://docs.github.com/en/rest/actions/workflow-jobs), and
[latest-commit and test-merge required checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).
