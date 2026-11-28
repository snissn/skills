#!/usr/bin/env python3
"""Zero-dependency CLI client for treedb-repo-mcp over Streamable HTTP or Unix socket.

Safe by default: read-only tools work out of the box; mutating `sync_now` requires
explicit `--allow-write`.

Examples:
  mcp_call.py --url http://127.0.0.1:7337/mcp health
  mcp_call.py --url http://127.0.0.1:7337/mcp tools
  mcp_call.py --url http://127.0.0.1:7337/mcp call status
  mcp_call.py --url http://127.0.0.1:7337/mcp call phrase_search \
      --arg phrase="elastic electron" --arg collection=repo --arg top_k=5 --arg explain=true
  mcp_call.py --socket /path/to/daemon.sock call search_code --arg query="CHSH" --arg ext=md
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import socket
import sys
import urllib.parse
from typing import Any


WRITE_TOOLS = {"sync_now"}


class UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, socket_path: str, timeout: float = 30.0) -> None:
        super().__init__("unix", timeout=timeout)
        self._socket_path = socket_path

    def connect(self) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect(self._socket_path)
        self.sock = sock


def parse_scalar_or_json(raw: str) -> Any:
    """Parse JSON literals (bool, int, float, list, object, null); keep plain strings as str."""
    trimmed = raw.strip()
    if trimmed == "":
        return ""
    if trimmed in ("true", "false", "null") or trimmed[0] in "[{\"" or (
        trimmed[0] in "-0123456789"
    ):
        try:
            return json.loads(trimmed)
        except json.JSONDecodeError:
            pass
    return raw


def parse_args_kv(items: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"invalid --arg {item!r}: expected key=value")
        key, val = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"invalid --arg {item!r}: empty key")
        out[key] = parse_scalar_or_json(val)
    return out


def http_request(
    *,
    url: str | None,
    socket_path: str | None,
    method: str,
    path: str,
    body: bytes | None = None,
    timeout: float = 30.0,
) -> tuple[int, bytes]:
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"

    if socket_path:
        conn: http.client.HTTPConnection = UnixHTTPConnection(socket_path, timeout=timeout)
        target_path = path
    elif url:
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme == "https":
            conn = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, timeout=timeout)
        elif parsed.scheme == "http":
            conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=timeout)
        else:
            raise ValueError(f"unsupported URL scheme in {url!r}")
        base_path = parsed.path.rstrip("/")
        if path == "/mcp":
            target_path = parsed.path or "/mcp"
        else:
            if base_path.endswith("/mcp"):
                base_path = base_path[:-4]
            target_path = f"{base_path}{path}"
    else:
        raise ValueError("specify --url / TREEDB_MCP_URL or --socket / TREEDB_MCP_SOCKET")

    try:
        conn.request(method, target_path, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        return resp.status, data
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query a treedb-repo-mcp server over Streamable HTTP or Unix socket."
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("TREEDB_MCP_URL", ""),
        help="Streamable HTTP MCP URL (default: $TREEDB_MCP_URL, e.g. http://127.0.0.1:7337/mcp)",
    )
    parser.add_argument(
        "--socket",
        default=os.environ.get("TREEDB_MCP_SOCKET", ""),
        help="Daemon Unix domain socket path (default: $TREEDB_MCP_SOCKET)",
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="Request timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--raw", action="store_true", help="Print raw JSON-RPC response envelope instead of unwrapped tool payload"
    )
    parser.add_argument(
        "--allow-write",
        action="store_true",
        help="Explicitly permit mutating tools such as sync_now",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("health", help="GET /health")
    sub.add_parser("tools", help="List available MCP tools (tools/list)")

    call_p = sub.add_parser("call", help="Invoke an MCP tool (tools/call)")
    call_p.add_argument("tool", help="MCP tool name (e.g. status, search, search_code, phrase_search)")
    call_p.add_argument("--json", dest="json_args", default="", help="JSON object of tool arguments")
    call_p.add_argument(
        "--arg",
        action="append",
        default=[],
        help="Tool argument as key=value (repeatable; JSON literals auto-decoded)",
    )

    ns = parser.parse_args()
    url = ns.url.strip() or None
    sock = ns.socket.strip() or None
    if not url and not sock:
        print(
            "error: pass --url / TREEDB_MCP_URL or --socket / TREEDB_MCP_SOCKET",
            file=sys.stderr,
        )
        return 2

    try:
        if ns.cmd == "health":
            status, raw = http_request(
                url=url, socket_path=sock, method="GET", path="/health", timeout=ns.timeout
            )
            text = raw.decode("utf-8", errors="replace")
            if status != 200:
                print(f"error: GET /health returned HTTP {status}: {text}", file=sys.stderr)
                return 1
            try:
                print(json.dumps(json.loads(text), indent=2))
            except json.JSONDecodeError:
                print(text)
            return 0

        if ns.cmd == "tools":
            payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
            status, raw = http_request(
                url=url,
                socket_path=sock,
                method="POST",
                path="/mcp",
                body=json.dumps(payload).encode("utf-8"),
                timeout=ns.timeout,
            )
            if status != 200:
                print(f"error: HTTP {status}: {raw.decode('utf-8', errors='replace')}", file=sys.stderr)
                return 1
            env = json.loads(raw.decode("utf-8"))
            if "error" in env:
                print(json.dumps(env, indent=2), file=sys.stderr)
                return 1
            print(json.dumps(env if ns.raw else env.get("result", env), indent=2))
            return 0

        if ns.cmd == "call":
            if ns.tool in WRITE_TOOLS and not ns.allow_write:
                print(
                    f"error: tool {ns.tool!r} mutates daemon state; re-run with --allow-write to permit it",
                    file=sys.stderr,
                )
                return 2
            args: dict[str, Any] = {}
            if ns.json_args:
                loaded = json.loads(ns.json_args)
                if not isinstance(loaded, dict):
                    raise ValueError("--json must decode to a JSON object")
                args.update(loaded)
            if ns.arg:
                args.update(parse_args_kv(ns.arg))

            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": ns.tool, "arguments": args},
            }
            status, raw = http_request(
                url=url,
                socket_path=sock,
                method="POST",
                path="/mcp",
                body=json.dumps(payload).encode("utf-8"),
                timeout=ns.timeout,
            )
            if status != 200:
                print(f"error: HTTP {status}: {raw.decode('utf-8', errors='replace')}", file=sys.stderr)
                return 1
            env = json.loads(raw.decode("utf-8"))
            if ns.raw:
                print(json.dumps(env, indent=2))
                res = env.get("result")
                is_err = isinstance(res, dict) and bool(res.get("isError"))
                return 0 if ("error" not in env and not is_err) else 1
            if "error" in env:
                print(json.dumps(env["error"], indent=2), file=sys.stderr)
                return 1
            result = env.get("result", {})
            content = result.get("content") or []
            if content and isinstance(content, list) and "text" in content[0]:
                text = content[0]["text"]
                if result.get("isError"):
                    print(text, file=sys.stderr)
                    return 1
                try:
                    print(json.dumps(json.loads(text), indent=2))
                except json.JSONDecodeError:
                    print(text)
                return 0
            print(json.dumps(result, indent=2))
            return 0 if not result.get("isError") else 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
