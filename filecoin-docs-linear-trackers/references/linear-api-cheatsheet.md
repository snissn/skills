# Linear API Cheatsheet

Use these snippets when a current Linear connector is unavailable, deprecated,
or failing. Prefer the connector when it works. The legacy Linear app may emit
internal MCP errors; in that case, direct GraphQL with `LINEAR_API_KEY` or
`LINEAR_TOKEN` is an acceptable fallback for this workflow.

Set a token without printing it:

```sh
TOKEN="${LINEAR_API_KEY:-$LINEAR_TOKEN}"
test -n "$TOKEN"
```

## Query One Issue By Identifier

```sh
curl -sS https://api.linear.app/graphql \
  -H "Authorization: $TOKEN" \
  -H 'Content-Type: application/json' \
  --data @- <<'JSON' | jq .
{
  "query": "query($id:String!){ issue(id:$id){ id identifier title description url priorityLabel updatedAt state { id name type } team { id key name states { nodes { id name type } } } parent { id identifier title url } children { nodes { id identifier title url state { name type } } } } }",
  "variables": { "id": "GER-1035" }
}
JSON
```

## Query Several Issues

The identifier lookup is reliable enough to loop over known GER IDs:

```sh
for id in GER-1034 GER-1035 GER-1114; do
  curl -sS https://api.linear.app/graphql \
    -H "Authorization: $TOKEN" \
    -H 'Content-Type: application/json' \
    --data "{\"query\":\"query { issue(id: \\\"$id\\\") { identifier title state { name type } priorityLabel url updatedAt } }\"}" |
    jq -r 'if .data.issue then [.data.issue.identifier,.data.issue.state.name,.data.issue.state.type,.data.issue.priorityLabel,.data.issue.title] | @tsv else "ERR\t" + ((.errors // [])|map(.message)|join("; ")) end'
done
```

If the issue body contains many child IDs, avoid noisy full-text search. Query
the known identifiers directly or inspect parent/child relationships.

## Find State IDs For An Issue Team

Do this before moving an issue. Choose state IDs by name and team, never by
memory.

```sh
curl -sS https://api.linear.app/graphql \
  -H "Authorization: $TOKEN" \
  -H 'Content-Type: application/json' \
  --data @- <<'JSON' | jq -r '.data.issue.team.states.nodes[] | [.id,.name,.type] | @tsv'
{
  "query": "query($id:String!){ issue(id:$id){ team { states { nodes { id name type } } } } }",
  "variables": { "id": "GER-1035" }
}
JSON
```

## Move An Issue To A State

Replace `STATE_ID` with the ID discovered from the team states query.

```sh
curl -sS https://api.linear.app/graphql \
  -H "Authorization: $TOKEN" \
  -H 'Content-Type: application/json' \
  --data @- <<'JSON' | jq .
{
  "query": "mutation($id:String!,$input:IssueUpdateInput!){ issueUpdate(id:$id,input:$input){ success issue { identifier state { name type } url } } }",
  "variables": {
    "id": "GER-1035",
    "input": { "stateId": "STATE_ID" }
  }
}
JSON
```

## Comment With PR And Validation Evidence

Keep comments concise and factual. Include PR URL, branch/base, validation, and
the intended next state. Do not mention Codex, ChatGPT, OpenAI, AI-generated
work, agents, bots, or tool provenance unless the user explicitly asks for that
disclosure or repo policy requires it.

```sh
curl -sS https://api.linear.app/graphql \
  -H "Authorization: $TOKEN" \
  -H 'Content-Type: application/json' \
  --data @- <<'JSON' | jq .
{
  "query": "mutation($input:CommentCreateInput!){ commentCreate(input:$input){ success comment { id url body } } }",
  "variables": {
    "input": {
      "issueId": "LINEAR_INTERNAL_ISSUE_ID",
      "body": "Opened ready-for-review PR: https://github.com/filecoin-project/filecoin-docs/pull/2471\n\nBase: filecoin-project/main\nHead: FIL-Builders:mikers/ger-1035-retrieval-upstream-main\n\nValidation:\n- npx markdownlint-cli2 <touched files>: pass\n- npm run build: pass\n- GitHub linkChecker: pass\n\nNext: review/merge before closing."
    }
  }
}
JSON
```

Use the internal `issue.id` from the query response for `issueId`, not the
human-readable `GER-####` identifier.

## Create A Child Issue

First query the parent issue to get its internal `id` and `team.id`.

```sh
curl -sS https://api.linear.app/graphql \
  -H "Authorization: $TOKEN" \
  -H 'Content-Type: application/json' \
  --data @- <<'JSON' | jq .
{
  "query": "mutation($input:IssueCreateInput!){ issueCreate(input:$input){ success issue { id identifier title url parent { identifier } } } }",
  "variables": {
    "input": {
      "teamId": "TEAM_ID",
      "parentId": "PARENT_ISSUE_INTERNAL_ID",
      "title": "New section to create - Store on Filecoin",
      "description": "TRACKER_BODY_MARKDOWN",
      "priority": 2
    }
  }
}
JSON
```

Linear priority values are numeric in the API. Query existing issues and avoid
changing priority unless the user asked for it or the source tracker makes it
clear.

## Filecoin Docs PR Commands

Verify remotes:

```sh
git remote -v
git fetch filecoin-project main
```

Create a branch from upstream main:

```sh
git switch -c mikers/ger-1114-store-on-filecoin-upstream-main filecoin-project/main
```

Branch names for this workflow must always begin with `mikers/`. Do not use
`codex/`, `ai/`, `agent/`, `bot/`, or generated-work markers in branch names.

Push to the fork remote and open a ready-for-review PR:

```sh
git push -u origin HEAD
gh pr create \
  --repo filecoin-project/filecoin-docs \
  --base main \
  --head FIL-Builders:mikers/ger-1114-store-on-filecoin-upstream-main \
  --title "Add Store on Filecoin section" \
  --body-file /tmp/filecoin-docs-pr.md
```

Inspect PR state before updating Linear:

```sh
gh pr view <number> \
  --repo filecoin-project/filecoin-docs \
  --json number,title,state,isDraft,mergeStateStatus,statusCheckRollup,reviewDecision,url,headRefName,baseRefName
```

Use `--draft` only when the user asked for a draft PR. For this workstream, a
ready-for-review PR is the default after approval.

Before creating the PR or commenting on Linear, audit drafted public text:

```sh
rg -n -i '\b(codex|chatgpt|openai|ai-generated|generated by|authored by an ai|ai agent|agent-generated|bot-generated|co-authored-by:.*(codex|chatgpt|openai|bot))\b' \
  /tmp/filecoin-docs-pr.md \
  /tmp/filecoin-docs-linear-comment.md \
  /tmp/filecoin-docs-commit-message.txt
```

The audit should return no matches unless the user explicitly approved a
disclosure.
