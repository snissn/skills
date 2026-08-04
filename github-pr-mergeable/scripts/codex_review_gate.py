#!/usr/bin/env python3
"""Classify the Codex review gate for one GitHub pull request.

Codex emits clean results as issue comments and findings as pull-request
reviews with inline threads. This helper inventories both surfaces, enforces
exact-head retry limits, and stops cross-head PR-lifetime review churn.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from typing import Any


DEFAULT_CODEX_LOGINS = {"chatgpt-codex-connector"}
REVIEWED_COMMIT_RE = re.compile(
    r"reviewed\s+commit[^0-9a-f]{0,20}([0-9a-f]{7,40})\b", re.IGNORECASE
)
CLEAN_RE = re.compile(
    r"(?:did(?:n't| not)\s+find\s+any(?:\s+major)?\s+issues|"
    r"no(?:\s+major)?\s+issues(?:\s+were)?\s+found)",
    re.IGNORECASE,
)
SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b", re.IGNORECASE)
REQUEST_RE = re.compile(r"^\s*@codex\s+review(?:\s|$)", re.IGNORECASE | re.MULTILINE)


def _normalized_login(login: str) -> str:
    value = login.lower()
    return value[:-5] if value.endswith("[bot]") else value


def _login(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("login") or "")
    return str(value or "")


def _is_codex_login(login: str, configured: set[str]) -> bool:
    return _normalized_login(login) in configured


def _head_matches(head: str, candidate: str | None) -> bool:
    if not candidate:
        return False
    candidate = candidate.lower()
    return len(candidate) >= 7 and head.lower().startswith(candidate)


def _reviewed_commit(body: str) -> str | None:
    match = REVIEWED_COMMIT_RE.search(body or "")
    return match.group(1).lower() if match else None


def _parse_time(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def _artifact(kind: str, timestamp: str, url: str, body: str, state: str = "") -> dict[str, Any]:
    return {
        "kind": kind,
        "timestamp": timestamp,
        "url": url,
        "state": state,
        "summary": (body or "").splitlines()[0][:200],
    }


def _is_clean_review(review: dict[str, Any]) -> bool:
    return (review.get("state") or "").upper() == "APPROVED" or bool(CLEAN_RE.search(review.get("body", "")))


def _request_artifact(comment: dict[str, Any]) -> dict[str, str]:
    return {
        "timestamp": comment.get("created_at", ""),
        "url": comment.get("html_url", ""),
    }


def classify(
    data: dict[str, Any],
    *,
    codex_logins: set[str] | None = None,
    retry_after_minutes: int = 10,
    max_requests: int = 3,
    max_total_requests: int = 6,
    max_finding_heads: int = 3,
    allow_after_churn: bool = False,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    configured = {_normalized_login(value) for value in (codex_logins or DEFAULT_CODEX_LOGINS)}
    head = data["head"].lower()
    head_time = _parse_time(data.get("head_commit_at"))
    now = now or dt.datetime.now(dt.timezone.utc)

    exact_artifacts: list[dict[str, Any]] = []
    clean_artifacts: list[dict[str, Any]] = []

    for comment in data.get("comments", []):
        login = _login(comment.get("user"))
        if not _is_codex_login(login, configured):
            continue
        body = comment.get("body", "")
        if not _head_matches(head, _reviewed_commit(body)):
            continue
        kind = "clean_comment" if CLEAN_RE.search(body) else "codex_comment"
        item = _artifact(kind, comment.get("created_at", ""), comment.get("html_url", ""), body)
        exact_artifacts.append(item)
        if kind == "clean_comment":
            clean_artifacts.append(item)

    for review in data.get("reviews", []):
        login = _login(review.get("user"))
        if not _is_codex_login(login, configured):
            continue
        body = review.get("body", "")
        commit = review.get("commit_id") or _reviewed_commit(body)
        if not _head_matches(head, commit):
            continue
        state = (review.get("state") or "").upper()
        clean = _is_clean_review(review)
        kind = "clean_review" if clean else "findings_review"
        item = _artifact(kind, review.get("submitted_at", ""), review.get("html_url", ""), body, state)
        exact_artifacts.append(item)
        if clean:
            clean_artifacts.append(item)

    exact_artifacts.sort(key=lambda item: item["timestamp"])
    clean_artifacts.sort(key=lambda item: item["timestamp"])

    all_requests = [
        _request_artifact(comment)
        for comment in data.get("comments", [])
        if REQUEST_RE.search(comment.get("body") or "")
        and not _is_codex_login(_login(comment.get("user")), configured)
    ]
    all_requests.sort(key=lambda item: item["timestamp"])
    finding_heads = {
        str(review.get("commit_id") or _reviewed_commit(review.get("body", ""))).lower()
        for review in data.get("reviews", [])
        if _is_codex_login(_login(review.get("user")), configured)
        and not _is_clean_review(review)
        and (review.get("commit_id") or _reviewed_commit(review.get("body", "")))
    }
    total_codex_threads = 0

    unresolved_threads = []
    for thread in data.get("threads", []):
        thread_comments = thread.get("comments") or []
        if isinstance(thread_comments, dict):
            thread_comments = thread_comments.get("nodes") or []
        codex_comments = [
            comment
            for comment in thread_comments
            if isinstance(comment, dict)
            and _is_codex_login(_login(comment.get("author")), configured)
        ]
        if not codex_comments:
            continue
        total_codex_threads += 1
        if not thread.get("isResolved"):
            unresolved_threads.append(
                {
                    "id": thread.get("id", ""),
                    "urls": [comment.get("url", "") for comment in codex_comments],
                    "summaries": [
                        (comment.get("body") or "").splitlines()[0][:200]
                        for comment in codex_comments
                    ],
                }
            )

    requests = []
    for comment in data.get("comments", []):
        body = comment.get("body", "")
        if not REQUEST_RE.search(body):
            continue
        if _is_codex_login(_login(comment.get("user")), configured):
            continue
        explicit_match = any(_head_matches(head, value) for value in SHA_RE.findall(body))
        created = _parse_time(comment.get("created_at"))
        if explicit_match or (created and head_time and created >= head_time):
            requests.append(_request_artifact(comment))
    requests.sort(key=lambda item: item["timestamp"])

    latest = exact_artifacts[-1] if exact_artifacts else None
    latest_clean = clean_artifacts[-1] if clean_artifacts else None
    request_count = len(requests)
    latest_request = requests[-1] if requests else None
    churn_reasons = []
    if max_total_requests > 0 and len(all_requests) >= max_total_requests:
        churn_reasons.append(f"total review requests {len(all_requests)} reached limit {max_total_requests}")
    if max_finding_heads > 0 and len(finding_heads) >= max_finding_heads:
        churn_reasons.append(f"finding-bearing heads {len(finding_heads)} reached limit {max_finding_heads}")
    churn_exhausted = bool(churn_reasons)

    if unresolved_threads:
        state = "findings"
        clean = False
        should_request = False
        action = (
            "resolve or disposition current findings, then stop for an architecture/scope reset; do not request another review"
            if churn_exhausted and not allow_after_churn
            else "resolve every Codex finding before requesting another review"
        )
    elif latest and latest["kind"] in {"clean_comment", "clean_review"}:
        state = "clean"
        clean = True
        should_request = False
        action = "stop requesting Codex reviews for this head"
    elif churn_exhausted and not allow_after_churn:
        state = "review_churn_blocked"
        clean = False
        should_request = False
        action = "stop review requests; perform a claim/architecture/scope reset and obtain explicit approval before resuming"
    elif latest:
        state = "resolved_findings"
        clean = False
        should_request = request_count < max_requests
        action = (
            "request one fresh review for this unchanged head"
            if should_request
            else "record Codex unavailable for this head; do not spam more requests"
        )
    elif requests:
        latest_request_time = _parse_time(latest_request["timestamp"] if latest_request else None)
        age_minutes = (
            (now - latest_request_time).total_seconds() / 60
            if latest_request_time
            else 0
        )
        exhausted = request_count >= max_requests
        state = "pending_exhausted" if exhausted else "pending"
        clean = False
        should_request = not exhausted and age_minutes >= retry_after_minutes
        action = (
            "record Codex unavailable for this head; do not spam more requests"
            if exhausted
            else (
                "one bounded retry is allowed"
                if should_request
                else "wait for the existing request; do not post another trigger"
            )
        )
    else:
        state = "not_requested"
        clean = False
        should_request = True
        action = "request one Codex review after the mature-head gate passes"

    return {
        "head": head,
        "state": state,
        "clean": clean,
        "should_request": should_request,
        "action": action,
        "latest_artifact": latest,
        "latest_clean_artifact": latest_clean,
        "exact_head_artifact_count": len(exact_artifacts),
        "request_count_for_head": request_count,
        "total_request_count": len(all_requests),
        "finding_head_count": len(finding_heads),
        "total_codex_thread_count": total_codex_threads,
        "review_churn_exhausted": churn_exhausted,
        "review_churn_reasons": churn_reasons,
        "review_churn_override_applied": churn_exhausted and allow_after_churn,
        "review_churn_limits": {
            "max_total_requests": max_total_requests,
            "max_finding_heads": max_finding_heads,
        },
        "latest_request": latest_request,
        "unresolved_codex_threads": unresolved_threads,
    }


def _gh_json(args: list[str]) -> Any:
    process = subprocess.run(
        ["gh", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or "gh command failed")
    return json.loads(process.stdout)


def _rest_pages(endpoint: str) -> list[dict[str, Any]]:
    pages = _gh_json(["api", "--paginate", "--slurp", endpoint])
    return [item for page in pages for item in page]


def _review_threads(owner: str, name: str, number: int) -> list[dict[str, Any]]:
    query = """
query($owner:String!,$name:String!,$number:Int!,$after:String){
  repository(owner:$owner,name:$name){pullRequest(number:$number){
    reviewThreads(first:100,after:$after){
      nodes{id isResolved comments(first:100){nodes{author{login} body url}}}
      pageInfo{hasNextPage endCursor}
    }
  }}
}"""
    threads: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        args = [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"number={number}",
        ]
        if after:
            args.extend(["-F", f"after={after}"])
        payload = _gh_json(args)
        page = payload["data"]["repository"]["pullRequest"]["reviewThreads"]
        threads.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return threads
        after = page["pageInfo"]["endCursor"]


def fetch_live(repo: str, number: int) -> dict[str, Any]:
    owner, name = repo.split("/", 1)
    pull = _gh_json(["api", f"repos/{repo}/pulls/{number}"])
    head = pull["head"]["sha"]
    commit = _gh_json(["api", f"repos/{repo}/commits/{head}"])
    commit_info = commit.get("commit", {})
    head_commit_at = (
        (commit_info.get("committer") or {}).get("date")
        or (commit_info.get("author") or {}).get("date")
    )
    return {
        "head": head,
        "head_commit_at": head_commit_at,
        "comments": _rest_pages(f"repos/{repo}/issues/{number}/comments?per_page=100"),
        "reviews": _rest_pages(f"repos/{repo}/pulls/{number}/reviews?per_page=100"),
        "threads": _review_threads(owner, name, number),
    }


def _fixture(
    *,
    head: str,
    comments: list[dict[str, Any]] | None = None,
    reviews: list[dict[str, Any]] | None = None,
    threads: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "head": head,
        "head_commit_at": "2026-01-01T00:00:00Z",
        "comments": comments or [],
        "reviews": reviews or [],
        "threads": threads or [],
    }


def self_test() -> None:
    head = "a" * 40
    bot = {"login": "chatgpt-codex-connector[bot]"}
    owner = {"login": "owner"}
    clean_body = "Codex Review: Didn't find any major issues.\n\n**Reviewed commit:** `aaaaaaaaaa`"
    trigger = {"user": owner, "body": f"@codex review exact head {head}", "created_at": "2026-01-01T00:06:00Z", "html_url": "trigger"}
    clean_comment = {"user": bot, "body": clean_body, "created_at": "2026-01-01T00:05:00Z", "html_url": "clean"}

    result = classify(_fixture(head=head, comments=[clean_comment, trigger]))
    assert result["state"] == "clean" and not result["should_request"]

    finding_review = {"user": bot, "body": "Codex Review suggestions", "commit_id": head, "state": "COMMENTED", "submitted_at": "2026-01-01T00:10:00Z", "html_url": "review"}
    unresolved = {"id": "thread", "isResolved": False, "comments": {"nodes": [{"author": bot, "body": "P1", "url": "finding"}]}}
    result = classify(_fixture(head=head, comments=[clean_comment], reviews=[finding_review], threads=[unresolved]))
    assert result["state"] == "findings" and not result["clean"]

    resolved = {**unresolved, "isResolved": True}
    later_clean = {**clean_comment, "created_at": "2026-01-01T00:15:00Z", "html_url": "later-clean"}
    result = classify(_fixture(head=head, comments=[later_clean], reviews=[finding_review], threads=[resolved]))
    assert result["state"] == "clean"

    approved = {**finding_review, "state": "APPROVED"}
    result = classify(_fixture(head=head, reviews=[approved]))
    assert result["state"] == "clean"

    stale = {**clean_comment, "body": clean_body.replace("aaaaaaaaaa", "bbbbbbbbbb")}
    result = classify(_fixture(head=head, comments=[stale, trigger]), now=dt.datetime(2026, 1, 1, 0, 7, tzinfo=dt.timezone.utc))
    assert result["state"] == "pending" and not result["should_request"]

    requests = [
        {**trigger, "created_at": f"2026-01-01T00:0{index}:00Z", "html_url": f"trigger-{index}"}
        for index in range(1, 4)
    ]
    result = classify(_fixture(head=head, comments=requests), now=dt.datetime(2026, 1, 1, 1, 0, tzinfo=dt.timezone.utc))
    assert result["state"] == "pending_exhausted" and not result["should_request"]

    historical_requests = [
        {**trigger, "body": "@codex review", "created_at": f"2025-12-0{index}T00:00:00Z", "html_url": f"historical-{index}"}
        for index in range(1, 4)
    ]
    historical_reviews = [
        {**finding_review, "commit_id": character * 40, "submitted_at": f"2025-12-0{index}T01:00:00Z"}
        for index, character in enumerate(("b", "c", "d"), start=1)
    ]
    churn_fixture = _fixture(head=head, comments=historical_requests, reviews=historical_reviews)
    result = classify(churn_fixture)
    assert result["state"] == "review_churn_blocked" and not result["should_request"]
    assert result["finding_head_count"] == 3 and result["total_request_count"] == 3

    result = classify(churn_fixture, allow_after_churn=True)
    assert result["state"] == "not_requested" and result["should_request"]
    assert result["review_churn_override_applied"]

    request_only_churn = _fixture(
        head=head,
        comments=[
            *[
                {**trigger, "body": "@codex review", "created_at": f"2025-11-0{index}T00:00:00Z", "html_url": f"request-only-{index}"}
                for index in range(1, 7)
            ],
            {**trigger, "body": "Do not type @codex review again.", "created_at": "2025-11-07T00:00:00Z", "html_url": "quoted-trigger"},
        ],
    )
    result = classify(request_only_churn)
    assert result["state"] == "review_churn_blocked"
    assert result["total_request_count"] == 6
    assert result["review_churn_reasons"] == ["total review requests 6 reached limit 6"]

    result = classify(churn_fixture, max_finding_heads=2)
    assert result["review_churn_limits"]["max_finding_heads"] == 2
    assert result["state"] == "review_churn_blocked"

    churn_with_clean = _fixture(head=head, comments=[*historical_requests, clean_comment], reviews=historical_reviews)
    result = classify(churn_with_clean)
    assert result["state"] == "clean" and result["review_churn_exhausted"]

    print("codex_review_gate self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="GitHub repository as owner/name")
    parser.add_argument("--pr", type=int, help="pull request number")
    parser.add_argument("--codex-login", action="append", default=[])
    parser.add_argument("--retry-after-minutes", type=int, default=10)
    parser.add_argument("--max-requests", type=int, default=3, help="maximum requests attributed to one exact head")
    parser.add_argument("--max-total-requests", type=int, default=6, help="PR-lifetime review-request churn limit; 0 disables")
    parser.add_argument("--max-finding-heads", type=int, default=3, help="PR-lifetime finding-bearing-head churn limit; 0 disables")
    parser.add_argument(
        "--allow-after-churn",
        action="store_true",
        help="override the lifetime churn stop only after explicit user/repository authorization",
    )
    parser.add_argument("--check", action="store_true", help="exit 2 unless the review gate is clean")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if not args.repo or not args.pr:
        parser.error("--repo and --pr are required unless --self-test is used")

    configured = DEFAULT_CODEX_LOGINS | set(args.codex_login)
    try:
        result = classify(
            fetch_live(args.repo, args.pr),
            codex_logins=configured,
            retry_after_minutes=args.retry_after_minutes,
            max_requests=args.max_requests,
            max_total_requests=args.max_total_requests,
            max_finding_heads=args.max_finding_heads,
            allow_after_churn=args.allow_after_churn,
        )
    except (AttributeError, KeyError, RuntimeError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"state": "error", "error": str(error)}, indent=2))
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["clean"] or not args.check else 2


if __name__ == "__main__":
    sys.exit(main())
