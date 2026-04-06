# Spooder 🕷️

**An emotive spider bot for Fluxer — giving every chat a tiny spider friend.**

Spooder takes a simple command and renders an ASCII spider with expressive eyes and a message, deleting the original command for a clean chat experience.

```
User types:  !spooder happy She is happy!
Chat shows:  ╱╲╱╲^^╱╲╱╲ -> Spooder Said: She is happy!
```

---

## How It Works

Type `!spooder <emotion> <message>` in any channel where Spooder is present. The bot deletes your command message and posts the spider in its place. The emotion determines the spider's eyes, and your message follows after "Spooder Said:".

```
╱╲╱╲^^╱╲╱╲ -> Spooder Said: She is happy!
╱╲╱╲><╱╲╱╲ -> Spooder Said: Don't touch my web!
╱╲╱╲;;╱╲╱╲ -> Spooder Said: It's raining on my web...
╱╲╱╲♥♥╱╲╱╲ -> Spooder Said: I love flies!
```

Type `!spooder` with no arguments to see all available emotions.

---

## Available Emotions

| Emotion | Eyes | Spider |
|---------|------|--------|
| happy | `^^` | `╱╲╱╲^^╱╲╱╲` |
| sad | `;;` | `╱╲╱╲;;╱╲╱╲` |
| angry | `><` | `╱╲╱╲><╱╲╱╲` |
| love | `♥♥` | `╱╲╱╲♥♥╱╲╱╲` |
| surprised | `OO` | `╱╲╱╲OO╱╲╱╲` |
| wink | `^~` | `╱╲╱╲^~╱╲╱╲` |
| sleepy | `--` | `╱╲╱╲--╱╲╱╲` |
| dead | `XX` | `╱╲╱╲XX╱╲╱╲` |
| confused | `??` | `╱╲╱╲??╱╲╱╲` |
| scared | `°°` | `╱╲╱╲°°╱╲╱╲` |
| shy | `..` | `╱╲╱╲..╱╲╱╲` |
| excited | `**` | `╱╲╱╲**╱╲╱╲` |
| suspicious | `¬¬` | `╱╲╱╲¬¬╱╲╱╲` |
| smug | `≖≖` | `╱╲╱╲≖≖╱╲╱╲` |
| dizzy | `@@` | `╱╲╱╲@@╱╲╱╲` |
| crying | `TT` | `╱╲╱╲TT╱╲╱╲` |
| sparkle | `✧✧` | `╱╲╱╲✧✧╱╲╱╲` |
| cool | `■■` | `╱╲╱╲■■╱╲╱╲` |
| blank | `  ` | `╱╲╱╲  ╱╲╱╲` |
| derp | `◉◉` | `╱╲╱╲◉◉╱╲╱╲` |
| uwu | `◡◡` | `╱╲╱╲◡◡╱╲╱╲` |

---

## Setup

### Prerequisites

- Docker and Docker Compose
- A Fluxer bot token

### 1. Clone the repository

```bash
git clone https://github.com/PapaBearDoes/spooder.git
cd spooder
```

### 2. Create your environment file

```bash
cp .env.template .env
```

Edit `.env` if you want to change the log level or command prefix (defaults are fine for most setups).

### 3. Add your bot token

```bash
echo "YOUR_FLUXER_BOT_TOKEN" > secrets/spooder_fluxer_token
chmod 600 secrets/spooder_fluxer_token
```

### 4. Build and run

```bash
docker compose up -d --build
```

### 5. Check logs

```bash
docker compose logs -f spooder
```

You should see colorized output confirming Spooder is connected and ready.

---

## Configuration

All configuration is static — loaded at startup from `.env` and Docker Secrets.

| Setting | Source | Default | Description |
|---------|--------|---------|-------------|
| `SPOODER_LOG_LEVEL` | `.env` | `INFO` | Log verbosity: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `SPOODER_COMMAND_PREFIX` | `.env` | `!spooder` | The command that triggers Spooder |
| `PUID` | `.env` | `1000` | Container user ID (match your host user) |
| `PGID` | `.env` | `1000` | Container group ID (match your host user) |
| `spooder_fluxer_token` | Docker Secret | — | Your Fluxer bot token (**required**) |

---

## Bot Permissions

Spooder needs the following Fluxer permissions:

| Permission | Why |
|------------|-----|
| Send Messages | To post the spider output |
| Manage Messages | To delete the user's command message before posting |
| Read Message Content | To see `!spooder` commands |

If `Manage Messages` is missing, Spooder will still work — it just won't be able to clean up the command message. A warning is logged on each failed deletion.

---

## Project Structure

```
spooder/
├── docs/standards/
│   └── charter.md              ← Architecture charter
├── src/
│   ├── main.py                 ← Entrypoint, gateway, signal handling
│   ├── handlers/
│   │   └── spooder_handler.py  ← Command parsing, dedup, render flow
│   ├── managers/
│   │   ├── config_manager.py   ← .env + Docker Secrets
│   │   └── logging_config_manager.py
│   └── utils/
│       └── emotions.py         ← Emotion map + spider builder
├── docker-entrypoint.py        ← PUID/PGID privilege dropping
├── Dockerfile                  ← Multi-stage Python 3.12 + tini
├── docker-compose.yml
├── .env.template
├── requirements.txt
├── secrets/
│   └── README.md               ← Secret setup instructions
└── .gitignore
```

---

## Technical Notes

### Why Unicode Spider Legs?

Fluxer interprets a leading `/` as a command prefix, which breaks the spider's ASCII legs (`/\/\`). Spooder uses Unicode box-drawing characters instead:

- `╱` (U+2571) replaces `/`
- `╲` (U+2572) replaces `\`

These render visually identical in chat but are invisible to Fluxer's command parser.

### Why Delete the Command Message?

Without deletion, the chat would show both the raw command and the spider output — doubling the noise. By removing the command first, only the spider appears, keeping conversations clean.

---

## Part of The Alphabet Cartel

Built with the same Clean Architecture principles as [Skald](https://github.com/PapaBearDoes/skald) and [Fluxarr](https://github.com/PapaBearDoes/fluxarr).

**Eight legs, one command, zero crashes** 🕷️
