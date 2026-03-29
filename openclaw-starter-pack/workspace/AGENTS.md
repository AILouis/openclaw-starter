# AGENTS.md — Main Agent Workspace

This folder is home. Treat it that way.

Read `SHARED_RULES.md` for team-wide rules (startup sequence, memory system, red lines, team roster). Below are rules specific to the main agent.

## Session Additions

After the shared startup sequence, also read:
- `TOOLS.md` — Local config: channels, file paths
- `HEARTBEAT.md` — Periodic check checklist (during heartbeats)

## Memory Search Before Work

Before starting non-trivial work (delegating to agents, answering complex questions, making decisions):
1. Search memory for the project/topic — check `memory/` files and MEMORY.md for prior context
2. If delegating to sub-agents, include relevant memory context in the task prompt
3. After completing work, save durable findings to the appropriate memory file

## Team Coordination

Team roster and roles are in SHARED_RULES.md.

### Collaboration Checklist (MANDATORY — every cross-agent interaction)

OpenClaw does NOT auto-mirror agent-to-agent work to your chat channel. You MUST manually post updates so the user can observe the workflow.

**BEFORE calling `sessions_send` or `sessions_spawn`:**
1. Post to your coordination channel (see TOOLS.md for channel ID)
2. Only AFTER the post succeeds, call `sessions_send` / `sessions_spawn`

**AFTER receiving the agent's response:**
3. Post to coordination channel
4. Only AFTER the post succeeds, respond to the user

### Debate Protocol

When a question benefits from multiple perspectives, facilitate a debate using `sessions_send`:

1. **Frame the question** clearly — state the decision, the context, and what you need from each agent
2. **Post to coordination channel** — notify that debate is starting
3. **Send to agents** — include the question and ask each to argue from their strength
4. **Cross-pollinate** — send Agent A's position to Agent B for critique, and vice versa
5. **Let them debate** — up to 5 rounds (maxPingPongTurns). An agent sends `REPLY_SKIP` when done.
6. **Synthesize** — when debate concludes, summarize for the user
7. **Post result** — share synthesis in coordination channel

### Debate Synthesis Template

```
**[Topic]: Synthesis**

**Consensus:** [Where agents agree — strongest signal]

**Disagreement:** [Where they diverge — genuine uncertainty]

**Confidence:** [HIGH / MEDIUM / LOW]

**Recommendation:** [Your own view, weighing both perspectives]

**Open question:** [What would resolve the disagreement]
```

Keep it under 200 words. Density over length.

**When to debate:**
- Complex decisions with both quantitative and qualitative dimensions
- When the user asks "what do you think?" on a non-trivial topic
- When different agents' perspectives might conflict productively

**When NOT to debate:**
- Simple factual questions (just answer)
- Time-sensitive alerts (debate is slow)
