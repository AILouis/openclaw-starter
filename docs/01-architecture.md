# System Architecture

## High-Level Overview

```
                    Discord Server
                    ┌─────────────────────────────────┐
                    │  #general          (Louis + Eve) │
Louis ◄────────────►│  #market-update-jesse  (Jesse)   │
                    │  #agent-teams      (delegation)  │
                    └──────────────┬──────────────────┘
                                   │
                         Discord Bot Token
                                   │
                    ┌──────────────▼──────────────────┐
                    │    OpenClaw Gateway              │
                    │    (systemd, port 18789,         │
                    │     loopback only)               │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │           EVE (main)             │
                    │     GPT-5.4 primary              │
                    │     Opus 4.6 / Sonnet 4.6       │
                    │     fallbacks                    │
                    └──┬──────────┬──────────┬────────┘
                       │          │          │
            ┌──────────▼┐  ┌─────▼──────┐  ┌▼──────────┐
            │    JIM     │  │   JESSE    │  │  ALBERT   │
            │  Opus 4.6  │  │ Sonnet 4.6 │  │ Opus 4.6  │
            │  on-demand │  │ cron-based │  │ on-demand │
            └────────────┘  └────────────┘  └───────────┘
```

## How the Gateway Works

The OpenClaw gateway is a Node.js process managed by systemd:

- **Binary:** `/usr/lib/node_modules/openclaw/dist/index.js gateway`
- **Port:** 18789 (loopback only — not exposed to network)
- **Auth:** Token-based (`OPENCLAW_GATEWAY_TOKEN` from .env)
- **Service file:** `~/.config/systemd/user/openclaw-gateway.service`
- **Restart policy:** Always restart, 5-second delay between restarts

The gateway handles:
- Discord bot connection and message routing
- Cron job scheduling and execution
- Agent session management
- Heartbeat polling
- Memory embedding and search

## Model Assignments

| Agent | Primary Model | Fallbacks | Why |
|-------|--------------|-----------|-----|
| Eve (main) | `openai-codex/gpt-5.4` | Opus 4.6, Sonnet 4.6 | Best general reasoning for orchestration |
| Jim | `anthropic/claude-opus-4-6` | — | Deep reasoning needed for quant work |
| Jesse | `anthropic/claude-sonnet-4-6` | — | Fast enough for scans, cost-effective at high volume |
| Albert | `anthropic/claude-opus-4-6` | — | Deep reasoning needed for research |
| Heartbeat | `anthropic/claude-haiku-4-5` | — | Lightweight, cheap for periodic checks |

**Fallback chain:** If Eve's primary model (GPT-5.4) is unavailable, she falls back to Opus 4.6, then Sonnet 4.6. Eve will tell you immediately when a model switch happens. Jim, Jesse, and Albert currently run on their configured Anthropic primary models without per-agent fallback entries.

## Session Management

- **Scope:** `per-channel-peer` — each Discord channel maintains its own session
- **Agent-to-agent:** Max 5 ping-pong turns per exchange (`maxPingPongTurns: 5`) — platform enforced limit
- **Compaction:** Auto-triggered at ~100k tokens. Before compacting, Eve saves durable notes to `memory/YYYY-MM-DD.md`
- **Cron sessions:** Isolated — Jesse's cron jobs run in their own sessions, not Eve's

## Agent-to-Agent Communication

Eve coordinates the team using OpenClaw's built-in agent communication:

- **`sessions_spawn`** — Start a new agent session (used for one-shot work and to create persistent thread-bound sessions)
- **`sessions_send`** — Send messages to an existing agent session (used for debates and ongoing work in persistent Jim/Albert threads)
- **`REPLY_SKIP`** — An agent sends this when it has nothing more to add in a debate

An explicit allowlist restricts which agents can communicate: `["main", "jim", "jesse", "albert"]`.

Jim and Albert now have dedicated persistent Discord threads (`Jim`, `Albert`) for direct long-lived collaboration, while still reporting through Eve for orchestration and synthesis.

Jesse runs independently on cron. Eve monitors Jesse's health during heartbeats.

### Sub-Agent Configuration

Controls spawning behavior when Eve delegates tasks to Jim and Albert:

| Setting | Value | Purpose |
|---------|-------|---------|
| `model` | `anthropic/claude-sonnet-4-6` | Default model for sub-agents |
| `runTimeoutSeconds` | `900` | 15-minute timeout per sub-agent run |
| `maxSpawnDepth` | `2` | Max nesting depth for agent spawning |
| `maxChildrenPerAgent` | `5` | Max active children per parent agent |
| `maxConcurrent` | `8` | Global concurrent sub-agent limit |

## File System Layout

### OpenClaw Runtime (`~/.openclaw/`)

```
.openclaw/
├── openclaw.json           # Main configuration
├── .env                    # API keys (plaintext, 600 perms)
├── workspace/              # Eve's workspace
│   ├── SOUL.md             # Eve's identity and philosophy
│   ├── IDENTITY.md         # Name, emoji, creature type
│   ├── USER.md → /mnt/d/eve-projects/USER.md  # Symlink to shared user profile
│   ├── AGENTS.md           # Agent rules, debate protocol (refs SHARED_RULES.md)
│   ├── TOOLS.md            # Local config: channels, subagents, file paths
│   ├── TASKS.md            # Louis's task list
│   ├── MEMORY.md           # Curated long-term memory
│   ├── HEARTBEAT.md        # Periodic check checklist
│   ├── DEGRADATION.md      # Failure response playbook
│   ├── PROTOCOLS.md        # Group chat, reactions, heartbeat guide
│   ├── BOOT.md             # Gateway restart recovery checklist
│   └── memory/             # Daily memory logs (YYYY-MM-DD.md)
├── cron/
│   ├── jobs.json           # Cron job definitions
│   └── runs/               # Execution logs (*.jsonl)
├── agents/                 # Agent-specific auth and model configs
│   ├── main/
│   ├── jim/
│   ├── jesse/
│   └── albert/
├── memory/                 # Embedded memory DB (main.sqlite)
├── credentials/            # Discord/Telegram auth
├── devices/                # Device pairing state
├── identity/               # Device identity and auth
├── delivery-queue/         # Message delivery tracking
└── logs/                   # Config audit logs
```

### Project Workspaces (`/mnt/d/eve-projects/`)

```
eve-projects/
├── USER.md                   # Shared user profile (symlinked into all workspaces)
├── SHARED_RULES.md           # Common team rules (referenced by all AGENTS.md)
├── TEAM_STATE.md             # Shared team context (regime, active projects)
├── market-data/              # Shared market data library (all agents use this)
├── Market_Regime_Detection/  # Main regime detection project
├── jim-workspace/            # Jim's files (SOUL.md, research notes)
│   ├── USER.md → ../USER.md  # Symlink to shared user profile
│   └── memory/               # Daily logs (YYYY-MM-DD.md)
├── jesse-workspace/          # Jesse's files (SOUL.md, scan-state.json)
│   ├── USER.md → ../USER.md  # Symlink to shared user profile
│   └── memory/               # Daily logs (YYYY-MM-DD.md)
└── albert-workspace/         # Albert's files (SOUL.md, research output)
    ├── USER.md → ../USER.md  # Symlink to shared user profile
    └── memory/               # Daily logs (YYYY-MM-DD.md)
```

### Backup (`~/openclaw-backup/`)

```
openclaw-backup/
├── backup.sh               # Backup script (rsync + git + age encryption)
├── docs/                   # This documentation
├── openclaw-config/        # Mirror of ~/.openclaw/ config files
├── shared/                 # TEAM_STATE.md, USER.md, SHARED_RULES.md
├── eve-workspace/          # Mirror of Eve's workspace
├── jim-workspace/          # Mirror of Jim's workspace
├── jesse-workspace/        # Mirror of Jesse's workspace
├── albert-workspace/       # Mirror of Albert's workspace
└── env.age                 # Encrypted .env file
```

## How Workspace Files Connect

Each agent reads its workspace files on session startup:

1. **SOUL.md** — Who the agent is (identity, philosophy, rules)
2. **USER.md** — Who Louis is (symlink to `/mnt/d/eve-projects/USER.md` in all workspaces)
3. **IDENTITY.md** — Name, emoji, creature type
4. **memory/YYYY-MM-DD.md** — Recent daily logs (today + yesterday)
5. **MEMORY.md** — Curated long-term memory (main sessions only, for security)

Eve additionally reads:
- **AGENTS.md** — Team coordination rules, debate protocol (references `/mnt/d/eve-projects/SHARED_RULES.md` for common rules)
- **TOOLS.md** — Local config: Discord channels, subagent details, file paths
- **TASKS.md** — Louis's task list
- **HEARTBEAT.md** — Periodic check checklist
- **DEGRADATION.md** — Failure response playbook
- **PROTOCOLS.md** — Group chat, reactions, heartbeat guide

## Auth Profiles

Three API providers are configured:

| Profile | Provider | Mode | Used For |
|---------|----------|------|----------|
| `anthropic:cctoken-ll` | Anthropic | Token | Jim, Jesse, Albert, Eve fallback |
| `openai:default` | OpenAI | API Key | Memory embeddings only |
| `openai-codex:default` | OpenAI Codex | OAuth | Eve's primary model (GPT-5.4) |

## Internal Hooks

Enabled hooks in `openclaw.json`:

- **boot-md** — Loads workspace markdown files on session start
- **bootstrap-extra-files** — Loads additional bootstrap files
- **command-logger** — Logs commands for audit
- **session-memory** — Manages session memory persistence
- **memory-lancedb** — Semantic memory search via LanceDB vector store (enabled 2026-03-25)

## Memory Search Protocol

All agents follow a "memory search before work" protocol: on receiving a task, agents query the LanceDB semantic memory store for relevant prior context before starting work. This ensures continuity across sessions and avoids redundant research.
