# Troubleshooting

## Quick Diagnostic Commands

```bash
# Gateway status
systemctl --user status openclaw-gateway

# Gateway logs (last 50 lines)
journalctl --user -u openclaw-gateway -n 50 --no-pager

# Backup log
tail -20 /tmp/openclaw-backup.log

# System crontab
crontab -l

# Disk usage
df -h /home /mnt/d

# Check if gateway is listening
ss -tlnp | grep 18789
```

---

## Common Issues

### Gateway Not Responding

**Symptoms:** Eve doesn't respond on Discord. No messages coming through.

**Diagnosis:**
```bash
systemctl --user status openclaw-gateway
```

**Fixes:**
```bash
# Restart the gateway
systemctl --user restart openclaw-gateway

# Check logs for errors
journalctl --user -u openclaw-gateway -n 100 --no-pager

# If the service file is corrupted, check it
cat ~/.config/systemd/user/openclaw-gateway.service

# Nuclear option: reload systemd and restart
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway
```

**Common causes:**
- WSL was restarted (gateway doesn't auto-start across WSL restarts)
- Memory pressure (check with `free -h`)
- Node.js crash (check logs)

### Eve Not Responding on Discord

**Symptoms:** Gateway is running but Eve doesn't reply.

**Check:**
1. Is the Discord bot token valid? Check `.env`
2. Is the Discord connection alive? Check gateway logs for "discord" entries
3. Is the guild ID correct in `openclaw.json`? Should be `1486000944314585248`
4. Is your Discord user ID allowlisted? Should be `843760137126019082`

```bash
# Check for Discord-specific errors
journalctl --user -u openclaw-gateway | grep -i discord | tail -20
```

### Jesse Scans Not Running

**Symptoms:** `#market-update-jesse` is silent during scheduled times.

**Diagnosis:**
1. Check if the cron jobs are enabled in `~/.openclaw/cron/jobs.json`
2. Check `consecutiveErrors` field in each job's `state`
3. Check if Jesse's model (Sonnet 4.6) is accessible

```bash
# Read cron job states
python3 -c "
import json
with open('$HOME/.openclaw/cron/jobs.json') as f:
    data = json.load(f)
for job in data['jobs']:
    state = job.get('state', {})
    print(f\"{job['name']}: enabled={job['enabled']}, status={state.get('lastRunStatus', 'never')}, errors={state.get('consecutiveErrors', 0)}\")
"
```

**Common causes:**
- Stale catch-up: If gateway was down during scheduled time and comes back >90min (morning) or >20min (hourly) late, Jesse skips with `NO_REPLY`
- Model rate limit: Check if Anthropic API is accessible
- Silence is intentional: Jesse sends `NO_REPLY` when there's nothing new. This is normal.

### Model Errors / Rate Limits

**Symptoms:** Eve mentions model switches or degraded responses.

**What Eve does automatically:**
- Tells you immediately when a model switch happens
- Falls back through the chain: GPT-5.4 -> Opus 4.6 -> Sonnet 4.6
- Reports which provider/model hit limits

**What you can check:**
```bash
# Check auth profile error counts
cat ~/.openclaw/agents/main/agent/auth-profiles.json | python3 -m json.tool
```

**Fixes:**
- Wait for rate limits to reset (usually 1-60 minutes)
- Check API key validity in `.env`
- If a provider is down, Eve's fallback chain handles it automatically

### Memory-LanceDB Plugin Issues

**Symptoms:** Memory search returns no results, or agents skip the "memory search before work" step.

**Fixes:**
```bash
# Restart the gateway after enabling the plugin
systemctl --user restart openclaw-gateway

# Verify the plugin is loaded in logs
journalctl --user -u openclaw-gateway | grep -i lancedb | tail -10
```

**Note:** The memory-lancedb plugin was enabled on 2026-03-25. If the gateway was not restarted after the config change, the plugin will not be active.

### File Permission Issues

**Symptoms:** Gateway cannot read config or `.env`, agents fail to start.

**Context:** File permissions under `~/.openclaw/` were hardened on 2026-03-25. The `.env` file should be `600`, and the `~/.openclaw/` directory should be `700`.

**Diagnosis:**
```bash
ls -la ~/.openclaw/.env          # Should be -rw-------
ls -ld ~/.openclaw/              # Should be drwx------
stat -c '%a' ~/.openclaw/.env    # Should be 600
```

**Fix:**
```bash
chmod 700 ~/.openclaw/
chmod 600 ~/.openclaw/.env
```

### Memory Not Persisting

**Symptoms:** Eve seems to forget things between sessions.

**Check:**
1. Are daily memory files being created?
```bash
ls -la ~/.openclaw/workspace/memory/
```

2. Is MEMORY.md being updated?
```bash
git -C ~/openclaw-backup log --oneline -- eve-workspace/MEMORY.md | head -5
```

3. Is compaction memoryFlush working? Check if recent daily files have content:
```bash
wc -l ~/.openclaw/workspace/memory/*.md
```

**Common causes:**
- Session ended before compaction triggered (rare — only if very short session)
- MEMORY.md not being read (check if `boot-md` hook is enabled in `openclaw.json`)

### Backup Failing

**Symptoms:** No recent commits in `~/openclaw-backup/`.

**Diagnosis:**
```bash
# Check backup log
cat /tmp/openclaw-backup.log

# Check crontab
crontab -l | grep backup

# Check git remote
cd ~/openclaw-backup && git remote -v

# Check last commit date
cd ~/openclaw-backup && git log -1 --format="%ai"
```

**Common fixes:**
```bash
# If crontab entry is missing
crontab -e
# Add: 0 3 * * * /home/clawl1nux/openclaw-backup/backup.sh >> /tmp/openclaw-backup.log 2>&1

# If age encryption fails
command -v age  # Check if age is installed
ls ~/.age/      # Check if keys exist

# If git push fails — check GITHUB_PAT in .env
grep GITHUB_PAT ~/.openclaw/.env  # Verify PAT exists
# backup.sh reads GITHUB_PAT from .env at runtime for git push auth
```

### Market Data Stale or Failing

**Symptoms:** Jesse's scans missing price levels, or prices look wrong.

**Diagnosis:**
```bash
cd /mnt/d/eve-projects/market-data && python3 -m market_data --snapshot --format telegram
```

**Common causes:**
- yfinance API changes or rate limiting
- Network issues from WSL
- Python dependency issues

**Fixes:**
```bash
# Reinstall dependencies
cd /mnt/d/eve-projects/market-data && pip install -r requirements.txt

# Run tests
cd /mnt/d/eve-projects/market-data && python3 -m pytest
```

### WSL Restart Recovery

After a WSL restart, you need to:

1. **Start the gateway:**
```bash
systemctl --user start openclaw-gateway
```

2. **Verify it's running:**
```bash
systemctl --user status openclaw-gateway
```

3. **Check Discord connection** — send a message in `#general` and see if Eve responds

Note: The gateway is configured with `WantedBy=default.target`, so it should start automatically with the user session. But WSL sometimes doesn't trigger user services on boot.

Eve's workspace now includes `BOOT.md` — a gateway restart recovery checklist. After restart, Eve reads this to verify gateway, Discord, agents, cron jobs, state files, market data, and disk health are all operational.

### Health Check System

OpenClaw has a built-in health check module that monitors:
- **Disk space:** Warning at >80%, critical at >90%
- **Memory:** Critical at >95% utilization
- **Process count:** Warning at >2000 processes (fork bomb detection)
- **Environment variables:** Checks for required secrets

The health check runs as part of Eve's heartbeat cycle.

### Auto-Healing: Skills Monitor

OpenClaw has an auto-healing module for skills:
- Detects missing `node_modules` and runs `npm install --production`
- Validates `SKILL.md` existence and creates stubs if missing
- Runs with 60-second timeout
- Can be ignored for specific skills via `.skill_monitor_ignore`

---

## Emergency Contacts

If something is fundamentally broken and you can't fix it:

1. Check OpenClaw docs/changelog for the installed version (`2026.3.13` config, `2026.3.22` gateway)
2. The backup repo has git history — you can always roll back to a working state
3. Recovery from scratch is documented in [06-backup-and-recovery.md](06-backup-and-recovery.md)
