# Mission Brief 05 — Paper Draft Skeleton (`paper/`)

**Context:** Read `AGENTS.md` and `PLAN.md` §6. Data/results sections stay EMPTY until Briefs 01–04 land; this brief builds structure and prose that doesn't depend on numbers.

**Goal:** A compilable ACM-style LaTeX skeleton with Intro, Background, Methods (draft), Related Work, Ethics written; Findings/Experiments stubbed with tables marked `<<PENDING: brief-04>>`.

**Tasks**
1. `paper/main.tex` (acmart, 8–10 pp target), `paper/refs.bib` with verified entries: Greshake 2302.12173, InjecAgent 2403.02691, AgentDojo 2406.13352, ToolEmu 2309.15817, MCPTox 2508.14925, MSB 2510.15994, MCPSecBench 2508.13220, MCP-TDP 2605.24069, OWASP Agentic Top 10 (genai.owasp.org), MCP spec — **verify each ID/URL by fetching before adding; drop anything unverifiable and note it**.
2. Write Intro (ecosystem growth + 3 motivating examples *from confirmed labels only*, else generic), Background (MCP + threat model + taxonomy from AGENTS.md §4.3), Methods (collection → detectors → validation protocol → ethics), Related Work (benchmarks vs. our measurement delta), Ethics & Disclosure.
3. Placeholder macro `\pending{}` for all numbers; a `paper/TODO.md` listing exactly which artifact populates each number.

**Acceptance criteria**
- [ ] Compiles clean (pdflatex or tectonic) with zero undefined refs
- [ ] Every number placeholder traceable to a producing artifact via TODO.md
- [ ] No invented stats/citations anywhere

**Don'ts**
- Don't write Findings prose before Brief 03 data exists
- Don't claim "first" for anything without a one-line justification citing the closest prior work
