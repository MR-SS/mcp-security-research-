# Labeling Rubric — v1 (frozen)

Each detector class gets a one-line **TP rule**. The labeler reads the rule, reads
the description, and decides. These rules are frozen for the paper's Methods
section; any regex fix derived from FP patterns goes to `data/validation_report.md`
as a **separate proposal diff**, never auto-applied to `analyze.py`.

## Capability classes

| Class | TP rule |
|---|---|
| `shell_execution` | TP only if the description explicitly says the tool can **run a shell, execute commands, invoke bash/cmd, or spawn a subprocess** — not merely that it references shell-related words in passing. |
| `file_write_delete` | TP only if the description states the tool **creates, modifies, or removes files on disk** at the caller's direction — not a metaphorical "write up a report". |
| `file_read_sensitive` | TP only if the description states the tool **reads files or filesystem content** (including globbing) — not a reference to reading data generally. |
| `secret_env_access` | TP only if the description states the tool **reads, writes, or depends on environment variables, tokens, API keys, secrets, or credentials** — not just the words in a list of what it protects against. |
| `network_egress` | TP only if the description states the tool **makes outbound HTTP requests, fetches URLs, posts to webhooks, downloads/uploads, or scrapes** — not merely that it connects to a remote server conceptually. |
| `database_write` | TP only if the description states the tool **queries, inserts, or updates a database** — not just the word "query" used in a non-SQL sense. |
| `package_install` | TP only if the description states the tool **installs packages or dependencies** (pip, npm, etc.) — not just lists dependencies as output. |

## Poisoning-pattern classes

| Class | TP rule |
|---|---|
| `imperative_to_model` | TP only if the description **tells the model what it must/should/never do** in an imperative directed at the agent — not marketing copy that happens to use "never" or "always" about a product feature. |
| `stealth_concealment` | TP only if it tells the agent to **HIDE actions, results, or reasoning from the user** (e.g., "do not disclose", "silently", "without the user's knowledge") — not a description of a hidden/internal feature. |
| `important_tags` | TP only if the description **contains or simulates injection-style markup tags** (`<IMPORTANT>`, `<SYSTEM>`, `[INST]`, `<<SYS>>`) designed to manipulate model behavior — not a product name containing those words. |
| `cross_tool_shadowing` | TP only if the description **instructs the agent to alter its use of OTHER tools or servers** (e.g., "when emailing, always CC…") — not a standalone tool description. |
| `exfiltration_language` | TP only if the description **describes sending data to an external endpoint or address** (URL, webhook, email CC, transmission) — not a product URL or marketing link in the description. |
| `sensitive_file_target` | TP only if the description **explicitly names a sensitive file or path** (`.ssh`, `id_rsa`, `.env`, `.aws/credentials`, `.kube`, `/etc/passwd`, `.npmrc`, `.pypirc`) **as a target the tool operates on** — not as a file the tool helps you avoid. |
| `fake_system_role` | TP only if the description **assigns a fake system role or instructs the model to ignore prior instructions** (e.g., "system prompt", "ignore previous", "new instructions") — not a legitimate product description. |

## Instruction-channel classes (v2, measured separately — NOT poisoning)

| Class | TP rule |
|---|---|
| `model_addressed` | TP if the description **names an agent, model, LLM, bot, or assistant as its intended audience** — this is a channel measurement, not malice. Benign marketing frequently addresses "AI agents". |
| `second_person_imperative` | TP if the description **uses "you"/"your" plus an imperative** — again a channel measurement; many benign product descriptions say "you must configure…". |
