# Mission Brief 02 — GitHub Enrichment (`pilot/fetch_github.py`)

**Context:** Read `AGENTS.md` first. ~46% of registry servers link a GitHub repo; the registry metadata holds only the server-level description — the real poisoning surface (tool descriptions) lives in source.

**Goal:** For every GitHub-linked server in `data/servers.jsonl`, fetch public source artifacts that reveal tool definitions.

**Tasks**
1. Create `pilot/fetch_github.py` (stdlib + requests; unauthenticated first — respect rate limits, ~1 req/s, retry with backoff; document the unauth request cap and stop cleanly at it).
2. Per repo fetch, when present: `README.md`; `package.json` / `pyproject.toml`; then grep the default-branch tree (via the GitHub API) for tool-registration blocks: `@mcp.tool`, `server.tool(`, `FastMCP`, `ListToolsResult`, `"description":` near tool names. Extract up to 20 tool descriptions per repo.
3. Output `data/github_tools.jsonl`: `{server_name, repo, tool_name, tool_description, source_file, extraction_confidence}`.
4. Append a section to `data/collection_report.md`: repos reached, repos with ≥1 tool extracted, median tools/repo.

**Acceptance criteria**
- [ ] ≥60% of GitHub-linked repos yield ≥1 tool description, or a documented analysis of why not
- [ ] Tool descriptions now flow through `pilot/analyze.py` (extend it: scan `data/github_tools.jsonl` too, keep server-level and tool-level results as separate rows with a `level` column)

**Don'ts**
- Don't clone/execute repos; raw file read only
- Don't use a GitHub token unless the human provides one interactively (print instructions, never accept it in code)
