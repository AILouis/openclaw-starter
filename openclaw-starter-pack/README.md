# OpenClaw Starter Pack

**OpenClaw** is a self-hosted AI agent framework that runs on your machine and talks to you via Telegram (or Discord, Signal, etc.). You control the models, the data stays local, and multiple agents can collaborate on your behalf.

This starter pack gives you a ready-to-customize multi-agent setup: config template, workspace files, memory system, heartbeat monitoring, and an agent-to-agent debate protocol.

## What's Inside

```
openclaw-starter-pack/
├── README.md                          ← You are here (setup guide)
├── openclaw.template.json             ← Config template (fill in your credentials)
├── telegram-setup.md                  ← Telegram bot setup walkthrough
├── .gitignore                         ← Prevents committing API keys
├── workspace/
│   ├── AGENTS.md                      ← Coordination rules, debate protocol
│   ├── SHARED_RULES.md                ← Team-wide rules all agents follow
│   ├── HEARTBEAT.md                   ← Periodic health check checklist
│   ├── TOOLS.md                       ← Channel IDs, file paths, local notes
│   ├── MEMORY.md                      ← Long-term memory (starts empty)
│   ├── SOUL.md.example                ← Example personality file
│   ├── IDENTITY.md.example            ← Example identity file
│   └── memory/                        ← Daily memory files go here
├── agents/
│   ├── coder/agent/                   ← Coder agent files (AGENTS.md + SOUL.md)
│   └── researcher/agent/              ← Researcher agent files (AGENTS.md + SOUL.md)
└── skills/
    └── README.md                      ← How to install/create skills
```

## What This Setup Gives You

- **3 agents**: a main assistant, a coder, and a researcher — all able to talk to each other
- **Debate protocol**: agents can debate topics from different angles, then synthesize a combined answer
- **Memory system**: daily logs + curated long-term memory, with automatic save before context resets
- **Heartbeat monitoring**: periodic health checks during your active hours
- **Session management**: auto-reset, compaction safeguards, session cleanup
- **Telegram integration**: connect via a Telegram bot you control

---

## Setup Guide (Step by Step)

### What You Need Before Starting

1. **A computer** that can stay on (your laptop, a home server, or a cloud VPS)
2. **Node.js** v18+ installed — download from <https://nodejs.org/>
3. **Two API keys** (both required):
   - **Anthropic API key** — powers your AI agents (Claude) → get it at <https://console.anthropic.com/>
   - **OpenAI API key** — powers memory search (embeddings only, very cheap) → get it at <https://platform.openai.com/>
4. **A Telegram account** — to talk to your agents
5. **(Optional) Perplexity API key** — enables web search → <https://www.perplexity.ai/settings/api>

**About costs:** Anthropic charges per token used. Claude Haiku (~$0.25/Mtok) handles heartbeats and light tasks. Claude Sonnet (~$3/Mtok) is the balanced workhorse. Claude Opus (~$15/Mtok) is the smartest but most expensive. Memory embeddings via OpenAI cost ~$0.02/Mtok — essentially free. Start with Sonnet for everything; you can optimize later.

### Step 1: Install OpenClaw

```bash
npm install -g openclaw
```

Verify:
```bash
openclaw --version
```

### Step 2: Initialize OpenClaw

```bash
openclaw init
```

This creates `~/.openclaw/` with a default config. We'll replace it next.

### Step 3: Set Up Telegram

Follow the **[Telegram Setup Guide](telegram-setup.md)** to:
1. Create your Telegram bot via @BotFather
2. Get your numeric user ID via @userinfobot
3. (Optional) Create a coordination group for agent-to-agent visibility

### Step 4: Fill In the Config

1. Copy the template:
```bash
cp openclaw.template.json ~/.openclaw/openclaw.json
```

2. Open `~/.openclaw/openclaw.json` in any text editor (VS Code, nano, vim, Notepad — anything works)

3. Find and replace every `YOUR_*` placeholder:

**Credentials:**

| Find this | Replace with | Where to get it |
|-----------|-------------|-----------------|
| `YOUR_TELEGRAM_BOT_TOKEN` | Your bot token | @BotFather on Telegram |
| `YOUR_TELEGRAM_USER_ID` | Your numeric user ID | @userinfobot on Telegram |
| `YOUR_OPENAI_API_KEY` | OpenAI API key | <https://platform.openai.com/> |
| `YOUR_PERPLEXITY_API_KEY` | Perplexity key (or remove the web.search block) | <https://perplexity.ai/settings/api> |

**Paths:**

| Find this | Replace with | Example |
|-----------|-------------|---------|
| `YOUR_WORKSPACE_PATH` | Where workspace files will live | `/home/you/.openclaw/workspace` |
| `YOUR_PROJECTS_PATH` | Where project folders will live | `/home/you/projects` |
| `YOUR_OPENCLAW_PATH` | OpenClaw data directory | `/home/you/.openclaw` |

**Agent names (pick whatever you like):**

| Find this | Replace with | Example |
|-----------|-------------|---------|
| `YOUR_MAIN_AGENT_NAME` | Name for your main agent | `assistant`, `eva`, `jarvis` |
| `YOUR_CODER_AGENT_NAME` | Name for your coder | `coder`, `dev`, `engineer` |
| `YOUR_RESEARCHER_AGENT_NAME` | Name for your researcher | `researcher`, `analyst`, `scholar` |

**Models:**

| Find this | Replace with | Recommendation |
|-----------|-------------|----------------|
| `YOUR_PRIMARY_MODEL` | Your default model | `anthropic/claude-sonnet-4-6` (balanced) |
| `YOUR_FALLBACK_MODEL` | Backup if primary fails | `anthropic/claude-haiku-4-5` (cheap fallback) |
| `YOUR_TIMEZONE` | Your timezone | `Asia/Hong_Kong`, `America/New_York`, `Europe/London` |

**Group chat (optional — remove if not using):**

| Find this | Replace with |
|-----------|-------------|
| `YOUR_GROUP_CHAT_ID` | Telegram group chat ID (negative number, e.g. `-1001234567890`) |

If you're NOT using a coordination group, delete the entire `"groups": { ... }` block from the config.

**Also update in workspace files:**
- `workspace/TOOLS.md` — replace `YOUR_MAIN_CHAT_ID` and `YOUR_COORDINATION_GROUP_ID` with your actual Telegram chat IDs

### Step 5: Set Up Auth

Tell OpenClaw how to authenticate with your AI providers:

```bash
# Paste your Anthropic API key when prompted
openclaw auth add anthropic

# Paste your OpenAI API key when prompted
openclaw auth add openai
```

### Step 6: Set Up Workspace Files

```bash
# Copy workspace files
cp -r workspace/* ~/.openclaw/workspace/

# Create your personality files from examples
cd ~/.openclaw/workspace
cp SOUL.md.example SOUL.md
cp IDENTITY.md.example IDENTITY.md
```

Now edit these files:
- **`SOUL.md`** — Give your agent a personality. This is the fun part — make it yours. The example file shows the structure; customize the tone, values, and style.
- **`IDENTITY.md`** — Pick a name and emoji for your agent.
- **`TOOLS.md`** — Fill in your Telegram chat IDs and project paths.

### Step 7: Set Up Agent Directories

Each sub-agent needs its own workspace:

```bash
# Create workspaces for your sub-agents
mkdir -p YOUR_PROJECTS_PATH/coder-workspace
mkdir -p YOUR_PROJECTS_PATH/researcher-workspace

# Copy the provided agent files
cp -r agents/coder ~/.openclaw/agents/
cp -r agents/researcher ~/.openclaw/agents/
```

(Replace `YOUR_PROJECTS_PATH` with the actual path you chose in Step 4.)

Feel free to edit the coder and researcher SOUL.md files to give them distinct personalities.

### Step 8: Validate Your Config

```bash
openclaw doctor
```

This checks your config for errors. Fix any issues it reports.

**Note:** `openclaw doctor` can be strict — if it flags a field you think is valid, try removing it. Not all options are supported in every version. When in doubt, simpler config = fewer issues.

### Step 9: Start OpenClaw

```bash
openclaw gateway start
```

### Step 10: Test It

1. Open Telegram
2. Find your bot and send: `hello`
3. It should respond!

Useful commands you can send to the bot:
- `/status` — see system status
- `/new` — start a fresh conversation
- `/model sonnet` — switch to a specific model

---

## Key Concepts

### How Agents Work

You have 3 agents that can talk to each other:

- **Main agent** — your primary assistant. You chat with this one. It orchestrates the others.
- **Coder** — specialized for coding. The main agent delegates implementation work to it.
- **Researcher** — specialized for analysis. The main agent sends research questions to it.

You talk to the main agent. When it needs help, it delegates to the specialists and synthesizes their work back to you.

### Debates

When a question has multiple angles, the main agent can run a "debate":

1. Sends the question to both coder and researcher
2. Each argues from their specialty
3. They cross-critique each other (up to 5 rounds)
4. Main agent synthesizes the final answer

Example: You ask "Should I use SQLite or PostgreSQL for this project?"
→ Coder argues implementation tradeoffs
→ Researcher argues architectural principles
→ Main agent synthesizes: "SQLite for now because X, migrate to Postgres when Y"

### Memory

Agents wake up fresh each session. Memory files give them continuity:

- **`memory/YYYY-MM-DD.md`** — daily logs saved automatically before context resets
- **`MEMORY.md`** — curated long-term memory you and the agent maintain together

### Heartbeat

Every 60 minutes during your active hours, OpenClaw checks in. The agent reads the health checklist and stays quiet if everything's fine. If something needs attention, it tells you.

You can customize active hours in the config (`heartbeat.activeHours`). Agents won't bother you outside those hours unless something is urgent.

### Sessions

Conversations reset automatically to keep context fresh:
- **DMs:** reset after 6 hours idle
- **Groups:** reset after 2 hours idle

You can manually reset anytime with `/new`.

---

## After Setup: What's Next?

1. **Install skills** — `openclaw skills install github` for GitHub, `openclaw skills install weather` for weather, etc.
2. **Customize personalities** — edit SOUL.md files to make agents truly yours
3. **Add cron jobs** — schedule agents to do things automatically (daily briefings, monitoring, etc.)
4. **Experiment with models** — try different models for different agents to optimize cost vs quality

---

## Troubleshooting

**`openclaw doctor` shows errors:**
Read the error messages — they're usually specific. Common fixes: check API keys, verify paths exist, ensure JSON is valid (a missing comma breaks everything).

**Bot doesn't respond on Telegram:**
- `openclaw gateway status` — is the gateway running?
- Is your bot token correct?
- Is your user ID in `allowedUsers`?

**Memory not working:**
- The OpenAI API key is required (for embeddings). Check it's set correctly in both `openclaw auth` and the config's `memory-lancedb` plugin.

**Agents can't talk to each other:**
- Check `tools.agentToAgent.enabled` is `true`
- Check `tools.agentToAgent.allow` includes all your agent IDs

**Need help?**
- Docs: <https://docs.openclaw.ai>
- Community: <https://discord.com/invite/clawd>
