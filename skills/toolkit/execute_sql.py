#!/usr/bin/env python3
"""Execute Sentio SQL via REST API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_BASE_URL = "https://api.sentio.xyz/v1"
DEFAULT_USER_AGENT = "curl/8.7.1"


def post_json(
    url: str,
    payload: dict[str, Any],
    api_key: str | None,
    timeout: int,
    user_agent: str,
) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
    )
    req.add_header("content-type", "application/json")
    req.add_header("accept", "application/json")
    req.add_header("user-agent", user_agent)
    if api_key:
        req.add_header("api-key", api_key)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {err.code} for {url}: {body}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Network error for {url}: {err.reason}") from err


def load_sql(sql_arg: str | None, sql_file: str | None) -> str:
    if sql_arg and sql_file:
        raise RuntimeError("Use only one of --sql or --sql-file")
    if sql_arg:
        return sql_arg
    if sql_file:
        with open(sql_file, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    raise RuntimeError("Provide --sql or --sql-file")


def collect_pages(
    endpoint: str,
    sql: str,
    size: int | None,
    fetch_all: bool,
    max_pages: int,
    api_key: str | None,
    timeout: int,
    user_agent: str,
) -> dict[str, Any]:
    initial_query: dict[str, Any] = {"sql": sql}
    if size is not None:
        initial_query["size"] = size

    payload = {"sqlQuery": initial_query}
    first = post_json(endpoint, payload, api_key, timeout, user_agent)
    if "error" in first and first["error"]:
        raise RuntimeError(f"SQL execution failed: {first['error']}")

    first_result = first.get("result")
    if not isinstance(first_result, dict):
        raise RuntimeError("Missing 'result' in SQL response")

    columns = first_result.get("columns", [])
    column_types = first_result.get("columnTypes", {})
    all_rows = list(first_result.get("rows", []))
    generated_at = first_result.get("generatedAt")
    cursor = first_result.get("cursor") or ""
    pages = 1

    if fetch_all:
        while cursor:
            if pages >= max_pages:
                raise RuntimeError(
                    f"Stopped at {max_pages} pages. Increase --max-pages to continue."
                )
            page_payload = {"cursor": cursor}
            page = post_json(endpoint, page_payload, api_key, timeout, user_agent)
            if "error" in page and page["error"]:
                raise RuntimeError(f"Cursor page failed: {page['error']}")
            page_result = page.get("result")
            if not isinstance(page_result, dict):
                raise RuntimeError("Missing 'result' in cursor page response")
            page_rows = page_result.get("rows", [])
            if isinstance(page_rows, list):
                all_rows.extend(page_rows)
            cursor = page_result.get("cursor") or ""
            pages += 1

    return {
        "columns": columns,
        "columnTypes": column_types,
        "rows": all_rows,
        "rowCount": len(all_rows),
        "generatedAt": generated_at,
        "runtimeCost": first.get("runtimeCost"),
        "computeStats": first.get("computeStats"),
        "pagesFetched": pages,
        "hasMore": bool(cursor),
        "nextCursor": cursor or None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute SQL against Sentio Data API.")
    parser.add_argument("--owner", default="sui", help="Sentio owner/org slug (default: sui)")
    parser.add_argument("--project", default="main", help="Sentio project slug (default: main)")
    parser.add_argument("--sql", help="SQL text to execute")
    parser.add_argument("--sql-file", help="Path to file containing SQL")
    parser.add_argument("--size", type=int, default=None, help="Page size for SQL query")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Fetch all pages using cursor pagination",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=20,
        help="Maximum pages to fetch when --all is set (default: 20)",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base API URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds")
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=f"HTTP User-Agent header (default: {DEFAULT_USER_AGENT})",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("SENTIO_API_KEY", ""),
        help="Sentio API key (or set SENTIO_API_KEY)",
    )
    args = parser.parse_args()

    sql = load_sql(args.sql, args.sql_file)
    api_key = args.api_key or None
    endpoint = (
        f"{args.base_url.rstrip('/')}/analytics/{urllib.parse.quote(args.owner)}/"
        f"{urllib.parse.quote(args.project)}/sql/execute"
    )

    result = collect_pages(
        endpoint=endpoint,
        sql=sql,
        size=args.size,
        fetch_all=args.all,
        max_pages=args.max_pages,
        api_key=api_key,
        timeout=args.timeout,
        user_agent=args.user_agent,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
    except RuntimeError as err:
        print(f"error: {err}", file=sys.stderr)
        raise SystemExit(1)
