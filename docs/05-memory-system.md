# Memory System

## Overview

OpenClaw's memory operates in three layers, from raw to curated:

```
Layer 1: Daily Logs          memory/YYYY-MM-DD.md     Raw session notes
    |
    v  (Eve distills during heartbeats)
Layer 2: MEMORY.md           workspace/MEMORY.md      Curated long-term memory
    |
    v  (OpenAI embeddings)
Layer 3: Embedded Memory      memory/main.sqlite       Semantic search via embeddings
```

## Layer 1: Daily Memory Logs

**Location:** `~/.openclaw/workspace/memory/YYYY-MM-DD.md`

Each sub-agent workspace also has its own `memory/` directory for daily logs:
- `jim-workspace/memory/`
- `jesse-workspace/memory/`
- `albert-workspace/memory/`

These are raw, timestamped notes captured during sessions. They include:
- Trade views and positioning
- Decisions Louis has made
- Preferences and communication rules
- Ongoing project state
- Important config changes
- Personal reflections

**How they're created:**
- Eve appends to the current day's file during conversations
- Before session compaction (at ~100k tokens), Eve auto-saves durable notes via the `memoryFlush` mechanism

**Compaction memoryFlush prompt:** When a session approaches 100k tokens, Eve receives a system prompt to save important context to `memory/YYYY-MM-DD.md` before the session is compressed. She saves trade views, decisions, preferences, project state, config changes, and reflections worth keeping.

## Layer 2: Curated Memory (MEMORY.md)

**Location:** `~/.openclaw/workspace/MEMORY.md`

This is Eve's curated long-term memory — the distilled essence of what matters across sessions. Think of it as her "long-term memory" vs the daily files which are "short-term notes."

**What's in it:**
- Louis's profile and preferences
- Communication rules and channel setup
- Model/config preferences
- Team structure details
- Market data and project context
- Trading/regime context
- Operational notes

**How it's maintained:**
- Eve reviews daily log files during heartbeats (every few days)
- She distills significant events, lessons, and insights into MEMORY.md
- She removes outdated entries that are no longer relevant
- She keeps it high-signal and concise

**Security rule:** MEMORY.md is ONLY loaded in main sessions (direct chat with Louis). It is NOT loaded in shared contexts (group chats, sessions with other people) to prevent personal context from leaking.

## Layer 3: Embedded Memory

**Location:** `~/.openclaw/memory/main.sqlite`

**Status:** ENABLED (memory-lancedb plugin activated 2026-03-25). Embedding search is now active for all agents.

OpenClaw embeds memory entries using:
- Provider: OpenAI
- Model: `text-embedding-3-small`
- Plugin: `memory-lancedb` (enabled in `openclaw.json`)

This enables semantic search — Eve can find relevant memories even when the exact wording differs from the query. This is the "recall" mechanism that powers Eve's ability to find context from weeks or months ago.

**Configuration:**
- `plugins.slots.memory` must be `"memory-lancedb"` to activate (not just enabled in entries)
- `embedding.apiKey: ${OPENAI_API_KEY}` and `embedding.model: text-embedding-3-small` are **required**
- `autoRecall: true` — relevant memories are automatically injected into context before responses
- `autoCapture: true` — important messages are automatically embedded for future recall
- `captureMaxChars: 2000` — max message length for capture

## How Memory Flows

```
1. Louis sends a thought/decision
      |
2. Eve captures it in memory/YYYY-MM-DD.md
      |
3. Session approaches 100k tokens
      |
4. memoryFlush triggers: Eve saves durable notes to daily file
      |
5. Session compacts (older messages compressed)
      |
6. During heartbeat: Eve reviews daily files
      |
7. Significant insights promoted to MEMORY.md
      |
8. Embedded memory indexes everything for semantic search
```

## Telling Eve to Remember Things

**Save something:**
- "Remember that I think CNH will weaken to 7.5 by Q3"
- "Save this: I want to focus on 5Y IRS as primary hedge"
- Any explicit "remember this" or "note this down"

Eve writes it to `memory/YYYY-MM-DD.md` and may promote important items to MEMORY.md.

**Recall something:**
- "What did I say about the CNH outlook?"
- "What were we working on last Tuesday?"
- "What's my current view on rates?"

Eve searches daily files, MEMORY.md, and embedded memory to find relevant context.

**Forget something:**
- "You can forget the Singapore rotation thing"
- "Remove the entry about the HKD peg from memory"

Eve updates MEMORY.md or daily files accordingly.

## Shared User Profile (USER.md)

USER.md is a single shared file at `/mnt/d/eve-projects/USER.md`, symlinked into all agent workspaces. This ensures every agent has the same view of Louis's profile and preferences without maintaining separate copies.

## Memory Search Protocol

As of 2026-03-25, all agents follow a "memory search before work" protocol, defined in each agent's AGENTS.md:

1. **Before starting any task**, the agent runs a memory search for relevant prior context
2. The agent checks daily logs and embedded memory for related decisions, preferences, or lessons
3. Results are incorporated into the current task to avoid repeating mistakes or contradicting prior decisions

This ensures continuity across sessions and prevents agents from operating without historical context.

## Memory Rules

### What Gets Saved

- Trade views, positioning decisions
- Louis's explicit preferences and rules
- Important config changes
- Project milestones and state
- Personal reflections worth keeping
- Lessons learned from mistakes

### What Doesn't Get Saved

- Secrets (unless explicitly asked)
- Ephemeral conversation (greetings, acknowledgments)
- Raw data that can be regenerated
- Duplicate information already in MEMORY.md

### The "Write It Down" Principle

Eve follows a strict rule: **if you want to remember something, write it to a file.** "Mental notes" don't survive session restarts. This applies to:
- Things Louis says to remember
- Lessons Eve learns from mistakes
- Configuration changes
- Patterns Eve notices

**Text > Brain** — always write it down.

## Memory Maintenance Schedule

During heartbeats (every ~55 minutes during active hours), Eve periodically:

1. Reads recent `memory/YYYY-MM-DD.md` files
2. Identifies significant events or insights worth keeping long-term
3. Updates MEMORY.md with distilled learnings
4. Removes outdated info from MEMORY.md

This happens every few days, not every heartbeat — it's part of the rotating checklist.
