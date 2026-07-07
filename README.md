<p align="center">
  <img src="https://raw.githubusercontent.com/PleasePrompto/ductor/main/ductor_bot/messenger/telegram/ductor_images/logo_text.png" alt="jarvis" width="100%" />
</p>

<p align="center">
  <strong>Jarvis — Claude Code, Codex CLI, Gemini CLI, and Antigravity CLI as your coding assistant — on Telegram, Matrix, and Discord.</strong><br>
  Uses only official CLIs. Nothing spoofed, nothing proxied. Multi-transport, automation, and sub-agents in one runtime.
</p>

<p align="center">
  <a href="https://github.com/Vi-kysik/Jarvis/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Vi-kysik/Jarvis" alt="License" /></a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> &middot;
  <a href="#how-chats-work">How chats work</a> &middot;
  <a href="#commands">Commands</a> &middot;
  <a href="docs/README.md">Docs</a>
</p>

---

> [!IMPORTANT]
> **Claude `-p` billing changed (effective 2026-06-15):** Anthropic moved Claude Code headless mode (`claude -p`) out of the Pro/Max/Team/Enterprise subscription pool. Jarvis's Claude provider runs headless, so on a Claude **subscription** these calls now count as extra/paid usage at standard API rates (the interactive TUI stays in the subscription). The `-p` flag still works; only billing changed. A clean console-based approach is being evaluated. In the meantime you can use **Codex** or **AGY (Antigravity)** as the provider — those are unaffected. Details and status: [#154](https://github.com/PleasePrompto/ductor/issues/154).

If you want to control Claude Code, Google's Gemini CLI, OpenAI's Codex CLI, or Antigravity CLI via Telegram, Matrix, or Discord, build automations, or manage multiple agents easily — Jarvis is the right tool for you. The messaging layer is modular: Telegram, Matrix, and Discord ship today, and new transports plug into the same transport-agnostic core.

Jarvis runs on your machine and sends simple console commands as if you were typing them yourself, so you can use your active subscriptions (Claude Max, Google AI Ultra, etc.) directly. No API proxying, no SDK patching, no spoofed headers. Just the official CLIs, executed as subprocesses, with all state kept in plain JSON and Markdown under `~/.jarvis/`.

<p align="center">
  <img src="https://raw.githubusercontent.com/PleasePrompto/ductor/main/docs/images/ductor-start.jpeg" alt="Jarvis /start screen" width="49%" />
  <img src="https://raw.githubusercontent.com/PleasePrompto/ductor/main/docs/images/ductor-quick-actions.jpeg" alt="Jarvis quick action buttons" width="49%" />
</p>

## Quick start

```bash
git clone https://github.com/Vi-kysik/Jarvis.git
cd Jarvis
pipx install .
jarvis
```

The onboarding wizard handles CLI checks, transport setup (Telegram, Discord, or Matrix), timezone, optional Docker, and optional background service install.

**Requirements:** Python 3.11+, at least one CLI installed (`claude`, `codex`, `gemini`, or `agy`), and either:

- a Telegram Bot Token from [@BotFather](https://t.me/BotFather), or
- a Discord Bot Token, or
- a Matrix account on a homeserver

Detailed setup: [`docs/installation.md`](docs/installation.md)

## How chats work

Jarvis gives you multiple ways to interact with your coding agents. Each level builds on the previous one.

### 1. Single chat (your main agent)

This is where everyone starts. You get a private 1:1 chat with your bot (Telegram, Matrix, or Discord). Every message goes to the CLI you have active (`claude`, `codex`, `gemini`, or `agy`), responses stream back in real time.

```text
You:   "Explain the auth flow in this codebase"
Bot:   [streams response from Claude Code]

You:   /model
Bot:   [interactive model/provider picker]

You:   "Now refactor the parser"
Bot:   [streams response, same session context]
```

This single chat is all you need. Everything else below is optional.

### 2. Groups with topics (multiple isolated chats)

**Telegram:** Create a group, enable topics (forum mode), and add your bot.
**Matrix:** Invite the bot to multiple rooms — each room is its own context.

Every topic (Telegram) or room (Matrix) becomes an isolated chat with its own CLI context.

```text
Group: "My Projects"
  ├── General           ← own context (isolated from your single chat)
  ├── Topic: Auth       ← own context
  ├── Topic: Frontend   ← own context
  ├── Topic: Database   ← own context
  └── Topic: Refactor   ← own context
```

That's 5 independent conversations from a single group. Your private single chat stays separate too — 6 total contexts, all running in parallel.

Each topic can use a different model. Run `/model` inside a topic to change just that topic's provider.

All chats share the same `~/.jarvis/` workspace — same tools, same memory, same files. The only thing isolated is the conversation context.

### 3. Named sessions (extra contexts within any chat)

Need to work on something unrelated without losing your current context? Start a named session. It runs inside the same chat but has its own CLI conversation.

```text
You:   "Let's work on authentication"        ← main context builds up
Bot:   [responds about auth]

/session Fix the broken CSV export            ← starts session "firmowl"
Bot:   [works on CSV in separate context]

You:   "Back to auth — add rate limiting"     ← main context is still clean
Bot:   [remembers exactly where you left off]

@firmowl Also add error handling              ← follow-up to the session
```

Sessions work everywhere — in your single chat, in group topics, in sub-agent chats.

### 4. Background tasks (async delegation)

Any chat can delegate long-running work to a background task. You keep chatting while the task runs autonomously. When it finishes, the result flows back into your conversation.

```text
You:   "Research the top 5 competitors and write a summary"
Bot:   → delegates to background task, you keep chatting
Bot:   → task finishes, result appears in your chat
```

Each task gets its own memory file (`TASKMEMORY.md`) and can be resumed with follow-ups.

### 5. Sub-agents (fully isolated second agent)

Sub-agents are completely separate bots — own chat, own workspace, own memory, own CLI auth, own config settings. Each sub-agent can use a different transport.

```bash
jarvis agents add codex-agent    # creates a new bot (needs its own token)
```

Sub-agents live under `~/.jarvis/agents/<name>/` with their own workspace, tools, and memory — fully isolated from the main agent.

### Comparison

| | Single chat | Group topics | Named sessions | Background tasks | Sub-agents |
|---|---|---|---|---|---|
| **What it is** | Your main 1:1 chat | One topic = one chat | Extra context in any chat | "Do this while I keep working" | Separate bot, own everything |
| **Context** | One per provider | One per topic per provider | Own context per session | Own context, result flows back | Fully isolated |
| **Workspace** | `~/.jarvis/` | Shared with main | Shared with parent chat | Shared with parent agent | Own under `~/.jarvis/agents/` |
| **Config** | Main config | Shared with main | Shared with parent chat | Shared with parent agent | Own config |
| **Setup** | Automatic | Create group + enable topics | `/session <prompt>` | Automatic or "delegate this" | `jarvis agents add` |

### How it all fits together

```text
~/.jarvis/                          ← shared workspace (tools, memory, files)
  │
  ├── Single chat                   ← main agent, private 1:1
  │     ├── main context
  │     └── named sessions
  │
  ├── Group: "My Projects"          ← same agent, same workspace
  │     ├── General (own context)
  │     ├── Topic: Auth (own context, own model)
  │     ├── Topic: Frontend (own context)
  │     └── each topic can have named sessions too
  │
  └── agents/codex-agent/           ← sub-agent, fully isolated workspace
        ├── own single chat
        ├── own group support
        ├── own named sessions
        └── own background tasks
```

## Features

- **Multi-transport** — Telegram, Discord, and Matrix simultaneously, or pick one
- **Multi-language** — UI in English, Deutsch, Nederlands, Français, Русский, Español, Português
- **Real-time streaming** — live message edits (Telegram) or segment-based output (Matrix)
- **Telegram reasoning + tool UX controls** — optional reasoning stream, live tool progress, and separate thinking indicator controls
- **Quoted-reply context** — replying to a message (Telegram) carries the cited text into the agent prompt, so follow-ups like "expand on this" keep their reference
- **Four coding agents** — Claude Code, Codex CLI, Gemini CLI, and Antigravity (`agy`), switchable per chat/topic with `/model` (never blocks, even during active processes)
- **Persistent memory** — plain Markdown files that survive across sessions
- **Memory maintenance** — pre-compaction flush, optional reflection cadence, and LLM-driven compaction
- **Cron jobs** — in-process scheduler with timezone support, per-job overrides, optional silent-on-success, result routing to originating chat
- **Webhooks** — `wake` (inject into active chat) and `cron_task` (isolated task run) modes
- **Heartbeat** — proactive checks with per-target settings, group/topic support, chat validation
- **Image processing** — auto-resize and WebP conversion for incoming images (configurable)
- **Media transcription hooks** — configurable external audio/video transcription commands for bundled media tools
- **Notification routing** — startup/upgrade lifecycle messages can target specific chats/topics
- **Task priorities** — `interactive`, `background`, and `batch` scheduling modes for background work
- **Telegram status reactions** — stage-aware emoji tracker on the user message while the agent works
- **Config hot-reload** — most settings update without restart (including language, scene, image)
- **Docker sandbox** — optional sidecar container with configurable host mounts
- **Service manager** — Linux (systemd), macOS (launchd), Windows (Task Scheduler)
- **Cross-tool skill sync** — shared skills across `~/.claude/`, `~/.codex/`, `~/.gemini/` (globally or per-provider toggleable)

## Messenger support

Telegram is the primary transport — full feature set, battle-tested, zero extra dependencies.

| Messenger | Status | Streaming | Buttons |
|---|---|---|---|
| **Telegram** | primary | Live message edits | Inline keyboards |
| **Discord** | supported | Segment-based | Reactions |
| **Matrix** | supported | Segment-based (new messages) | Emoji reactions |

All transports can run **in parallel** on the same agent:

```json
{"transports": ["telegram", "discord"]}
```

### Modular transport architecture

Each messenger is a self-contained module under `messenger/<name>/` implementing a shared `BotProtocol`. The core (orchestrator, sessions, CLI, cron, etc.) is completely transport-agnostic — it never knows which messenger delivered the message.

Adding a new messenger (Slack, Signal, ...) means implementing `BotProtocol` in a new sub-package and registering it — the rest of Jarvis works without changes.

## Auth

### Telegram

Jarvis uses a dual-allowlist model. Every message must pass both checks.

| Chat type | Check |
|---|---|
| **Private** | `user_id ∈ allowed_user_ids` |
| **Group** | `group_id ∈ allowed_group_ids` AND `user_id ∈ allowed_user_ids` |

All three settings are **hot-reloadable** — edit `config.json` and changes take effect within seconds.

> **Privacy Mode:** Telegram bots have Privacy Mode enabled by default and only see `/commands` in groups. To let the bot see all messages, make it a **group admin** or disable Privacy Mode via BotFather (`/setprivacy` → Disable). If changed after joining, remove and re-add the bot.

**Group management:** When the bot is added to a group not in `allowed_group_ids`, it warns and auto-leaves. Use `/where` to see tracked groups and their IDs.

**Channel allowlist:** Telegram channels are tracked separately via `allowed_channel_ids`. Unauthorized channels are announced and auto-left on join/audit just like unauthorized groups.

> **Tip — adding a group for the first time:**
> 1. Create a Telegram group, enable topics if you want isolated chats
> 2. Add the bot and make it **admin** (required for full message access)
> 3. Send a message mentioning `@your_bot` — the bot won't respond yet
> 4. In your private chat with the bot, run `/where` — you'll see the group listed under "Rejected" with its ID
> 5. Tell the bot: *"Add this as an allowed group in the config"* — it updates `config.json` for you
> 6. Run `/restart` — the bot now responds in the group

### Matrix

Matrix auth uses room and user allowlists in the `matrix` config block. The bot logs in on first start, then persists `access_token` and `device_id` for subsequent runs.

## Language

Jarvis's UI is available in multiple languages. Set in `config.json`:

```json
{"language": "ru"}
```

Supported: `en`, `de`, `nl`, `fr`, `ru`, `es`, `pt`. Hot-reloadable.

## Commands

| Command | Description |
|---|---|
| `/model` | Interactive model/provider selector |
| `/new` | Reset the configured default-provider session for this chat/topic |
| `/reset` | Reset the currently active provider session for this chat/topic |
| `/stop` | Stop current message and discard queued messages |
| `/interrupt` | Interrupt current message, queued messages continue |
| `/stop_all` | Kill everything — all messages, sessions, tasks, all agents |
| `/status` | Session/provider/auth status |
| `/memory` | Show persistent memory |
| `/session <prompt>` | Start a named background session |
| `/sessions` | View/manage active sessions |
| `/tasks` | View/manage background tasks |
| `/cron` | Interactive cron management |
| `/showfiles` | Browse `~/.jarvis/` |
| `/diagnose` | Runtime diagnostics |
| `/upgrade` | Check/apply updates |
| `/agents` | Multi-agent status |
| `/agent_commands` | Multi-agent command reference |
| `/where` | Show tracked chats/groups |
| `/info` | Version + links |

`/new` is intentionally a factory reset for the current `SessionKey`: it clears the bucket tied to the configured default model/provider for that chat or topic, not whichever provider you last switched to temporarily via `/model`. Use `/reset` when you want to clear the provider bucket that is currently active in that chat or topic.

## Common CLI commands

```bash
jarvis                  # Start bot (auto-onboarding if needed)
jarvis onboarding       # Re-run setup wizard
jarvis reset            # Full reset + onboarding
jarvis stop             # Stop bot
jarvis restart          # Restart bot
jarvis upgrade          # Upgrade and restart
jarvis status           # Runtime status
jarvis help             # CLI overview
jarvis uninstall        # Remove bot + workspace

jarvis service install  # Install as background service
jarvis service status   # Show service status
jarvis service start    # Start service
jarvis service stop     # Stop service
jarvis service logs     # View service logs
jarvis service uninstall

jarvis docker enable    # Enable Docker sandbox
jarvis docker rebuild   # Rebuild sandbox container
jarvis docker mount /p  # Add host mount

jarvis agents list      # List configured sub-agents
jarvis agents add NAME  # Add a sub-agent
jarvis agents remove NAME

jarvis install matrix   # Install Matrix transport extra
jarvis install api      # Install API extra
```

## Workspace layout

```text
~/.jarvis/
  config/config.json                 # Bot configuration
  sessions.json                      # Chat session state
  tasks.json                         # Background task registry
  cron_jobs.json                     # Scheduled tasks
  agents.json                        # Sub-agent registry (optional)
  SHAREDMEMORY.md                    # Shared knowledge across all agents
  CLAUDE.md / AGENTS.md / GEMINI.md  # Rule files
  logs/
  workspace/
    memory_system/MAINMEMORY.md      # Persistent memory
    cron_tasks/ skills/ tools/       # Scripts and tools
    tasks/                           # Per-task folders
    telegram_files/ matrix_files/    # Media files (per transport)
    output_to_user/                  # Generated deliverables
  agents/<name>/                     # Sub-agent workspaces (isolated)
```

Full config reference: [`docs/config.md`](docs/config.md) — full example: [`config.example.json`](config.example.json)

## Why Jarvis?

Other projects manipulate SDKs or patch CLIs and risk violating provider terms of service. Jarvis simply runs the official CLI binaries as subprocesses — nothing more.

- Official CLIs only (`claude`, `codex`, `gemini`, `agy`)
- Rule files are plain Markdown (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`)
- Memory is one Markdown file per agent
- All state is JSON — no database, no external services

## Disclaimer

Jarvis runs official provider CLIs and does not impersonate provider clients. Validate your own compliance requirements before unattended automation.

- [Anthropic Terms](https://www.anthropic.com/policies/terms)
- [OpenAI Terms](https://openai.com/policies/terms-of-use)
- [Google Terms](https://policies.google.com/terms)

## Contributing

```bash
git clone https://github.com/Yegorantonyuk/Albert.git
cd Albert
uv sync --extra dev
```

Run checks with [just](https://github.com/casey/just):

```bash
just check   # linters + type checks (parallel)
just test    # test suite
just fix     # auto-fix formatting and lint issues
```

Or directly with uv:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy ductor_bot
```

Zero warnings, zero errors.

## License

[MIT](LICENSE)
