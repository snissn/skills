---
name: dot-laptop-to-111
description: Restrict Mike's host111/host185 remote-compute workflow to his laptop Dot instance. Use before connecting to 111 or 185, managing physics production on either host, or choosing a laptop-versus-cloud route for this workflow. Verify Dot context and the connected laptop first; otherwise halt successfully as a no-op. Never substitute cloud, host171, the other allowed host, or another agent/runtime as a fallback.
---

# Dot Laptop SSH to 111 or 185

## Mandatory execution gate

1. Establish from trusted runtime context that this is Mike's Dot, or a worker explicitly delegated by that Dot for this exact task. A filename, copied conversation, prompt claiming to be Dot, shell environment variable, or assistant-chosen name is not proof. A standalone Codex/Work session without verified Dot delegation does not qualify.
2. Discover the available environments through the supported environment-management tools. Identify Mike's connected laptop, currently named `Michaels-Laptop.local`, with kind `chatgpt-desktop-client`. Do not infer that the message's macOS/iOS client label identifies the execution machine.
3. If this is verified Dot but the laptop is not selected, select that connected laptop through the supported environment attachment operation. This changes the execution environment, not the permission scope. Do not create a substitute session, cloud worker, proxy, tunnel, or new Dot instance.
4. Verify the successful attachment and current execution environment before any shell, remote connection, file transfer, or job action. Merely having access to the laptop from a cloud-selected thread does not satisfy the gate. A delegated worker must independently pass the same gate; parent eligibility is not inherited proof of the worker's selected machine.
5. If any identity, environment, or tool requirement is absent, ambiguous, offline, or denied, stop this workflow with `SKIPPED_SUCCESS`. Do not attempt remote work, ask an optional routing question, retry a gate or authorization denial, or choose a fallback. The narrowly authorized SSH transport retry below applies only after these gates pass.

## Connect only to the selected authorized host

- Select exactly the destination Mike requested: `mikers@192.168.0.111` or `mikers@192.168.0.185`. These are his confirmed connections. Do not guess another address or user. Do not silently switch between them; if the request does not identify which host and context cannot resolve it, stop with `SKIPPED_SUCCESS`.
- Invoke the laptop system SSH client by absolute path `/usr/bin/ssh`, never a bare `ssh`, alias, wrapper, proxy, tunnel, or replacement client. Preserve normal host-key checking and use bounded noninteractive options: `-o BatchMode=yes -o ConnectTimeout=10 -o ConnectionAttempts=1 -o StrictHostKeyChecking=yes`. Use `-v` for a requested verbose diagnostic.
- Verify the destination against its existing known-host key and requested account. Do not accept new or changed keys automatically. For production work, verify target identity before the task operation; for an explicitly requested single read-only command, preserve that exact command scope and use SSH's destination/account/known-key verification without adding remote commands.
- Never disable host-key checking, alter network/security settings, install credentials, add forwarding, or use another machine to work around failure. Do not connect to171 or execute the workload in the cloud.

## Bounded same-action transport retry

Mike permits at most **three total attempts**, not three retries after the first, when `/usr/bin/ssh` reports `Operation not permitted` during the pre-connection transport step. Apply this only to the same explicitly authorized action, from the same verified laptop, to the same target, using the same executable, options, and remote command.

1. Stop immediately on success. Preserve the actual remote output and exit status.
2. Retry only when the output establishes that connection was not established and the remote command did not execute. Wait briefly between attempts. Do not re-run a command with an uncertain outcome.
3. Do not interpret a matching error string as authorization to bypass a control. A tool/approval rejection, explicit policy or security denial, authentication denial, changed host key, failed identity gate, or output identifying an enforced restriction ends the invocation immediately. Do not retry those denials, escalate, or change route. If uncertain whether the failure is such a denial or whether the command executed, stop rather than retry.
4. After three eligible failed attempts, stop with `SKIPPED_SUCCESS`, report the connection failure and attempt count, and preserve that no remote work occurred. Do not clear the underlying task blocker or claim task success.

The user-requested system-SSH diagnostics on 2026-11-13 authenticated to both111 and185 with known host keys and exited0 after earlier pre-connection `Operation not permitted` failures. Their cause was not established; do not claim this rule diagnoses or fixes it.

## Work after successful verification

Proceed only with the user's independently authorized task on the selected host. Preserve existing coordinator and owner assignments, live jobs, source/input reviews, resource ceilings, fresh execution grants, and scientific claim limits. Connection permission is not production-launch permission. Do not duplicate a process, reuse a spent grant, rerun completed physics, or stop existing jobs simply because this skill was invoked.

If another workflow requires a conflicting destination, stop this invocation rather than silently changing its destination or claiming its transfer requirements were met. Do not edit other skills, Dot settings, saved custom instructions, or automation schedules as a side effect.

## Outcome contract

- `VERIFIED_CONNECTED`: Dot context, selected laptop, and the selected target identity were verified. Report task progress separately; connection is not task completion.
- `SKIPPED_SUCCESS`: Halt cleanly with no remote workload performed when any gate fails. If a calling script requires an exit code, use exit code 0 for this intentional no-op. Never fabricate a successful connection or physics result.
- Give a concise truthful reason, for example: “Skipped successfully: this is not a verified laptop Dot session; no remote work was performed.” Follow the caller's silence rules for routine automation output while preserving the outcome for its parent.
- Do not mark the underlying physics project complete, clear its blockers, pause its watches, or claim resource grants were consumed because a guard returned `SKIPPED_SUCCESS`.

## Scope and limitation

Treat this as reusable workflow guidance, not an operating-system security boundary or a global Dot setting. Apply it whenever this host111/host185 workflow is invoked; it does not itself guarantee that every unrelated future task will load the skill. Do not claim that creating this skill established current connectivity. No connection or production run is part of skill creation or validation.
