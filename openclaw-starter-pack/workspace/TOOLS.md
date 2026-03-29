# TOOLS.md - Local Notes

Model assignments are in `openclaw.json`. Run `openclaw agents list` for current models.

Team roster and roles: see SHARED_RULES.md. Agent-specific reach commands:
- Coder: `sessions_send(label="coder", message="<message>")`
- Researcher: `sessions_send(label="researcher", message="<message>")`

### Telegram Chats
- **main chat** (YOUR_MAIN_CHAT_ID) — main chat with user
- **coordination group** (YOUR_COORDINATION_GROUP_ID) — team coordination visibility (optional)

When collaborating with sub-agents, post a brief status update to the coordination chat so the user can observe the workflow.

### File System Layout
- **Projects root:** YOUR_PROJECTS_PATH — all projects go here
- **Workspace:** ~/.openclaw/workspace — agent workspace files

### Installed Skills

| Skill | Description |
|-------|-------------|
| (none yet) | Run `openclaw skills list` to see available skills |

---

Add whatever helps you do your job. This is your cheat sheet.
