# OpenClaw File System & Management Guide

A complete reference for the file structure of Louis's OpenClaw multi-agent system. Use this to understand what each file does, where it lives, and how to maintain the system.

## Directory Layout

```
~/.openclaw/                                   # OpenClaw runtime home
  openclaw.json                                # Master config (agents, channels, plugins, cron)
  .env                                         # API keys (DO NOT commit)
  workspace/                                   # Eve's workspace
    SOUL.md            [auto-loaded]           # Eve's identity, philosophy, promises
    AGENTS.md          [auto-loaded]           # Eve's operational rules, delegation checklist
    IDENTITY.md        [auto-loaded]           # Name + emoji (routing metadata)
    TOOLS.md           [on-demand]             # Discord channels, agent reach commands, paths
    HEARTBEAT.md       [on-heartbeat]          # Periodic check rotation
    BOOT.md            [on-restart]            # Gateway restart recovery (loaded by boot-md hook)
    REFERENCE.md       [on-demand]             # Group chat rules, project protocol, failure playbook
    MEMORY.md          [on-demand]             # Curated long-term memory
    USER.md -> /mnt/d/eve-projects/USER.md     # Symlink to shared user profile
    memory/                                    # Daily session logs
      YYYY-MM-DD.md                            # Raw session notes (auto-appended at compaction)
      heartbeat-state.json                     # Heartbeat rotation tracker
      archive/YYYY-MM/                         # Monthly archival (>30 day files)
    skills/                                    # Installed skills (github, notion, summarize)
  agents/                                      # Per-agent runtime state
    main/sessions/                             # Eve's session transcripts
    jim/sessions/                              # Jim's sessions
    jesse/sessions/                            # Jesse's sessions
    albert/sessions/                           # Albert's sessions
  cron/jobs.json                               # Scheduled job definitions
  memory/lancedb/                              # Semantic memory index (auto-managed)

/mnt/d/eve-projects/                           # Shared project root
  USER.md                                      # Louis's profile (single source of truth)
  SHARED_RULES.md                              # Team-wide rules (all agents read at startup)
  TEAM_STATE.md                                # Current regime, projects, infrastructure status

/mnt/d/eve-projects/jim-workspace/             # Jim's workspace
  SOUL.md            [auto-loaded]             # Jim Simons quant philosophy
  AGENTS.md          [auto-loaded]             # Operational rules, debugging protocol, local paths
  IDENTITY.md        [auto-loaded]             # Name + emoji
  HEARTBEAT.md       [on-heartbeat]            # Self-checks when spawned
  MEMORY.md          [on-demand]               # Curated long-term memory
  USER.md -> /mnt/d/eve-projects/USER.md       # Symlink
  memory/                                      # Daily logs
  docs/                                        # Work artifacts (code audits, design docs, reviews)

/mnt/d/eve-projects/jesse-workspace/           # Jesse's workspace
  SOUL.md            [auto-loaded]             # Jesse Livermore tape reader philosophy
  AGENTS.md          [auto-loaded]             # Pre/post scan procedures
  IDENTITY.md        [auto-loaded]             # Name + emoji
  JESSE.md           [on-demand, every scan]   # Operational runbook (thresholds, format, schedule)
  MEMORY.md          [on-demand]               # Operational lessons (rare)
  USER.md -> /mnt/d/eve-projects/USER.md       # Symlink
  scan-state.json                              # Live scan state (dedup, rates, narratives)
  memory/                                      # Operational logs

/mnt/d/eve-projects/albert-workspace/          # Albert's workspace
  SOUL.md            [auto-loaded]             # Einstein research philosophy
  AGENTS.md          [auto-loaded]             # Operational rules, local notes
  IDENTITY.md        [auto-loaded]             # Name + emoji
  HEARTBEAT.md       [on-heartbeat]            # Research checklist
  MEMORY.md          [on-demand]               # Research queue
  USER.md -> /mnt/d/eve-projects/USER.md       # Symlink
  memory/                                      # Daily logs
  research/                                    # Research output files
```

## File Loading Behavior

OpenClaw loads files in three ways:

| Loading Mode | When | Files |
|-------------|------|-------|
| **Auto-loaded** | Every session/turn | SOUL.md, AGENTS.md, IDENTITY.md |
| **Hook-loaded** | On specific events | HEARTBEAT.md (heartbeat cycle), BOOT.md (gateway restart) |
| **On-demand** | Agent reads explicitly | TOOLS.md, MEMORY.md, USER.md, TEAM_STATE.md, REFERENCE.md, JESSE.md |

**Token cost implication:** Auto-loaded files burn tokens on every turn. Keep them lean. On-demand files only cost when read.

## File Responsibilities

| Responsibility | File | Scope |
|---------------|------|-------|
| Agent personality & decision framework | SOUL.md | Per-agent |
| Operational rules & protocols | AGENTS.md | Per-agent (references SHARED_RULES.md) |
| Routing metadata (name, emoji) | IDENTITY.md | Per-agent |
| Team-wide rules, startup sequence, red lines | SHARED_RULES.md | Global |
| User profile & preferences | USER.md | Global (symlinked) |
| Regime state, active projects, infrastructure | TEAM_STATE.md | Global (Eve maintains) |
| Discord channels, agent commands, paths | TOOLS.md | Eve only |
| Group chat behavior, project protocol, failures | REFERENCE.md | Eve only |
| Periodic health checks | HEARTBEAT.md | Eve, Jim, Albert |
| Gateway restart recovery | BOOT.md | Eve only |
| Curated long-term memory | MEMORY.md | Per-agent |
| Daily session notes | memory/YYYY-MM-DD.md | Per-agent |
| Jesse scan operations, format, thresholds | JESSE.md | Jesse only |
| Jesse dedup state, rates snapshot | scan-state.json | Jesse only |

## Shared vs Per-Agent Rules

### Shared (in SHARED_RULES.md)
- Session startup sequence
- Memory system rules
- Red lines (no data exfiltration, trash > rm)
- External vs internal action rules
- Execution honesty rules
- Platform formatting (Discord)
- Team roster and shared paths

### Per-Agent (in each AGENTS.md)
- Agent-specific startup additions
- Memory search protocol (specialized per role)
- Role-specific operational rules
- Debate mode behavior
- Local paths and environment notes

**Rule:** If a rule applies to all agents, it goes in SHARED_RULES.md. If it's specific to one agent's workflow, it stays in that agent's AGENTS.md.

## Memory Architecture

Three tiers, from automatic to curated:

```
Tier 1: LanceDB        (automatic, noisy)    -- semantic search across all conversations
Tier 2: memory/*.md     (per-session, raw)    -- daily logs appended at compaction
Tier 3: MEMORY.md       (curated, distilled)  -- key facts, preferences, project state
```

**Guidelines:**
- MEMORY.md should stay under ~50 lines. Prune as it grows.
- Daily logs have no cap but are archived monthly (>30 days -> memory/archive/YYYY-MM/).
- Jesse uses scan-state.json instead of daily logs. MEMORY.md is for rare operational lessons only.
- Work artifacts (code reviews, design docs) go in `docs/` or `research/`, not memory.

## Adding a New Agent

1. Create workspace directory: `/mnt/d/eve-projects/<name>-workspace/`
2. Create required files: `SOUL.md`, `AGENTS.md`, `IDENTITY.md`, `MEMORY.md`
3. Create `memory/` directory
4. Symlink USER.md: `ln -s /mnt/d/eve-projects/USER.md <workspace>/USER.md`
5. Add agent to `openclaw.json` (`agents.list` array)
6. Add routing rule to `openclaw.json` (`bindings` array) if Discord-driven
7. Have the agent's AGENTS.md reference SHARED_RULES.md for team rules
8. Optional: add HEARTBEAT.md if the agent needs periodic checks

## Maintenance Checklist

### Weekly
- Check TEAM_STATE.md is current
- Verify Jesse's scan-state.json isn't accumulating junk (>100 reported_items)

### Monthly
- Archive daily memory files >30 days old (move to `memory/archive/YYYY-MM/`)
- Review MEMORY.md files -- prune stale entries, distill daily logs
- Check disk space (`df -h /home/clawl1nux && df -h /mnt/d`)

### When Editing Instruction Files
- **Auto-loaded files** (SOUL.md, AGENTS.md, IDENTITY.md): Changes take effect next session. Every line costs tokens.
- **On-demand files**: Changes take effect when the agent next reads the file.
- **SHARED_RULES.md**: Affects all agents. Test with one agent first.
- **openclaw.json**: Requires gateway restart to take effect.

## Key Conventions

1. **Single source of truth.** If info exists in SHARED_RULES.md, don't duplicate it in AGENTS.md.
2. **Symlinks for shared files.** USER.md is symlinked, not copied. Edit the source at `/mnt/d/eve-projects/USER.md`.
3. **Work output != instruction files.** Code reviews, design docs, and research go in `docs/` or `research/`, not alongside SOUL.md.
4. **BOOT.md must keep its filename.** The `boot-md` hook loads it by name.
5. **Token economy.** Smaller auto-loaded files = cheaper sessions. Put reference material in on-demand files.
