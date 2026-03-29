# Skills

OpenClaw skills are specialized instruction sets that teach your agents how to use specific tools or APIs.

## How to Install Skills

```bash
# Browse available skills
openclaw skills list

# Install a skill
openclaw skills install <skill-name>
```

## Recommended Starter Skills

| Skill | What It Does |
|-------|-------------|
| `github` | GitHub CLI integration — issues, PRs, workflows |
| `summarize` | Summarize URLs, PDFs, audio, YouTube videos |
| `weather` | Weather forecasts via wttr.in |
| `blogwatcher` | Monitor RSS/Atom feeds for updates |

## Custom Skills

You can create your own skills. Each skill is a directory with a `SKILL.md` file that contains instructions for the agent.

```
skills/
  my-skill/
    SKILL.md          # Instructions the agent reads
    scripts/          # Optional helper scripts
    references/       # Optional reference docs
```

See the OpenClaw docs for the full skill authoring guide.
