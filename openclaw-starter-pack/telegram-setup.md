# Telegram Setup Guide

This guide walks you through connecting OpenClaw to Telegram.

## Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts:
   - Choose a **display name** (e.g., "My AI Assistant")
   - Choose a **username** (must end in `bot`, e.g., `my_ai_bot`)
4. BotFather gives you a **token** like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`
5. **Save this token** — you'll need it for the config

### Optional Bot Settings (via BotFather)

Send these commands to @BotFather to configure your bot:

- `/setdescription` — set what users see before starting the bot
- `/setuserpic` — upload a profile picture
- `/setcommands` — set slash commands (optional, OpenClaw handles this)

### Enable Group Messages (if using groups)

By default, bots only see messages that mention them. To let the bot see all messages:

1. Send `/mybots` to @BotFather
2. Select your bot
3. Go to **Bot Settings** → **Group Privacy**
4. Set to **Disabled** (this ENABLES the bot to read all group messages)

Yes, the naming is confusing — "disabling" group privacy means the bot CAN read messages.

## Step 2: Get Your Telegram User ID

Your user ID is a number (not your username). To find it:

1. Search for **@userinfobot** on Telegram
2. Send it any message
3. It replies with your numeric user ID (e.g., `123456789`)
4. **Save this number**

## Step 3: Create a Group (Optional)

If you want a coordination channel for agent-to-agent visibility:

1. Create a new Telegram group
2. Add your bot to the group
3. Send a message in the group
4. To get the group's chat ID, you can either:
   - Use `@userinfobot` (forward a message from the group)
   - Or run: `curl https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` and look for the `chat.id` field
5. Group chat IDs are typically negative numbers (e.g., `-1001234567890`)

## Step 4: Fill in the Config

Open `openclaw.template.json` and replace these Telegram placeholders:

| Placeholder | What to Put | Example |
|------------|-------------|---------|
| `YOUR_TELEGRAM_BOT_TOKEN` | Bot token from BotFather | `123456:ABC-DEF1234...` |
| `YOUR_TELEGRAM_USER_ID` | Your numeric user ID | `123456789` |
| `YOUR_GROUP_CHAT_ID` | Group chat ID (if using groups) | `-1001234567890` |

These appear in:
- `channels.telegram.token`
- `channels.telegram.allowedUsers`
- `channels.telegram.groups`
- `channels.telegram.execApprovals.approvers`
- `tools.elevated.allowFrom.telegram`

## Step 5: Verify

After starting OpenClaw:

1. Open your Telegram chat with the bot
2. Send `hello`
3. The bot should respond

If it doesn't respond:
- Check `openclaw doctor` for config errors
- Make sure the token is correct
- Make sure your user ID is in the allowedUsers list

## Multi-Bot Setup (Multiple Agents)

If you want each agent to have its own Telegram bot (like separate Discord bots):

1. Create additional bots with BotFather (one per agent)
2. Add each bot's token to the config under `channels.telegram.accounts`:

```json
"accounts": {
  "main": {
    "token": "TOKEN_FOR_MAIN_BOT"
  },
  "coder": {
    "token": "TOKEN_FOR_CODER_BOT"
  },
  "researcher": {
    "token": "TOKEN_FOR_RESEARCHER_BOT"
  }
}
```

3. Add matching bindings so each bot routes to the right agent

This is optional — you can start with a single bot and add more later.

## Troubleshooting

**Bot doesn't respond in groups:**
- Check that Group Privacy is disabled (BotFather → Bot Settings → Group Privacy → Disabled)
- Check that the group chat ID is in the config

**"Unauthorized" errors:**
- Your bot token is wrong. Get a fresh one from BotFather.

**Messages delayed:**
- Telegram bots use polling by default. This is normal — slight delays (1-2s) are expected.
