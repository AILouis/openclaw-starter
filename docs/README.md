# OpenClaw Documentation

A complete reference guide for Louis's multi-agent AI system.

## What is OpenClaw?

OpenClaw is a multi-agent AI framework running on WSL2 that powers a team of four specialized agents. The system connects to Discord, runs automated market scans on cron schedules, maintains persistent memory across sessions, and backs up everything to GitHub daily. It is designed for a Greater China Rates Trading analyst who also walks the path of non-duality.

## The Team

| Agent | Emoji | Inspired By | Model | Role |
|-------|-------|-------------|-------|------|
| **Eve** | `n/a` | Oracle archetype | GPT-5.4 (primary) | Main agent. Second brain, strategist, builder, guide, guardian |
| **Jim** | `n/a` | Jim Simons | Claude Opus 4.6 | Quant. Backtesting, model building, data pipelines |
| **Jesse** | `n/a` | Jesse Livermore | Claude Sonnet 4.6 | Market scout. 24/7 automated Greater China rates intelligence |
| **Albert** | `n/a` | Albert Einstein | Claude Opus 4.6 | Researcher. Philosophy, macro analysis, deep research |

## Quick Start

1. Open Discord and go to the `general` channel
2. Message Eve directly — no mention needed, she reads everything in the server
3. Ask her to do things: research, run market data, delegate to Jim/Albert, check on Jesse
4. Use the dedicated `Jim` / `Albert` threads when you want direct persistent specialist collaboration
5. Watch `market-update-jesse` for automated market scans
6. Watch `agent-teams` for behind-the-scenes agent coordination

## Documentation

| File | Contents |
|------|----------|
| [01-architecture.md](01-architecture.md) | System architecture, how everything connects |
| [02-agents.md](02-agents.md) | Agent profiles: roles, personalities, skills, models |
| [03-discord-guide.md](03-discord-guide.md) | Discord channels, interaction tips, best practices |
| [04-scheduling.md](04-scheduling.md) | Cron jobs, heartbeat system, when agents work |
| [05-memory-system.md](05-memory-system.md) | Memory architecture, daily logs, compaction |
| [06-backup-and-recovery.md](06-backup-and-recovery.md) | Backup system, encryption, recovery procedures |
| [07-market-data.md](07-market-data.md) | Shared market data infrastructure |
| [08-troubleshooting.md](08-troubleshooting.md) | Common issues and how to fix them |
| [09-configuration-reference.md](09-configuration-reference.md) | All config files, env vars, file paths |
| [10-file-system-guide.md](10-file-system-guide.md) | File system layout, management guide, maintenance checklist |

## Recent Improvements (2026-03-25 through 2026-03-28)

### File System Cleanup Audit (2026-03-28)
- **Deleted 6 redundant/empty files** — TASKS.md (unused), 3 sub-agent TOOLS.md (negligible), Jesse HEARTBEAT.md (contradictory), DEGRADATION.md (merged)
- **Renamed PROTOCOLS.md -> REFERENCE.md** — consolidated group chat rules, project protocol, and failure playbook into one reference file
- **Moved 7 Jim work artifacts** to `jim-workspace/docs/` — separated work output from instruction files
- **Deduplicated Eve's AGENTS.md** — removed Execution Honesty block and team roster (both word-for-word copies of SHARED_RULES.md)
- **Trimmed all SOUL.md files** — removed motivational sections, compressed overlapping rules, stripped redundant identity content from IDENTITY.md
- **Trimmed SHARED_RULES.md** — removed agent-specific startup section (each agent's own AGENTS.md covers this), collapsed verbose sections
- **Added MEMORY.md size cap** — guideline of ~50 lines added to SHARED_RULES.md
- **Added file system management guide** — new `docs/10-file-system-guide.md` documents the complete file layout, loading behavior, and maintenance procedures
- **Result:** ~17% reduction in daily startup token cost (~17K-26K tokens/day saved). See `audits/2026-03-28-file-system-cleanup.md` for full details.

### Persistent Specialist Threads + Formatting Enforcement (2026-03-26)
- **Jim persistent thread** — Jim now runs as a long-lived Discord thread named `Jim`
- **Albert persistent thread** — Albert now runs as a long-lived Discord thread named `Albert`
- **Discord thread-bound subagent spawning** enabled via `channels.discord.threadBindings.spawnSubagentSessions`
- **Agent-teams formatting hardened** — every message now starts with `** **\n`, uses emoji prefixes, and uses `───` separators between debate phases for mobile readability
- **Jesse citation rules tightened** — web-sourced non-`market_data` data now requires source date and policy-event staleness checks

### System Audit v3 — Config Optimization + Agent-Teams Fix
- **Cron `errorBackoff`** — exponential backoff (30s to 1h) on all 6 cron jobs to prevent cascading failures during outages
- **Agent-teams delegation workflow** — restructured AGENTS.md to gate all delegations on agent-teams posting (post FIRST, then act). Added heartbeat safety net and compaction flush catch-up check. Fixes the issue where Eve skipped mirroring inter-agent work to the agent-teams Discord channel.
- **TEAM_STATE.md OOS fix** — corrected 3/5 to 4/5 (verified from Jim's execution log and HMM results)

### Post-Audit Compatibility Rollback (2026-03-25 evening)
- **Removed `heartbeat.isolatedSession`** after `openclaw doctor` flagged it as unsupported
- **Removed memory-lancedb hybrid retrieval block** (`retrieval.mode`, `vectorWeight`, `bm25Weight`, `rerank`) because the current plugin config no longer accepts those keys
- **Removed `subagents.archiveAfterMinutes`** after `openclaw doctor` / config validation flagged it as unsupported

### Jim Discipline Upgrade + lancedb Fix
- **Jim: Debugging Protocol** — 7-step investigate-before-fix workflow (inspired by gstack). Iron rule: no code changes until root cause confirmed
- **Jim: Completeness Principle** — full test coverage, all edge cases, proper error handling, no TODOs in shared codebases
- **Eve: delegation reminders** — reinforces Jim's new protocols when assigning work
- **Fixed memory-lancedb** — added required `embedding` config (openai-compatible, text-embedding-3-small), re-enabled plugin

### Performance Upgrade
- **Discord historyLimit** increased 15 → 50 for better conversation continuity
- **Compaction threshold** increased 40k → 100k tokens to retain more context in long sessions
- **memory-lancedb autoCapture** enabled with captureMaxChars 2000 for richer automatic memory
- **Debate depth** maxPingPongTurns stays at 5 (platform max; 8 was attempted but reverted)
- **Cleaned up** orphaned `~/.openclaw/agents/claude-opus-4-6/` directory

### System Audit v2
- **Shortened Jesse cron prompts** — reference JESSE.md instead of duplicating rules inline, saving ~2,100 tokens/day
- **Jesse reads TEAM_STATE.md** before every scan — enables crisis-mode threshold override (lower by ~30% when L3=RISK_OFF)
- **Fixed Albert's weekly cron** — now reads MEMORY.md for prioritized research queue, writes to `research/YYYY-MM-DD-topic.md`
- **Added subagent config** — maxSpawnDepth:2, maxConcurrent:8, runTimeoutSeconds:900 for cost/reliability guardrails
- **Added agentToAgent allowlist** — explicit `["main", "jim", "jesse", "albert"]` for security
- **Configured memory-lancedb** — autoRecall:true, autoCapture:true, captureMaxChars:2000
- **Created BOOT.md** for Eve — gateway restart recovery checklist
- **Created Albert's `research/` directory** — structured research output

### System Audit v1 (earlier)
- Enabled **memory-lancedb** plugin for semantic memory search across all agents
- Added **memory search protocol** to all AGENTS.md — agents now search prior context before non-trivial work
- Added **significant move threshold table** to Jesse's runbook — consistent alerting thresholds for all asset classes
- Added **structured debate synthesis template** — Eve produces actionable consensus/disagreement/recommendation format
- Populated **Albert's research queue** with 6 concrete topics aligned to Louis's interests
- Standardized **HEARTBEAT.md** across all sub-agents with actionable self-check lists
- Added **active narratives** from Jesse's scan-state to TEAM_STATE.md for team situational awareness
- Documented **agent-specific startup files** in SHARED_RULES.md
- Hardened **file permissions** under `~/.openclaw/` (700 dirs, 600 sensitive files)

## Key File Paths

```
~/.openclaw/                         # OpenClaw runtime home
~/.openclaw/openclaw.json            # Main configuration
~/.openclaw/.env                     # API keys (plaintext, local only)
~/.openclaw/workspace/               # Eve's workspace
  SOUL.md, AGENTS.md, IDENTITY.md    #   Auto-loaded every session
  TOOLS.md, REFERENCE.md             #   On-demand reference
  HEARTBEAT.md, BOOT.md              #   Loaded on heartbeat / restart
  MEMORY.md, memory/                 #   Curated + daily memory

/mnt/d/eve-projects/                 # All project workspaces
  USER.md                            #   Shared user profile (symlinked)
  SHARED_RULES.md                    #   Team-wide rules
  TEAM_STATE.md                      #   Regime, projects, decisions
  jim-workspace/                     #   Jim (SOUL, AGENTS, docs/)
  jesse-workspace/                   #   Jesse (SOUL, AGENTS, JESSE.md)
  albert-workspace/                  #   Albert (SOUL, AGENTS, research/)
  market-data/                       #   Shared market data library
  Market_Regime_Detection/           #   Regime detection project

~/openclaw-backup/                   # This repo
  backup.sh                          #   Backup script (daily cron)
  docs/                              #   System documentation
  audits/                            #   Change logs and audit reports
```

For a complete file-by-file reference, see [10-file-system-guide.md](docs/10-file-system-guide.md).
