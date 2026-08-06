# Skills repository policy

## Scientific portfolio skills

Any skill that opens, resumes, reviews, merges, or project-manages scientific
issues or pull requests must preserve these invariants:

1. read a repository-owned portfolio board when one exists;
2. enforce its active scientific and maintenance workstream limits;
3. use an explicit status taxonomy with blocked, parked, deferred, superseded,
   and completed states that do not authorize implementation;
4. keep one scientific identity and decision surface per PR by default;
5. prohibit workflow-generated scientific candidate revisions;
6. bind PR descriptions, manifests, review, CI, and merge to one exact head;
7. renew scientific review after every scientific edit;
8. continue review-fix work after the default repair round only for a
   claim-changing scientific or evidence-path finding; and
9. activate descendants only from merged positive predecessor authority.

Use `scientific-portfolio-governance` for portfolio reconciliation and compose
it with `scientific-mainline-workflow` and `gpt56-pro-issue-graph-executor` when
the target repository contains a scientific portfolio board or the user asks
for multi-lane scientific project management.

Do not add a second competing status schema to another skill. Repository-local
policy may narrow the default limits and statuses, and wins when it is stricter.
