#!/usr/bin/env python3
"""List public Sentio SQL tables and columns for a project."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_BASE_URL = "https://dash.sentio.xyz/api/v1"
DEFAULT_USER_AGENT = "curl/8.7.1"


def request_json(url: str, api_key: str | None, timeout: int, user_agent: str) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
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


def parse_project_id(payload: dict[str, Any]) -> str:
    project = payload.get("project")
    if isinstance(project, dict):
        value = project.get("id")
        if isinstance(value, str) and value:
            return value
    value = payload.get("id")
    if isinstance(value, str) and value:
        return value
    raise RuntimeError("Could not find project id in project response")


def parse_latest_version(payload: dict[str, Any]) -> int:
    versions = payload.get("versions")
    if not isinstance(versions, list) or not versions:
        raise RuntimeError("No versions found in versions response")

    max_version: int | None = None
    for item in versions:
        if not isinstance(item, dict):
            continue
        raw_version = item.get("version")
        if isinstance(raw_version, int):
            value = raw_version
        elif isinstance(raw_version, str) and raw_version.isdigit():
            value = int(raw_version)
        else:
            continue
        if max_version is None or value > max_version:
            max_version = value

    if max_version is None:
        raise RuntimeError("Could not parse latest version from versions response")
    return max_version


def summarize_tables(tables: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for table_name in sorted(tables.keys()):
        table_info = tables.get(table_name, {})
        columns = {}
        if isinstance(table_info, dict):
            raw_columns = table_info.get("columns", {})
            if isinstance(raw_columns, dict):
                for col_name, col in sorted(raw_columns.items()):
                    if isinstance(col, dict):
                        columns[col_name] = {
                            "columnType": col.get("columnType"),
                            "clickhouseDataType": col.get("clickhouseDataType"),
                            "isBuiltin": col.get("isBuiltin"),
                        }
        out.append(
            {
                "name": table_name,
                "tableType": table_info.get("tableType") if isinstance(table_info, dict) else None,
                "relatedProjectId": (
                    table_info.get("relatedProjectId") if isinstance(table_info, dict) else None
                ),
                "columns": columns,
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Sentio public SQL tables by calling project -> versions -> tables APIs."
        )
    )
    parser.add_argument("--owner", default="sui", help="Sentio owner/org slug (default: sui)")
    parser.add_argument("--project", default="main", help="Sentio project slug (default: main)")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base API URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--include-dash",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include Dash tables in result (default: true)",
    )
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    parser.add_argument(
        "--api-key",
        default=os.getenv("SENTIO_API_KEY", ""),
        help="Sentio API key (or set SENTIO_API_KEY)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw tables API response instead of normalized output",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=f"HTTP User-Agent header (default: {DEFAULT_USER_AGENT})",
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    api_key = args.api_key or None

    project_url = f"{base}/project/{urllib.parse.quote(args.owner)}/{urllib.parse.quote(args.project)}"
    project_payload = request_json(project_url, api_key, args.timeout, args.user_agent)
    project_id = parse_project_id(project_payload)

    versions_url = f"{base}/processors/{urllib.parse.quote(project_id)}/versions?"
    versions_payload = request_json(versions_url, api_key, args.timeout, args.user_agent)
    latest_version = parse_latest_version(versions_payload)

    table_params = urllib.parse.urlencode(
        {
            "projectId": project_id,
            "version": str(latest_version),
            "includeDash": "true" if args.include_dash else "false",
        }
    )
    tables_url = (
        f"{base}/analytics/{urllib.parse.quote(args.owner)}/"
        f"{urllib.parse.quote(args.project)}/sql/tables?{table_params}"
    )
    tables_payload = request_json(tables_url, api_key, args.timeout, args.user_agent)

    if args.raw:
        print(json.dumps(tables_payload, indent=2))
        return 0

    raw_tables = tables_payload.get("tables", {})
    if not isinstance(raw_tables, dict):
        raise RuntimeError("Expected 'tables' object in tables API response")

    output = {
        "owner": args.owner,
        "project": args.project,
        "projectId": project_id,
        "latestVersion": latest_version,
        "tableCount": len(raw_tables),
        "tables": summarize_tables(raw_tables),
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
    except RuntimeError as err:
        print(f"error: {err}", file=sys.stderr)
        raise SystemExit(1)
