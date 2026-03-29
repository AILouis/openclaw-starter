# Configuration Reference

## openclaw.json

**Location:** `~/.openclaw/openclaw.json`

This is the main configuration file. Key sections:

### `auth.profiles`

API provider authentication:

```json
{
  "anthropic:cctoken-ll": { "provider": "anthropic", "mode": "token" },
  "openai:default": { "provider": "openai", "mode": "api_key" },
  "openai-codex:default": { "provider": "openai-codex", "mode": "oauth" }
}
```

### `agents.defaults`

Default settings applied to all agents:

| Setting | Value | Purpose |
|---------|-------|---------|
| `model.primary` | `openai-codex/gpt-5.4` | Default model |
| `model.fallbacks` | Opus 4.6, Sonnet 4.6 | Fallback chain |
| `workspace` | `~/.openclaw/workspace` | Default workspace |
| `memorySearch.provider` | `openai` | Embedding provider |
| `memorySearch.model` | `text-embedding-3-small` | Embedding model |
| `compaction.memoryFlush.softThresholdTokens` | `100000` | Compaction trigger |
| `heartbeat.every` | `55m` | Heartbeat interval |
| `heartbeat.activeHours` | 07:00-22:00 HKT | Active hours |
| `heartbeat.model` | `claude-haiku-4-5` | Heartbeat model |

Sub-agent spawning defaults (`subagents`):

```json
"subagents": {
  "model": "anthropic/claude-sonnet-4-6",
  "runTimeoutSeconds": 900,
  "maxSpawnDepth": 2,
  "maxChildrenPerAgent": 5,
  "maxConcurrent": 8
}
```

Controls sub-agent spawning limits and defaults.

### `agents.list`

Individual agent configurations:

| Agent | ID | Model | Workspace |
|-------|-----|-------|-----------|
| Eve | `main` | `openai-codex/gpt-5.4` + fallbacks | `~/.openclaw/workspace` |
| Jim | `jim` | `anthropic/claude-opus-4-6` | `/mnt/d/eve-projects/jim-workspace` |
| Jesse | `jesse` | `anthropic/claude-sonnet-4-6` | `/mnt/d/eve-projects/jesse-workspace` |
| Albert | `albert` | `anthropic/claude-opus-4-6` | `/mnt/d/eve-projects/albert-workspace` |

### `tools`

```json
{
  "profile": "coding",
  "web.search": { "enabled": true, "provider": "perplexity" },
  "web.fetch": { "enabled": true },
  "agentToAgent": {
    "enabled": true,
    "allow": ["main", "jim", "jesse", "albert"]
  }
}
```

### `session`

```json
{
  "dmScope": "per-channel-peer",
  "agentToAgent": { "maxPingPongTurns": 5 }
}
```

### `channels.discord`

```json
{
  "enabled": true,
  "token": "${DISCORD_BOT_TOKEN}",
  "groupPolicy": "allowlist",
  "historyLimit": 50,
  "streaming": "partial",
  "guilds": {
    "1486000944314585248": {
      "requireMention": false,
      "users": ["843760137126019082"]
    }
  },
  "threadBindings": {
    "spawnSubagentSessions": true
  }
}
```

- `threadBindings.spawnSubagentSessions: true` enables thread-bound persistent Jim/Albert sessions on Discord

### `channels.telegram`

Currently **disabled** (`enabled: false`). Discord is the primary surface.

### `gateway`

```json
{
  "port": 18789,
  "mode": "local",
  "bind": "loopback",
  "auth": { "mode": "token", "token": "${OPENCLAW_GATEWAY_TOKEN}" }
}
```

### `plugins`

```json
{
  "slots": {
    "memory": "memory-lancedb"
  },
  "entries": {
    "memory-lancedb": {
      "enabled": true,
      "config": {
        "autoRecall": true,
        "autoCapture": true,
        "captureMaxChars": 2000,
        "embedding": {
          "apiKey": "${OPENAI_API_KEY}",
          "model": "text-embedding-3-small"
        }
      }
    }
  }
}
```

- `plugins.slots.memory` must be set to `"memory-lancedb"` to activate the plugin as the memory provider (default is `"memory-core"`)
- `embedding.apiKey` and `embedding.model` are **required** — without them, `openclaw doctor` will report an error
- `autoRecall` injects relevant memories before responses
- `autoCapture` automatically embeds important messages for future recall (up to 2000 chars)
- Supported embedding models: `text-embedding-3-small`, `text-embedding-3-large`

The plugin powers semantic memory search using embedded vectors stored in LanceDB at `~/.openclaw/memory/lancedb`. Restart the gateway after enabling or disabling.

### `hooks.internal`

Enabled hooks:
- `boot-md` — Loads workspace markdown files on session start
- `bootstrap-extra-files` — Loads additional bootstrap files
- `command-logger` — Logs commands for audit
- `session-memory` — Manages session memory persistence

---

## Environment Variables (.env)

**Location:** `~/.openclaw/.env` (permissions: 600)
**Encrypted backup:** `~/openclaw-backup/env.age`

| Variable | Purpose |
|----------|---------|
| `PERPLEXITY_API_KEY` | Web search (Perplexity AI) |
| `DISCORD_BOT_TOKEN` | Discord bot authentication |
| `OPENCLAW_GATEWAY_TOKEN` | Gateway API authentication |
| `OPENAI_API_KEY` | Memory embeddings only (NOT for chat) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot (currently disabled) |
| `GITHUB_PAT` | GitHub authentication for `backup.sh` git push |

---

## Cron Jobs (jobs.json)

**Location:** `~/.openclaw/cron/jobs.json`

See [04-scheduling.md](04-scheduling.md) for full schedule details.

### Active Jobs Summary

| Job Name | Cron (HKT) | Agent | Model | Delivery Channel |
|----------|-----------|-------|-------|------------------|
| `jesse-morning-briefing` | `0 7 * * 1-5` | jesse | sonnet-4-6 | market-update-jesse |
| `jesse-hourly-scan` | `0 10,13,16,19,22 * * 1-5` | jesse | sonnet-4-6 | market-update-jesse |
| `jesse-weekend-scan` | `0 9,21 * * 0,6` | jesse | sonnet-4-6 | market-update-jesse |
| `jesse-week-review` | `0 20 * * 0` | jesse | sonnet-4-6 | market-update-jesse |
| `jesse-week-ahead` | `30 20 * * 0` | jesse | sonnet-4-6 | market-update-jesse |
| `albert-weekly-research` | `0 15 * * 0` | main (Eve orchestrates Albert + Jim) | system event → Opus debate flow | agent-teams + general |

Note: `albert-weekly-research` is no longer an isolated Albert cron. It now fires into Eve's main session as a `systemEvent`, and Eve runs the Albert↔Jim debate workflow from there.

Schema per job (isolated agent example):
```json
{
  "id": "uuid",
  "name": "job-name",
  "description": "Human-readable description",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 7 * * 1-5",
    "tz": "Asia/Hong_Kong"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "The prompt sent to the agent",
    "model": "anthropic/claude-sonnet-4-6",
    "timeoutSeconds": 900
  },
  "delivery": {
    "mode": "announce",
    "channel": "discord",
    "to": "channel:<channel_id>"
  },
  "state": {
    "nextRunAtMs": 0,
    "lastRunAtMs": 0,
    "lastRunStatus": "ok",
    "lastDurationMs": 0,
    "lastDeliveryStatus": "delivered",
    "consecutiveErrors": 0
  },
  "agentId": "jesse"
}
```

---

## Systemd Service

**Location:** `~/.config/systemd/user/openclaw-gateway.service`

```ini
[Unit]
Description=OpenClaw Gateway (v2026.3.22)
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/node /usr/lib/node_modules/openclaw/dist/index.js gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30

[Install]
WantedBy=default.target
```

**Commands:**
```bash
systemctl --user start openclaw-gateway     # Start
systemctl --user stop openclaw-gateway      # Stop
systemctl --user restart openclaw-gateway   # Restart
systemctl --user status openclaw-gateway    # Status
journalctl --user -u openclaw-gateway -f    # Follow logs
```

---

## Discord IDs Reference

| Entity | ID |
|--------|----|
| Guild (server) | `1486000944314585248` |
| `#general` channel | `1486000944998121646` |
| `#market-update-jesse` channel | `1486001063319572642` |
| `#agent-teams` channel | `1486001111511863356` |
| Louis's Discord user | `843760137126019082` |

---

## Complete File Path Reference

### OpenClaw Runtime
```
~/.openclaw/openclaw.json                    # Main config
~/.openclaw/.env                             # API keys (600 perms)
~/.openclaw/cron/jobs.json                   # Cron definitions
~/.openclaw/cron/runs/                       # Cron execution logs
~/.openclaw/memory/main.sqlite               # Embedded memory DB
~/.openclaw/agents/{main,jim,jesse,albert}/  # Agent auth + model configs
~/.openclaw/workspace/                       # Eve's workspace root
~/.openclaw/workspace/SOUL.md                # Eve's identity
~/.openclaw/workspace/IDENTITY.md            # Eve's name/emoji
~/.openclaw/workspace/USER.md                # Louis's profile
~/.openclaw/workspace/AGENTS.md              # Agent rules
~/.openclaw/workspace/TOOLS.md               # Local config
~/.openclaw/workspace/TASKS.md               # Task list
~/.openclaw/workspace/MEMORY.md              # Curated memory
~/.openclaw/workspace/HEARTBEAT.md           # Heartbeat checklist
~/.openclaw/workspace/memory/                # Daily memory logs
```

### Shared Project Files
```
/mnt/d/eve-projects/USER.md                  # Single shared user profile (symlinked into all workspaces)
/mnt/d/eve-projects/SHARED_RULES.md          # Common team rules (referenced by all agents' AGENTS.md)
/mnt/d/eve-projects/TEAM_STATE.md            # Shared team context (regime, active projects)
```

**SHARED_RULES.md agent-specific startup section** (added 2026-03-25): SHARED_RULES.md now includes an agent-specific startup section that defines per-agent initialization steps. Each agent reads SHARED_RULES.md at boot and executes its designated startup routine (e.g., memory search, loading scan-state, checking research queue). This replaces ad-hoc startup logic that was previously scattered across individual AGENTS.md files.

### Project Workspaces
```
/mnt/d/eve-projects/market-data/             # Shared market data library
/mnt/d/eve-projects/Market_Regime_Detection/ # Regime detection project
/mnt/d/eve-projects/jim-workspace/SOUL.md    # Jim's identity
/mnt/d/eve-projects/jesse-workspace/SOUL.md  # Jesse's identity
/mnt/d/eve-projects/jesse-workspace/scan-state.json  # Jesse's dedup state
/mnt/d/eve-projects/albert-workspace/SOUL.md # Albert's identity
```

### Backup & System
```
~/openclaw-backup/backup.sh                  # Backup script
~/openclaw-backup/env.age                    # Encrypted secrets
~/.age/key.txt                               # Age private key
~/.age/recipients.txt                        # Age public key
~/.config/systemd/user/openclaw-gateway.service  # Systemd service
/tmp/openclaw-backup.log                     # Backup log
```

### Windows Drive Mapping
```
C: → /mnt/c/    # OS + system only
D: → /mnt/d/    # All projects (eve-projects/)
E: → /mnt/e/    # Available, backup/overflow
```
