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
QUOTA_RE = re.compile(
    r"(?:reached your Codex usage limits for code reviews|"
    r"code review (?:usage )?(?:quota|limit)(?: has been)? (?:reached|exceeded|exhausted))",
    re.IGNORECASE,
)
REVIEW_STATE_RE = re.compile(r"<!--\s*codex-review-state:v1\s+(.*?)\s*-->", re.DOTALL)


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


def _structured_code_review(body: str) -> dict[str, Any] | None:
    """Read only the code-review state; ambiguous/incomplete states prove no pass."""
    markers = REVIEW_STATE_RE.findall(body)
    if len(markers) != 1:
        return None
    try:
        payload = json.loads(markers[0])
    except (TypeError, ValueError):
        return None
    code = payload.get("code_review") if isinstance(payload, dict) else None
    if not isinstance(code, dict):
        return None
    commit = code.get("commit_sha")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        return None
    status = code.get("status")
    any_findings = code.get("has_any_findings")
    unresolved = code.get("has_unresolved_findings")
    if status in {"running", "failed"}:
        if any(value is not None and type(value) is not bool for value in (any_findings, unresolved)):
            return None
        if unresolved is True and any_findings is not True:
            return None
    elif status == "completed":
        if type(any_findings) is not bool or type(unresolved) is not bool:
            return None
        if unresolved and not any_findings:
            return None
    else:
        return None
    return {**code, "commit_sha": commit.lower()}


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
    max_total_requests: int = 0,
    max_finding_heads: int = 0,
    warn_total_requests: int = 6,
    warn_finding_heads: int = 3,
    allow_after_churn: bool = False,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    configured = {_normalized_login(value) for value in (codex_logins or DEFAULT_CODEX_LOGINS)}
    head = data["head"].lower()
    head_time = _parse_time(data.get("head_commit_at"))
    now = now or dt.datetime.now(dt.timezone.utc)

    exact_artifacts: list[dict[str, Any]] = []
    clean_artifacts: list[dict[str, Any]] = []
    structured_finding_heads: set[str] = set()

    for comment in data.get("comments", []):
        login = _login(comment.get("user"))
        if not _is_codex_login(login, configured):
            continue
        body = comment.get("body", "")
        if "codex-review-state:v1" in body:
            # A structured summary must not fall back to prose (which can
            # describe a security review, stale head, or malformed state).
            code = _structured_code_review(body)
            if code and code["status"] == "completed" and code["has_any_findings"]:
                structured_finding_heads.add(code["commit_sha"])
            if not code or code["commit_sha"] != head:
                continue
            if code["status"] == "failed":
                kind = "failed_comment"
            elif code.get("has_unresolved_findings") is True:
                kind = "findings_comment"
            elif code["status"] == "running":
                kind = "running_comment"
            elif code["has_any_findings"]:
                kind = "findings_comment"
            else:
                kind = "clean_comment"
            item = _artifact(kind, comment.get("updated_at") or comment.get("created_at", ""),
                             comment.get("html_url", ""), body, code["status"])
            item["has_unresolved_findings"] = code.get("has_unresolved_findings")
            exact_artifacts.append(item)
            if kind == "clean_comment":
                clean_artifacts.append(item)
            continue
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
    finding_heads = structured_finding_heads | {
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

    # Quota replies often omit a SHA. Attribute those only to a preceding
    # current-head request, never to a bot comment predating this head. An
    # explicit stale SHA must not be rescued by temporal attribution.
    for comment in data.get("comments", []):
        body = comment.get("body") or ""
        if not _is_codex_login(_login(comment.get("user")), configured) or not QUOTA_RE.search(body):
            continue
        if "codex-review-state:v1" in body:
            continue
        commit = _reviewed_commit(body)
        timestamp = comment.get("created_at", "")
        created = _parse_time(timestamp)
        bound = _head_matches(head, commit) if commit else bool(
            created and head_time and created >= head_time
            and any(request["timestamp"] <= timestamp for request in requests)
        )
        if bound:
            exact_artifacts.append(_artifact("quota_comment", timestamp,
                                             comment.get("html_url", ""), body, "quota_exhausted"))
    exact_artifacts.sort(key=lambda item: item["timestamp"])

    latest = exact_artifacts[-1] if exact_artifacts else None
    substantive = [item for item in exact_artifacts
                   if item["kind"] not in {"running_comment", "failed_comment", "quota_comment"}]
    latest_substantive = substantive[-1] if substantive else None
    running = [item for item in exact_artifacts if item["kind"] == "running_comment"]
    latest_running = running[-1] if running else None
    latest_clean = clean_artifacts[-1] if clean_artifacts else None
    request_count = len(requests)
    latest_request = requests[-1] if requests else None
    warning_reasons = []
    if warn_total_requests > 0 and len(all_requests) >= warn_total_requests:
        warning_reasons.append(f"total review requests {len(all_requests)} reached warning {warn_total_requests}")
    if warn_finding_heads > 0 and len(finding_heads) >= warn_finding_heads:
        warning_reasons.append(f"finding-bearing heads {len(finding_heads)} reached warning {warn_finding_heads}")
    churn_reasons = []
    if max_total_requests > 0 and len(all_requests) >= max_total_requests:
        churn_reasons.append(f"total review requests {len(all_requests)} reached hard limit {max_total_requests}")
    if max_finding_heads > 0 and len(finding_heads) >= max_finding_heads:
        churn_reasons.append(f"finding-bearing heads {len(finding_heads)} reached hard limit {max_finding_heads}")
    churn_exhausted = bool(churn_reasons)

    unavailable_artifacts = [item for item in exact_artifacts
                             if item["kind"] in {"failed_comment", "quota_comment"}]
    latest_unavailable = unavailable_artifacts[-1] if unavailable_artifacts else None
    hosted_unavailable = bool(latest_unavailable and (
        not latest_clean or latest_unavailable["timestamp"] > latest_clean["timestamp"]
    ) and (not latest_running or latest_unavailable["timestamp"] >= latest_running["timestamp"]))

    if unresolved_threads or (latest_substantive and latest_substantive.get("has_unresolved_findings") is True):
        state = "findings"
        clean = False
        should_request = False
        action = (
            "resolve or disposition current findings, then stop for an architecture/scope reset; do not request another review"
            if churn_exhausted and not allow_after_churn
            else "resolve every Codex finding before requesting another review"
        )
    elif latest_substantive and latest_substantive["kind"] in {"clean_comment", "clean_review"}:
        state = "clean"
        clean = True
        should_request = False
        action = "stop requesting Codex reviews for this head"
    elif hosted_unavailable:
        state = "unavailable"
        clean = False
        should_request = False
        action = "record hosted review failure/quota evidence and use the permitted exact-candidate internal fallback; no automatic waiver or retry"
    elif churn_exhausted and not allow_after_churn:
        state = "review_churn_blocked"
        clean = False
        should_request = False
        action = "stop review requests; perform a claim/architecture/scope reset and obtain explicit approval before resuming"
    elif latest_running and (not latest_substantive or latest_running["timestamp"] >= latest_substantive["timestamp"]):
        state = "pending"
        clean = False
        should_request = False
        action = "wait for the running exact-head code review; do not post another trigger"
    elif latest_substantive:
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

    if hosted_unavailable and state == "findings":
        action = "disposition every existing finding; record hosted failure/quota and use a permitted exact-candidate internal fallback, without automatic waiver or retry"

    return {
        "hosted_unavailable": hosted_unavailable,
        "latest_unavailable_artifact": latest_unavailable,
        "unavailable_artifacts": unavailable_artifacts,
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
        "review_churn_warning": bool(warning_reasons),
        "review_churn_warning_reasons": warning_reasons,
        "review_churn_exhausted": churn_exhausted,
        "review_churn_reasons": churn_reasons,
        "review_churn_override_applied": churn_exhausted and allow_after_churn,
        "review_churn_limits": {
            "max_total_requests": max_total_requests,
            "max_finding_heads": max_finding_heads,
            "warn_total_requests": warn_total_requests,
            "warn_finding_heads": warn_finding_heads,
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


def _rest_pages(endpoint: str, fetch: Any = None) -> list[dict[str, Any]]:
    """Fetch REST arrays explicitly; older gh releases lack --slurp."""
    fetch = fetch or _gh_json
    items: list[dict[str, Any]] = []
    page_number = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        page = fetch(["api", f"{endpoint}{separator}per_page=100&page={page_number}"])
        if not isinstance(page, list) or any(not isinstance(item, dict) for item in page):
            raise RuntimeError("GitHub REST pagination returned a non-object array")
        items.extend(page)
        if len(page) < 100:
            return items
        page_number += 1


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
        "comments": _rest_pages(f"repos/{repo}/issues/{number}/comments"),
        "reviews": _rest_pages(f"repos/{repo}/pulls/{number}/reviews"),
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
    assert result["state"] == "not_requested" and result["should_request"]
    assert result["review_churn_warning"] and not result["review_churn_exhausted"]
    assert result["finding_head_count"] == 3 and result["total_request_count"] == 3

    result = classify(churn_fixture, max_finding_heads=3)
    assert result["state"] == "review_churn_blocked" and not result["should_request"]
    assert result["review_churn_exhausted"]

    result = classify(churn_fixture, max_finding_heads=3, allow_after_churn=True)
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
    assert result["state"] == "not_requested" and result["should_request"]
    assert result["review_churn_warning"] and not result["review_churn_exhausted"]
    assert result["total_request_count"] == 6

    result = classify(request_only_churn, max_total_requests=6)
    assert result["state"] == "review_churn_blocked"
    assert result["review_churn_reasons"] == ["total review requests 6 reached hard limit 6"]

    result = classify(churn_fixture, max_finding_heads=2)
    assert result["review_churn_limits"]["max_finding_heads"] == 2
    assert result["state"] == "review_churn_blocked"

    churn_with_clean = _fixture(head=head, comments=[*historical_requests, clean_comment], reviews=historical_reviews)
    result = classify(churn_with_clean, max_finding_heads=3)
    assert result["state"] == "clean" and result["review_churn_exhausted"]

    def structured_comment(status: str, any_findings: Any = None,
                           unresolved_findings: Any = None, **overrides: Any) -> dict[str, Any]:
        code = dict(commit_sha=head, status=status, has_any_findings=any_findings,
                    has_unresolved_findings=unresolved_findings)
        code.update(overrides)
        payload = dict(code_review=code, security_review=dict(
            commit_sha=head, status="completed", has_any_findings=False,
            has_unresolved_findings=False))
        return dict(user=bot, created_at="2026-01-01T00:01:00Z",
                    updated_at="2026-01-01T00:20:00Z", html_url="structured",
                    body="<!-- codex-review-state:v1 " + json.dumps(payload) + " -->\nCodex Review Summary")

    running_comment = structured_comment("running")
    result = classify(_fixture(head=head, comments=[running_comment]))
    assert result["state"] == "pending" and not result["should_request"]
    assert result["exact_head_artifact_count"] == 1 and result["latest_artifact"]["kind"] == "running_comment"
    result = classify(_fixture(head=head, comments=[trigger, running_comment]),
                      now=dt.datetime(2026, 1, 1, 1, 0, tzinfo=dt.timezone.utc))
    assert result["state"] == "pending" and not result["should_request"]

    structured_clean = structured_comment("completed", False, False)
    result = classify(_fixture(head=head, comments=[structured_clean, trigger]))
    assert result["state"] == "clean" and not result["should_request"]
    result = classify(_fixture(head=head, comments=[structured_clean], threads=[unresolved]))
    assert result["state"] == "findings" and not result["should_request"]

    # Updated-at, not the summary's original creation time, orders completions.
    result = classify(_fixture(head=head, comments=[structured_clean], reviews=[finding_review]))
    assert result["state"] == "clean"
    later_running = {**running_comment, "updated_at": "2026-01-01T00:30:00Z"}
    result = classify(_fixture(head=head, comments=[structured_clean, later_running, trigger]))
    assert result["state"] == "clean" and not result["should_request"]
    result = classify(_fixture(head=head, comments=[clean_comment, later_running]))
    assert result["state"] == "clean" and not result["should_request"]
    running_findings = structured_comment("running", True, True)
    result = classify(_fixture(head=head, comments=[clean_comment, running_findings]))
    assert result["state"] == "findings" and not result["should_request"]
    assert result["latest_artifact"]["kind"] == "findings_comment"

    structured_findings = structured_comment("completed", True, True)
    result = classify(_fixture(head=head, comments=[clean_comment, structured_findings]))
    assert result["state"] == "findings" and not result["should_request"]
    assert result["finding_head_count"] == 1
    result = classify(_fixture(head=head, comments=[structured_comment("completed", True, False)]))
    assert result["state"] == "resolved_findings" and not result["clean"]
    result = classify(_fixture(head=head, comments=[structured_comment("completed", True, False), later_running]))
    assert result["state"] == "pending" and not result["should_request"]

    # Malformed, stale, non-bot and security-only summaries cannot prove a pass.
    ignored = [
        structured_comment("completed", False, False, commit_sha="b" * 40),
        structured_comment("completed", False, False, commit_sha="a" * 10),
        structured_comment("completed", 0, False),
        structured_comment("completed", False, None),
        structured_comment("completed", False, True),
        structured_comment("running", False, True),
        structured_comment("running", None, True),
        structured_comment("unknown", False, False),
        {**structured_clean, "user": owner},
        {**structured_clean, "body": '<!-- codex-review-state:v1 {bad json} -->'},
        {**structured_clean, "body": '<!-- codex-review-state:v1 {"security_review":{"status":"completed"}} -->'},
        {**structured_clean, "body": structured_clean["body"] * 2},
    ]
    for comment in ignored:
        # Misleading legacy prose must not rescue a structured summary.
        comment = {**comment, "body": comment["body"] + "\n" + clean_body}
        result = classify(_fixture(head=head, comments=[comment]))
        assert result["state"] == "not_requested" and not result["clean"]
    security_findings = json.loads(REVIEW_STATE_RE.search(structured_clean["body"]).group(1))
    security_findings["security_review"].update(has_any_findings=True, has_unresolved_findings=True)
    result = classify(_fixture(head=head, comments=[{**structured_clean, "body":
        "<!-- codex-review-state:v1 " + json.dumps(security_findings) + " -->"}]))
    assert result["state"] == "clean"

    # Failed summaries may retain generic finding flags: failure is no pass
    # and no proof of actual findings. Real prior findings/threads still block.
    failed = structured_comment("failed", True, True)
    result = classify(_fixture(head=head, comments=[trigger, failed]))
    assert result["state"] == "unavailable" and result["hosted_unavailable"]
    assert not result["clean"] and not result["should_request"]
    assert result["finding_head_count"] == 0
    result = classify(_fixture(head=head, comments=[failed], threads=[unresolved]))
    assert result["state"] == "findings" and result["hosted_unavailable"]
    result = classify(_fixture(head=head, comments=[structured_findings,
        {**failed, "updated_at": "2026-01-01T00:25:00Z"}]))
    assert result["state"] == "findings"
    result = classify(_fixture(head=head, comments=[structured_comment("failed", commit_sha="b" * 40)]))
    assert result["state"] == "not_requested" and not result["hosted_unavailable"]
    result = classify(_fixture(head=head, comments=[structured_comment("failed")]))
    assert result["state"] == "unavailable"

    quota = dict(user=bot, body="You have reached your Codex usage limits for code reviews.",
                 created_at="2026-01-01T00:21:00Z", html_url="quota")
    result = classify(_fixture(head=head, comments=[trigger, quota]))
    assert result["state"] == "unavailable" and not result["should_request"]
    assert result["latest_unavailable_artifact"]["url"] == "quota"
    for ignored_quota in [
        {**quota, "user": owner},
        {**quota, "created_at": "2025-12-31T00:00:00Z"},
        {**quota, "body": quota["body"] + "\nReviewed commit: " + "b" * 40},
    ]:
        result = classify(_fixture(head=head, comments=[trigger, ignored_quota]))
        assert not result["hosted_unavailable"]
    result = classify(_fixture(head=head, comments=[quota]))
    assert result["state"] == "not_requested" and not result["hosted_unavailable"]
    result = classify(_fixture(head=head, comments=[trigger, quota,
        {**structured_clean, "updated_at": "2026-01-01T00:25:00Z"}]))
    assert result["state"] == "clean" and not result["hosted_unavailable"]
    result = classify(_fixture(head=head, comments=[failed, quota, later_running, trigger]))
    assert result["state"] == "pending" and not result["should_request"]
    result = classify(_fixture(head=head, comments=[structured_clean, failed, quota, trigger]))
    assert result["state"] == "clean" and not result["should_request"]

    rest_calls: list[list[str]] = []
    first_page = [{"id": index} for index in range(100)]
    second_page = [{"id": 100}]

    def fake_rest(args: list[str]) -> Any:
        rest_calls.append(args)
        if args[-1].endswith("page=1"):
            return first_page
        if args[-1].endswith("page=2"):
            return second_page
        raise AssertionError(f"unexpected REST page: {args}")

    assert _rest_pages("repos/example/project/issues/1/comments", fake_rest) == [
        *first_page, *second_page,
    ]
    assert rest_calls == [
        ["api", "repos/example/project/issues/1/comments?per_page=100&page=1"],
        ["api", "repos/example/project/issues/1/comments?per_page=100&page=2"],
    ]

    print("codex_review_gate self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="GitHub repository as owner/name")
    parser.add_argument("--pr", type=int, help="pull request number")
    parser.add_argument("--codex-login", action="append", default=[])
    parser.add_argument("--retry-after-minutes", type=int, default=10)
    parser.add_argument("--max-requests", type=int, default=3, help="maximum requests attributed to one exact head")
    parser.add_argument("--max-total-requests", type=int, default=0, help="explicit PR-lifetime hard request cap; 0 disables")
    parser.add_argument("--max-finding-heads", type=int, default=0, help="explicit PR-lifetime hard finding-head cap; 0 disables")
    parser.add_argument("--warn-total-requests", type=int, default=6, help="advisory PR-lifetime request threshold; 0 disables")
    parser.add_argument("--warn-finding-heads", type=int, default=3, help="advisory PR-lifetime finding-head threshold; 0 disables")
    parser.add_argument(
        "--allow-after-churn",
        action="store_true",
        help="override an explicit hard lifetime cap only after user/repository authorization",
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
            warn_total_requests=args.warn_total_requests,
            warn_finding_heads=args.warn_finding_heads,
            allow_after_churn=args.allow_after_churn,
        )
    except (AttributeError, KeyError, RuntimeError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"state": "error", "error": str(error)}, indent=2))
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["clean"] or not args.check else 2


if __name__ == "__main__":
    sys.exit(main())
