# Scheduling: Cron Jobs & Heartbeat

## Jesse's Cron Schedule (All times Asia/Hong_Kong)

### Weekday Schedule

| Time | Job | What It Does |
|------|-----|-------------|
| **07:00** Mon-Fri | `jesse-morning-briefing` | Comprehensive 24-hour recap. The most detailed scan of the day. |
| **10:00** Mon-Fri | `jesse-hourly-scan` | What changed since last scan |
| **13:00** Mon-Fri | `jesse-hourly-scan` | What changed since last scan |
| **16:00** Mon-Fri | `jesse-hourly-scan` | What changed since last scan |
| **19:00** Mon-Fri | `jesse-hourly-scan` | What changed since last scan |
| **22:00** Mon-Fri | `jesse-hourly-scan` | What changed since last scan |

### Weekend Schedule

| Time | Job | What It Does |
|------|-----|-------------|
| **09:00** Sat & Sun | `jesse-weekend-scan` | Light scan: geopolitical, crypto, breaking news |
| **21:00** Sat & Sun | `jesse-weekend-scan` | Light scan: geopolitical, crypto, breaking news |

### Sunday Specials

| Time | Job | What It Does |
|------|-----|-------------|
| **20:00** Sunday | `jesse-week-review` | Facts-only summary of the week's major developments by narrative thread. Under 500 words. |
| **20:30** Sunday | `jesse-week-ahead` | Economic calendar for Mon-Fri. Consensus estimates. Market-moving items flagged. |

### Cron Job Details

**Cron expressions:**
- Morning briefing: `0 7 * * 1-5`
- Hourly scan: `0 10,13,16,19,22 * * 1-5`
- Weekend scan: `0 9,21 * * 0,6`
- Week review: `0 20 * * 0`
- Week ahead: `30 20 * * 0`

**All Jesse jobs share:**
- Model: `anthropic/claude-sonnet-4-6`
- Timeout: 900 seconds (15 minutes)
- Session: Isolated (doesn't use Eve's session)
- Delivery: Discord `market-update-jesse` channel
- Agent ID: `jesse`

> **Prompt optimization (2026-03-25):** Jesse's cron prompts were shortened to reference `JESSE.md` for all format rules, freshness windows, dedup logic, and self-audit procedures instead of duplicating them inline. This saves ~2,100 tokens/day across 7 daily scans. Prompts now also tell Jesse to read `TEAM_STATE.md` for current regime context, enabling the crisis-mode threshold override rule (lower all thresholds by ~30% when L3 = RISK_OFF).

**Stale catch-up rules:**
- Morning briefing: If the run starts >90 minutes late, Jesse responds `NO_REPLY` and skips
- Hourly scan: If the run starts >20 minutes late, Jesse responds `NO_REPLY` and skips
- Weekend scan: No skip rule (less time-sensitive)

**Silence behavior:**
- If a scan finds nothing new or noteworthy, Jesse responds `NO_REPLY` — no message is sent to Discord
- Silence means no news. Jesse never sends "nothing to report" filler.

### Cron Job Health Tracking

Each job tracks in `jobs.json`:
- `lastRunAtMs` — when it last ran
- `lastRunStatus` — `ok` or error
- `lastDurationMs` — how long it took
- `lastDeliveryStatus` — `delivered` or error
- `consecutiveErrors` — error counter (resets on success)

Eve checks cron health during heartbeats by reading these fields.

---

## Albert's Cron Schedule (All times Asia/Hong_Kong)

| Time | Job | What It Does |
|------|-----|-------------|
| **15:00** Sunday | `albert-weekly-research` | Weekly research digest delivered to the team |

### Cron Job Details

- Cron expression: `0 15 * * 0`
- Model: `anthropic/claude-opus-4-6`
- Delivery: Discord `agent-teams` channel
- Agent ID: `albert`

> **Note (2026-03-25):** Albert's cron now reads `MEMORY.md` for his prioritized research queue (6 topics), reads `AGENTS.md` for operational rules, and writes output to `research/YYYY-MM-DD-topic.md` instead of the workspace root.

---

## Heartbeat System

The heartbeat is Eve's periodic check-in mechanism — a lightweight background process that ensures the system stays healthy and Louis stays informed.

### Configuration

| Setting | Value |
|---------|-------|
| Interval | Every 55 minutes |
| Active hours | 07:00 - 22:00 HKT |
| Model | `anthropic/claude-haiku-4-5` (cheap, fast) |
| Target | `last` (continues the most recent session) |
| Light context | `true` (minimal token usage) |

### What Eve Checks (Rotating)

Eve doesn't do all checks every heartbeat — she rotates through them:

**System health:**
- Jesse cron — any errors or missed scans?
- `market_data.py` — returning fresh data?
- Disk/system health — anything unusual?

**Memory maintenance:**
- Recent daily memory files worth distilling into MEMORY.md?
- Outdated entries in MEMORY.md to clean up?

**Projects:**
- Pending Jim tasks — anything waiting for review?
- Albert research — stalled projects?

**Life admin (1-2x per day):**
- TASKS.md — anything due soon or overdue?
- Upcoming deadlines — university, SC onboarding prep?
- Did Louis mention something to do "later" that hasn't been done?

### Proactive Behavior (Waking Hours Only)

- If Louis hasn't been heard from in 8+ hours, Eve sends a gentle check-in
- If Jesse reports something contradicting Louis's known positions, Eve flags it
- If a TASKS.md item is due today, Eve reminds Louis early

### Silent Hours (23:00 - 07:00 HKT)

During silent hours, Eve responds `HEARTBEAT_OK` unless something is truly urgent. No check-ins, no reminders, no proactive messages.

### Heartbeat State

Eve tracks her checks in `memory/heartbeat-state.json`:
```json
{
  "lastChecks": {
    "jesse_health": 1703275200,
    "memory_maintenance": 1703260800,
    "market_data": null
  }
}
```

### Heartbeat vs Cron: When to Use Each

| Use Heartbeat When | Use Cron When |
|---------------------|---------------|
| Multiple checks can batch together | Exact timing matters |
| Need conversational context | Task needs session isolation |
| Timing can drift (~55 min is fine) | Want a different model |
| Want to reduce API calls | Output should go directly to a channel |

---

## Daily Backup Cron

In addition to OpenClaw's internal cron, a system-level cron job runs the backup:

```
0 3 * * * /home/clawl1nux/openclaw-backup/backup.sh >> /tmp/openclaw-backup.log 2>&1
```

- **Time:** 03:00 HKT daily
- **What:** Syncs all workspaces and config to `~/openclaw-backup/`, encrypts `.env`, commits and pushes to GitHub
- **Log:** `/tmp/openclaw-backup.log`

See [06-backup-and-recovery.md](06-backup-and-recovery.md) for full details.

---

## Modifying Cron Jobs

Cron jobs are defined in `~/.openclaw/cron/jobs.json`. To modify:

1. Edit the file directly (careful with JSON syntax)
2. Or use Eve — ask her to update a cron schedule

Key fields per job:
- `schedule.expr` — Standard cron expression
- `schedule.tz` — Timezone (always `Asia/Hong_Kong`)
- `enabled` — Toggle job on/off
- `payload.message` — The prompt Jesse receives
- `payload.model` — Model to use
- `payload.timeoutSeconds` — Max execution time
- `delivery.to` — Discord channel target

After editing, restart the gateway for changes to take effect:
```bash
systemctl --user restart openclaw-gateway
```
