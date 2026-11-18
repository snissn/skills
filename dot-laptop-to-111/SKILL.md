---
name: dot-laptop-to-111
description: Connect directly from Mike's laptop to host111 or host185 over SSH, with bounded transport retries and honest failure reporting. Use for authorized server commands, file transfers, and remote compute on either server. Preserve existing jobs and task-specific execution permissions.
---

# Laptop SSH to 111 or 185

Use Mike's laptop as the SSH origin. This is a transport recipe, not an extra approval or agent-identity gate. It applies to Dot and its delegated workers as well as a user-authorized laptop session.

## Route

1. Use the already connected laptop when runtime context or a successful local command establishes that commands execute there. If necessary, discover and attach `Michaels-Laptop.local` through available environment tools. Do not require a particular tool name, a second independent attachment, or proof of a special Dot identity when the actual laptop execution context is already established. If the current runtime cannot execute on the laptop, hand the task to the existing authorized laptop coordinator or report that specific access blocker. Do not substitute a cloud SSH origin.
2. Use the requested server: `mikers@192.168.0.111` or `mikers@192.168.0.185`. Resolve the destination from the user's task or existing assignment, not by silently switching servers after a failure.
3. Run the laptop's system client directly:

```bash
/usr/bin/ssh -o BatchMode=yes -o ConnectTimeout=10 -o ConnectionAttempts=1 \
  -o ServerAliveInterval=15 -o ServerAliveCountMax=3 \
  -o StrictHostKeyChecking=yes mikers@192.168.0.185 'hostname; id -un'
```

Use `.111` instead when that is the assigned destination. Verify the known host key, remote hostname and account before production work. Keep an explicitly requested single read-only command's scope instead of appending unrelated commands. Use direct `scp` or `rsync -e` with equivalent SSH options for authorized transfers; compare byte counts and hashes where custody matters.

## Retries and recovery

- Retry transient connection failures at most three total attempts, with short backoff (for example 2 then 5 seconds). This includes a pre-connection `Operation not permitted` only when the tool has not denied the action and the output establishes that no remote command executed. Keep the same laptop, destination and authorized operation.
- Stop on authentication failure, unknown/changed host key, explicit policy or approval denial, or another identified security restriction. Do not disable host-key checks, alter credentials/network/security settings, tunnel, proxy, or change origin to work around it.
- A dropped connection after a command may have started is **not** permission to replay it. Reconnect read-only to inspect the existing process, job ID, receipts and outputs first. Resume monitoring rather than duplicate a job. Retry a mutation only when known not to have executed or independently idempotent and still authorized.
- After bounded retries, report the actual failure, attempt count and whether remote execution is absent or uncertain. Do not label blocked work successful or clear its blocker. No indefinite retry loop.

## Remote work

Connection permission is not blanket permission to launch, stop or change jobs. Follow the user's task scope and the repository's applicable source, review, resource and scientific gates. Reuse the existing coordinator/owner and check current processes before launch. Preserve live jobs, accepted results and unrelated work; do not reuse spent grants or silently extend resource caps. For long jobs, use the project's existing durable supervisor/session and monitor it across SSH reconnects.

Report transport and task outcomes separately: connected, connection failed before execution, or execution outcome uncertain. A successful SSH command does not establish a completed experiment. Do not change other skills, saved instructions, settings or schedules as a side effect of using this transport recipe.
