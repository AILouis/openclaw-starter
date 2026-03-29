# Discord Interaction Guide

## Channel Map

| Channel | ID | Purpose |
|---------|-----|---------|
| `#general` | `1486000944998121646` | Main chat with Eve. Talk about anything here. |
| `#market-update-jesse` | `1486001063319572642` | Jesse's automated market scans and briefings |
| `#agent-teams` | `1486001111511863356` | Agent coordination visibility — see what Eve delegates |
| `Jim` (thread under `#general`) | dynamic | Direct persistent thread with Jim for coding / quant work |
| `Albert` (thread under `#general`) | dynamic | Direct persistent thread with Albert for research / synthesis |

## Talking to Eve

Just message in `#general`. No @mention needed — Eve reads everything in the server. She responds to all your messages.

### Things You Can Ask Eve

- **Research:** "Look into the PBoC's RRR history and how it correlates with CGB 10Y moves"
- **Delegate to Jim:** "Have Jim backtest a momentum signal on CGB futures"
- **Delegate to Albert:** "Ask Albert to research the parallels between 1998 Asian crisis and current conditions"
- **Request a debate:** "I want Jim and Albert to debate whether we're entering a stagflation regime"
- **Memory:** "Remember that I think CNH will weaken to 7.5 by Q3"
- **Tasks:** "Add to my tasks: review SC onboarding docs by April 15"
- **Market data:** "Run the market data snapshot"
- **Philosophy:** "What would Ramana say about the fear of missing a trade?"
- **Life strategy:** "I'm stuck on whether to take the Singapore rotation or stay in HK"

### How Eve Responds

- She'll acknowledge quickly, then work in background if needed
- For delegated tasks, she posts to `#agent-teams` first, then delivers results to you
- If she needs to restart the gateway or do something disruptive, she warns you first
- If her model switches (e.g., GPT-5.4 goes down), she tells you immediately
- If you want direct long-form work with Jim or Albert, she can route you to their dedicated persistent threads

## Direct Threads with Jim and Albert

Jim and Albert now each have a dedicated persistent thread under `#general`:

- **Jim** — technical desk for coding, backtests, debugging, and implementation
- **Albert** — research desk for macro synthesis, philosophy, and deep dives

Use `#general` when you want Eve to orchestrate. Use the dedicated thread when you want to speak to that specialist directly.

## Watching Jesse's Scans

Jesse posts to `#market-update-jesse` on a fixed schedule (see [04-scheduling.md](04-scheduling.md)). You don't interact with Jesse directly — just read the channel.

### What Jesse's Output Looks Like

```
Red [Fed Policy 2026]

Fed — Waller Signals June Cut on Table

- Waller said June FOMC "live" if labor data softens
- Fed funds futures now price 68% chance of 25bps June cut (vs 52% yesterday)
- 10Y UST rallied 8bps to 4.12%

(Reuters)
<https://www.reuters.com/...>
```

### Interpreting Urgency Flags

- **Red** — Position-impacting. Central bank decisions, major data misses, geopolitical escalations. Read immediately.
- **Yellow** — Notable but expected. In-line data, scheduled events. Read when convenient.
- **Green** — Background. Context, minor developments. Skim.

### What Silence Means

If Jesse doesn't post during a scheduled scan slot, it means nothing noteworthy happened. Silence = no news. Jesse never sends "nothing to report" messages.

## Watching Agent-Teams

The `#agent-teams` channel shows you what's happening behind the scenes:

```
** **
🔧 **Jim assigned:** backtest momentum signal on CGB 10Y futures

2015-2025 sample, focus on regime robustness.

** **
🔬 **Albert assigned:** research 1998 Asian crisis parallels

China rates environment + current macro analogs.

** **
───

** **
✅ **Result:** elevated inflation risk agreed.

Disagreement remains on duration and transmission path.
```

This channel is read-only for you — Eve posts here automatically when coordinating agents.

## Best Practices

### Communication Style

- **Be direct.** Eve values directness. No need for pleasantries or formal requests.
- **Be casual.** Eve is designed for informal, honest conversation.
- **Be specific when delegating.** "Have Jim backtest X on Y data from Z to W" is better than "can Jim look at some trading stuff?"
- **Send half-formed ideas.** Eve is your second brain — she'll organize and connect dots.

### Getting the Most Out of Eve

- **Ask for opinions.** Eve has them. She's not a search engine.
- **Challenge her.** If her analysis seems weak, say so. She'll dig deeper.
- **Request debates.** When facing a complex decision, a Jim vs Albert debate surfaces perspectives you might miss.
- **Use her as a journal.** Send thoughts, reflections, trade ideas at any hour. She captures and connects everything.
- **Ask her to remember.** "Remember this" or "add this to my memory" — she'll update her files.
- **Check in on tasks.** "What's on my plate?" — she checks TASKS.md and reminds you.

### Things to Avoid

- **Don't ask Jesse for analysis.** Jesse reports facts. Ask Eve or Jim for analysis.
- **Don't expect instant agent responses.** Jim and Albert take time (they run on Opus). Eve will let you know when results are ready.
- **Don't worry about overwhelming Eve.** Send multiple messages, change topics mid-thread — she handles context.

## Discord Formatting Notes

- Eve uses bullet lists instead of tables (Discord doesn't render markdown tables well)
- All URLs are wrapped in `<>` to suppress embed previews
- Code blocks use triple backticks with language hints
- Eve can react with emoji to acknowledge without cluttering the chat

## Managing Tasks via Discord

Tell Eve to manage your task list:

- **Add:** "Add to tasks: finish regime detection writeup by March 30"
- **Check:** "What are my active tasks?"
- **Complete:** "Mark the regime writeup as done"
- **Remind:** Eve automatically checks TASKS.md during heartbeats and reminds you about upcoming due dates

## Asking Eve to Remember Things

- **Save:** "Remember that the 5Y CGB IRS is my main hedge right now"
- **Recall:** "What did I say about the CNH outlook last week?"
- **Forget:** "You can forget the thing about the Singapore rotation — it's off the table"

Eve stores important context in `MEMORY.md` (curated) and `memory/YYYY-MM-DD.md` (daily logs). She reviews and distills these during heartbeats.
