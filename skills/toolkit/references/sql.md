# Sentio SQL Notes

## Data Studio workflow
- Open Data Studio and use the SQL editor to run queries.
- Use the schema panel to inspect available tables and columns.

## Running and managing queries
- Run a query with the Run button or Ctrl/Cmd + Enter.
- Results include status, execution time, and output.
- Use the action buttons to save a query, save a view, add to a dashboard, or create an endpoint.
- Use Endpoints to expose a saved query as an API.

## REST API flow
- Execute SQL endpoint:
`POST https://api.sentio.xyz/v1/analytics/{owner}/{project}/sql/execute`
- First request body:
`{"sqlQuery":{"sql":"SELECT ...","size":1000}}`
- Cursor request body:
`{"cursor":"<cursor-from-previous-response>"}`
- Add `api-key` header for authenticated/private usage.

## Table discovery flow (public tables)
- Get project:
`GET https://dash.sentio.xyz/api/v1/project/{owner}/{project}`
- Get versions by project id:
`GET https://dash.sentio.xyz/api/v1/processors/{projectId}/versions?`
- Get tables with latest version:
`GET https://dash.sentio.xyz/api/v1/analytics/{owner}/{project}/sql/tables?projectId={projectId}&version={latestVersion}&includeDash=true`

## Bundled scripts
- `scripts/list_public_tables.py`
Call the 3-step discovery flow and return tables with columns.
- `scripts/execute_sql.py`
Execute SQL and optionally fetch all pages with cursor pagination.

## Script usage
```bash
python scripts/list_public_tables.py --owner sui --project main
```

```bash
python scripts/execute_sql.py --owner sui --project main --sql "SELECT 1 AS x"
```

```bash
python scripts/execute_sql.py --owner sui --project main --sql "SELECT number FROM numbers(5)" --size 2 --all
```

## Notes
- Both scripts accept `--api-key` or `SENTIO_API_KEY`.
- Both scripts accept `--user-agent` if your environment requires a specific HTTP signature.
