# Spooder — Docker Secrets

This directory holds Docker Secret files for the Spooder bot.
**These files are gitignored and must never be committed.**

## Required Secrets

| File | Purpose | Example Value |
|------|---------|---------------|
| `spooder_fluxer_token` | Fluxer bot token | `FluxerBot.XXXX.YYYY` |

## Setup

1. Copy the example below and fill in your real token:

```bash
echo "YOUR_FLUXER_BOT_TOKEN_HERE" > spooder_fluxer_token
```

2. Ensure permissions are restrictive:

```bash
chmod 600 spooder_fluxer_token
```

3. The `docker-compose.yml` mounts this file as a Docker Secret
   at `/run/secrets/spooder_fluxer_token` inside the container.
