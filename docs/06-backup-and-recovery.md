# Backup & Recovery

## What's Backed Up

| Directory | Source | Contents |
|-----------|--------|----------|
| `openclaw-config/` | `~/.openclaw/` | openclaw.json, cron jobs, agent auth profiles |
| `eve-workspace/` | `~/.openclaw/workspace/` | SOUL.md, MEMORY.md, AGENTS.md, daily memory logs |
| `jim-workspace/` | `/mnt/d/eve-projects/jim-workspace/` | Quant agent workspace + research files |
| `jesse-workspace/` | `/mnt/d/eve-projects/jesse-workspace/` | Market scout workspace + runbook |
| `albert-workspace/` | `/mnt/d/eve-projects/albert-workspace/` | Researcher workspace |
| `shared/` | `/mnt/d/eve-projects/` | TEAM_STATE.md, USER.md, SHARED_RULES.md |
| `env.age` | `~/.openclaw/.env` | API keys (age-encrypted) |

## What's Excluded (and Why)

| Excluded | Reason |
|----------|--------|
| `.env` (plaintext) | Security — only encrypted `env.age` is committed |
| `*.jsonl` (session logs) | Too large, ephemeral, not needed for recovery |
| `scan-state.json` | Rebuilt every scan by Jesse |
| `*.db`, `*.sqlite*` | Database files, rebuilt from source data |
| `*.csv`, `*.parquet` | Data files, fetched from APIs |
| `__pycache__/` | Python cache, regenerated |
| `node_modules/` | Dependencies, reinstalled |

## Backup Schedule

Daily at 03:00 HKT via system cron:

```
0 3 * * * /home/clawl1nux/openclaw-backup/backup.sh >> /tmp/openclaw-backup.log 2>&1
```

## How the Backup Script Works

**Location:** `~/openclaw-backup/backup.sh`

The script does six things:

1. **Sources .env** — Loads `~/.openclaw/.env` at runtime to authenticate git push via `GITHUB_PAT`
2. **Syncs config** — Copies `openclaw.json`, `jobs.json`, and agent auth profiles
3. **Syncs workspaces** — Uses `rsync -aL --delete` to mirror all workspaces (Eve, Jim, Jesse, Albert), following symlinks so backup contains real file contents
4. **Syncs shared files** — Copies TEAM_STATE.md, USER.md, and SHARED_RULES.md into `shared/`
5. **Encrypts secrets** — Uses `age` to encrypt `.env` into `env.age`
6. **Commits and pushes** — `git add -A`, commit with timestamp, push to GitHub

```bash
# Run manually anytime
~/openclaw-backup/backup.sh
```

## Secret Encryption (age)

Secrets (API keys, bot tokens) are encrypted using `age` before being committed to git.

### How It Works

- `.env` contains plaintext secrets (never committed to git)
- `age` encrypts `.env` into `env.age` using a public key
- Only `env.age` is committed
- Decryption requires the private key at `~/.age/key.txt`

### Key Locations

| File | Purpose |
|------|---------|
| `~/.age/key.txt` | Private key (NEVER commit this) |
| `~/.age/recipients.txt` | Public key (used for encryption) |

### Setting Up age (First Time)

```bash
mkdir -p ~/.age
age-keygen -o ~/.age/key.txt 2> ~/.age/recipients.txt

# IMPORTANT: Save ~/.age/key.txt in a password manager
# This is your recovery backstop
```

## Recovery Procedures

### Quick Recovery (Single File Corrupted)

```bash
cd ~/openclaw-backup

# Find the good version
git log --oneline -- eve-workspace/SOUL.md

# Restore it
git show <commit>:eve-workspace/SOUL.md > /tmp/restored-SOUL.md
cp /tmp/restored-SOUL.md ~/.openclaw/workspace/SOUL.md
```

### Full Recovery (New Machine or WSL Rebuild)

```bash
# 1. Clone the backup repo
git clone git@github.com:AILouis/openclaw-backup.git ~/openclaw-backup

# 2. Install OpenClaw (follow OpenClaw install docs)

# 3. Restore config
cp ~/openclaw-backup/openclaw-config/openclaw.json ~/.openclaw/
cp ~/openclaw-backup/openclaw-config/cron/jobs.json ~/.openclaw/cron/
cp -r ~/openclaw-backup/openclaw-config/agents/* ~/.openclaw/agents/

# 4. Restore workspaces
cp -r ~/openclaw-backup/eve-workspace/* ~/.openclaw/workspace/
cp -r ~/openclaw-backup/jim-workspace/* /mnt/d/eve-projects/jim-workspace/
cp -r ~/openclaw-backup/jesse-workspace/* /mnt/d/eve-projects/jesse-workspace/
cp -r ~/openclaw-backup/albert-workspace/* /mnt/d/eve-projects/albert-workspace/

# 5. Restore shared files and recreate USER.md symlinks
cp ~/openclaw-backup/shared/TEAM_STATE.md /mnt/d/eve-projects/TEAM_STATE.md
cp ~/openclaw-backup/shared/USER.md /mnt/d/eve-projects/USER.md
cp ~/openclaw-backup/shared/SHARED_RULES.md /mnt/d/eve-projects/SHARED_RULES.md
ln -sf /mnt/d/eve-projects/USER.md ~/.openclaw/workspace/USER.md
ln -sf /mnt/d/eve-projects/USER.md /mnt/d/eve-projects/jim-workspace/USER.md
ln -sf /mnt/d/eve-projects/USER.md /mnt/d/eve-projects/jesse-workspace/USER.md
ln -sf /mnt/d/eve-projects/USER.md /mnt/d/eve-projects/albert-workspace/USER.md

# 6. Decrypt secrets
age -d -i ~/.age/key.txt ~/openclaw-backup/env.age > ~/.openclaw/.env
chmod 600 ~/.openclaw/.env

# 7. Restart gateway
systemctl --user restart openclaw-gateway
```

### Recovering a Specific Day's Memory

```bash
cd ~/openclaw-backup
git log --oneline -- eve-workspace/memory/

# Find and restore a specific day
git show <commit>:eve-workspace/memory/2026-03-24.md
```

## GitHub Repository

- **Repo:** `github.com/AILouis/openclaw-backup`
- **Visibility:** Private
- **Auth:** GitHub PAT stored in `~/.openclaw/.env` as `GITHUB_PAT` (sourced by backup.sh at runtime)
- **Push strategy:** Quiet push to `main`, fallback to `master`

## Verifying Backup Health

```bash
# Check last backup log
tail -20 /tmp/openclaw-backup.log

# Check last commit
cd ~/openclaw-backup && git log -1

# Check crontab entry exists
crontab -l | grep backup

# Run a manual backup
~/openclaw-backup/backup.sh
```
