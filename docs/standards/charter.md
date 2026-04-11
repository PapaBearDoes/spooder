# Clean Architecture Charter — Spooder

## Sacred Principles - NEVER TO BE VIOLATED

**Version**: v1.0.0
**Last Modified**: 2026-04-05
**Repository**: https://github.com/PapaBearDoes/spooder

---

# 🎯 SPOODER VISION (Never to be violated):

## **Spooder Gives the Chat a Tiny Spider Friend**:
1. **Express**  → Let anyone render spider emotions in chat with ASCII art
2. **Delight**  → Bring personality to conversations with a simple command
3. **Endure**   → Run without interruption so spooder is always ready to emote

---

## 🏛️ **IMMUTABLE ARCHITECTURE RULES**

### **Rule #1: Factory Function Pattern - MANDATORY**
- **ALL managers and handlers MUST use factory functions** — `create_[name]()`
- **NEVER call constructors directly**
- **Factory functions enable**: dependency injection, testing, consistency
- **Examples**: `create_config_manager()`, `create_spooder_handler()`

### **Rule #2: Dependency Injection - REQUIRED**
- **All managers/handlers accept dependencies through constructor parameters**
- **Logging manager is always injected; config manager where needed**
- **Additional managers passed as named parameters**
- **Clean separation of concerns maintained**

### **Rule #3: Additive Development - STANDARD**
- **New functionality ADDS capability, never REMOVES**
- **Maintain backward compatibility within a component**
- **Each feature builds on the previous foundation**

### **Rule #4: Static Configuration - SACRED**

Spooder is a single-purpose bot. All configuration is static — loaded once at startup
and never changed at runtime without a container restart. There is no dynamic config
layer, no database-backed settings, and no dashboard.

#### **Static Config — Bot-process settings**

| Type | Sensitive? | Storage | Examples |
|------|-----------|---------|---------|
| Bot token | ✅ Yes | Docker Secrets | `spooder_fluxer_token` |
| Log level, command prefix | ❌ No | `.env` file | `SPOODER_LOG_LEVEL`, `SPOODER_COMMAND_PREFIX` |

The config stack:
```
.env file                 ← non-sensitive runtime values (not committed)
      ↓ overridden by
Docker Secrets            ← sensitive values only (never in .env or source)
```

There is no JSON config layer and no database-backed config in Spooder.

#### **Secret Naming Convention**
Spooder uses `spooder_{purpose}` for all Docker Secret filenames:

```
spooder/
└── secrets/
    └── spooder_fluxer_token       ← Fluxer bot token
```

All `secrets/` directories are gitignored. Only `secrets/README.md` is committed.

#### **Environment Variable Naming Convention**
Static (non-sensitive) config uses `SPOODER_{CATEGORY}_{NAME}` in SCREAMING_SNAKE_CASE:

```bash
SPOODER_LOG_LEVEL=INFO
SPOODER_COMMAND_PREFIX=!spooder
```

#### **Reading Secrets in Python**
```python
def _read_secret(path: str) -> str:
    """Read a Docker Secret from its file path. Strips trailing whitespace."""
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(f"Docker Secret not found at: {path}")
    except PermissionError:
        raise RuntimeError(f"Cannot read Docker Secret at: {path} — permission denied")
```

#### **Red Flags**
- ❌ Sensitive values in `.env`, compose files, or source code
- ❌ Non-sensitive values stored as Docker Secrets (unnecessary complexity)
- ❌ `.env` variables undocumented in `.env.template`
- ❌ Creating new secrets without auditing existing ones first


### **Rule #5: Resilient Error Handling - PRODUCTION CRITICAL**
- **Invalid user input gets a friendly error**, not a crash
- **Gateway disconnects trigger automatic reconnection** via session resume
- **Unknown emotions get a help message** listing valid options
- **System prioritizes operational continuity** — the bot should never crash from user input
- **Unrecognized commands are silently ignored** (don't spam the channel)

### **Rule #6: File Versioning System - MANDATORY**
- **ALL code files MUST include version headers** in the format `v[Major].[Minor].[Patch]`
- **Version format**:
  - `v1.0.0` — initial release
  - `v1.1.0` — new feature or meaningful change
  - `v1.1.1` — bug fix or small improvement
- **Header placement**: At the top of each file in the module docstring
- **Version increments**: Required for each meaningful change

#### **Required Version Header Format — Spooder Standard:**

```python
"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================

MISSION:
    Give every chat a tiny spider friend that expresses emotions
    through ASCII art, one command at a time.

============================================================================
{File Description — plain English, one or two sentences}
----------------------------------------------------------------------------
FILE VERSION: v{Major}.{Minor}.{Patch}
LAST MODIFIED: {YYYY-MM-DD}
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""
```

### **Rule #7: Dedup Guards - MANDATORY**

All Fluxer gateway events fire twice (confirmed platform bug). Every handler MUST
implement a time-windowed dedup guard.

#### **Dedup Guard Pattern**

```python
import time

class ExampleHandler:
    def __init__(self, ...):
        self._recent_events: dict[str, float] = {}
        self._dedup_window: float = 5.0  # seconds

    def _is_duplicate(self, key: str) -> bool:
        now = time.monotonic()
        last = self._recent_events.get(key, 0.0)
        if now - last < self._dedup_window:
            return True
        self._recent_events[key] = now
        return False

    async def handle_message(self, payload: dict) -> None:
        dedup_key = f"{payload.get('author', {}).get('id')}:{payload.get('id')}"
        if self._is_duplicate(dedup_key):
            return
        # ... handler logic ...
```

Use a **time-windowed dict**, not a set. A set grows without bound. The time-window
dict self-cleans: old keys are overwritten and aged out.


### **Rule #8: Backslash Escaping for Spider Legs - SACRED**

Spooder uses real `/\` characters for spider legs. Fluxer's markdown engine treats
`\` as an escape character and strips single backslashes. To render a single `\` in
chat, the REST API payload must contain `\\` (double backslash).

#### **Escaping Chain**
```
Python string:  /\\      (3 chars: / \ \)
json.dumps:     /\\\\    (JSON escapes each \ to \\)
Fluxer receives: /\\     (JSON decoded back to /\\)
Fluxer renders:  /\      (markdown un-escapes \\ to \)
```

In Python source code, the leg pair constant is `"/\\\\"` which produces the
Python string `/\\`.

#### **Spider Anatomy**
```
/\/\^^/\/\ -> Spooder Said: She is happy!
```

- **Legs**: Four pairs of `/\` — two on each side of the eyes
- **Eyes**: Two-character string from the emotions map, determined by the `<emotion>` argument
- **Arrow**: ` -> ` separator between spider and message
- **Prefix**: `Spooder Said: ` before the user's message text

#### **Command Format**
```
!spooder <emotion> <message>
```

#### **Example Output**
```
/\/\^^/\/\ -> Spooder Said: She is happy!
/\/\><\/\/\ -> Spooder Said: Don't touch my web!
/\/\;;/\/\ -> Spooder Said: It's raining on my web...
```

#### **Why Double-Escaped Backslashes?**
Fluxer's markdown engine treats `\` as an escape character — both in user-typed
messages and in bot REST API payloads. A single `\` gets stripped. Sending `\\`
through the REST API causes Fluxer to render a single `\`, giving Spooder
properly formed `/\` legs at normal text width.

#### **Red Flags**
- ❌ Using single backslashes in spider leg rendering (Fluxer will strip them)
- ❌ Using Unicode box-drawing characters (render at double width in Fluxer)
- ❌ Hardcoding the spider string — always assemble from the leg constants and emotions map


### **Rule #9: LoggingConfigManager with Colorization - MANDATORY**

All logging MUST use `LoggingConfigManager` for consistent, colorized output.

#### **Required Colorization Scheme**
| Log Level | Color | ANSI Code | Symbol | Purpose |
|-----------|-------|-----------|--------|---------|
| CRITICAL | Bright Red (Bold) | `\033[1;91m` | 🚨 | System failures |
| ERROR | Red | `\033[91m` | ❌ | Exceptions, failed operations |
| WARNING | Yellow | `\033[93m` | ⚠️ | Degraded state, potential issues |
| INFO | Cyan | `\033[96m` | ℹ️ | Normal operations, status updates |
| DEBUG | Gray | `\033[90m` | 🔍 | Diagnostic details |
| SUCCESS | Green | `\033[92m` | ✅ | Successful completions (custom level 25) |

#### **Human-Readable Output Format**
```
[2026-04-05 14:30:00] INFO     | spooder.main              | ℹ️ Connected to Fluxer gateway
[2026-04-05 14:30:01] SUCCESS  | spooder.spooder_handler   | ✅ Rendered spider: happy
[2026-04-05 14:30:02] WARNING  | spooder.spooder_handler   | ⚠️ Unknown emotion: "grumpy"
```


### **Rule #10: Python 3.12 and Virtual Environment - MANDATORY**

All Docker containers MUST use Python 3.12 with virtual environments.

#### **Docker Multi-Stage Build Pattern**
```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv
```


### **Rule #11: Pure Python Docker Entrypoints with PUID/PGID - MANDATORY**

Spooder containers MUST use Pure Python entrypoint scripts with `tini` for PID 1.

#### **Required Architecture**
```
Container Start (as root)
  ↓
tini (PID 1) — signal handling, zombie reaping
  ↓
docker-entrypoint.py (Python)
  ├─ Read PUID/PGID from environment
  ├─ Fix ownership of writable directories
  ├─ Drop privileges (os.setgid → os.setuid)
  └─ exec application
  ↓
Bot process (runs as configured user)
```

#### **Environment Variables**
| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID to run the bot as |
| `PGID` | 1000 | Group ID to run the bot as |

#### **Dockerfile Requirements**
- Dockerfile installs `tini` in runtime stage
- Dockerfile does NOT use `USER` directive
- `ENTRYPOINT` uses tini + Python pattern
- Entrypoint reads `PUID`/`PGID` from environment
- Entrypoint drops privileges before exec


### **Rule #12: AI Assistant File System Tool Usage - MANDATORY**

When Claude or other AI assistants are editing project files, the correct tools must
be used for the file location.

#### **User's Computer (Windows paths, network paths)**
For files on the user's Windows machine or network shares (paths like `Y:\git\spooder\...`):

```
Desktop Commander:read_file        - Read file contents
Desktop Commander:edit_block       - Make targeted edits (preferred for changes)
Desktop Commander:write_file       - Write entire file (use for new files or full rewrites)
Desktop Commander:list_directory   - Browse directories
Desktop Commander:start_search     - Search for files or content
```

#### **Claude's Container**
For files in Claude's own container (`/home/claude/`, `/mnt/user-data/`):

```
str_replace    - Edit files in Claude's container
view           - Read files in Claude's container
create_file    - Create files in Claude's container
bash_tool      - Execute commands in Claude's container
```

#### **How to Identify File Location**
| Path Pattern | Location | Tools to Use |
|--------------|----------|-------------|
| `Y:\git\...` | User's Windows machine | `Desktop Commander:*` |
| `\\10.20.30.*\...` | Network share | `Desktop Commander:*` |
| `/home/claude/...` | Claude's container | `str_replace`, `view`, etc. |
| `/mnt/user-data/...` | Claude's container | `str_replace`, `view`, etc. |

#### **Best Practices**
1. **Prefer `Desktop Commander:edit_block`** over `write_file` for targeted changes
2. **Always read the file first** before editing to confirm current content
3. **Chunk writes to 25–30 lines maximum** — this is standard practice


---

## 🔧 **MANAGER IMPLEMENTATION STANDARDS**

### **Required Manager Structure:**
```python
"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================
{Manager Description}
----------------------------------------------------------------------------
FILE VERSION: v{Major}.{Minor}.{Patch}
LAST MODIFIED: {YYYY-MM-DD}
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

class [Manager]Manager:
    def __init__(self, [dependencies...], log) -> None:
        """Constructor with dependency injection. log is always last."""

    async def [operation](self, ...):
        """Async operations for network/API managers."""

    def [sync_operation](self, ...):
        """Sync operations for config/logging managers."""


async def create_[manager]_manager([parameters]) -> [Manager]Manager:
    """Async factory function for managers that require IO at startup."""
    ...

def create_[manager]_manager([parameters]) -> [Manager]Manager:
    """Sync factory function for managers that don't require IO at startup."""
    ...


__all__ = ['[Manager]Manager', 'create_[manager]_manager']
```

---

## 🕷️ **COMMAND BEHAVIOR**

### **Command Cleanup - MANDATORY**

When Spooder processes a `!spooder` command, the handler MUST:
1. **Delete the original command message** before posting the spider output
2. **Post the rendered spider** as a new message in the same channel

This creates a clean experience where the chat only shows the spider output, not the
raw command. The user's intent is conveyed through the spider, not the command syntax.

#### **Deletion Flow**
```
User sends: !spooder happy She is happy!
  ↓
Handler parses emotion + message
  ↓
DELETE the original message (REST API call)
  ↓
POST the spider: /\/\^^/\/\ -> Spooder Said: She is happy!
```

#### **Failure Handling**
- If message deletion fails (missing permissions, API error), **log a warning but still
  post the spider output**. The spider rendering is the primary goal; cleanup is secondary.
- The bot requires `Manage Messages` permission to delete other users' messages.
- If the bot lacks this permission, it should log a WARNING at startup and on each
  failed deletion attempt, but continue operating normally.

---

## 🏥 **PRODUCTION RESILIENCE PHILOSOPHY**

### **Operational Continuity Over Perfection**
Spooder should never crash from user input or transient failures. The bot
staying online is more important than any single command succeeding.

- **Unknown emotion** — respond with a help message listing valid emotions
- **Missing message** — respond with just the spider (no "Spooder Said:" text)
- **Gateway disconnect** — automatic reconnection via session resume
- **Message deletion failure** — log warning, still post the spider
- **Unrecognized command** — silent ignore

### **Error Handling Hierarchy**
1. **Unrecoverable errors** (missing bot token, can't reach Fluxer gateway): Fail-fast with clear log at startup
2. **Message deletion failure**: Log warning, continue with spider output
3. **Invalid user input**: Friendly help message, no crash
4. **Handler exception**: Log error with traceback, do not crash the process

---

## 🚨 **VIOLATION PREVENTION**

### **Before Making ANY Code Change:**
1. Does this maintain the factory function pattern? ✅ Required
2. Does this preserve all existing functionality? ✅ Required
3. Does this follow dependency injection principles? ✅ Required
4. Does this use the correct config layer (sensitive → secrets, non-sensitive → `.env`)? ✅ Required
5. Does this implement resilient error handling? ✅ Required
6. Does this include a proper file version header with `COMPONENT`? ✅ Required
7. Did I audit existing secrets/env vars before creating new ones? ✅ Required
8. Does this use LoggingConfigManager with standard colorization? ✅ Required
9. Does this use Python 3.12 with `/opt/venv`? ✅ Required
10. Am I using the correct file system tools for the file location? ✅ Required
11. Does the Dockerfile use a Pure Python entrypoint with tini? ✅ Required
12. Does every handler implement a dedup guard? ✅ Required
13. Does the handler delete the command message before posting? ✅ Required
14. Are spider legs using double-escaped backslashes (`/\\\\` in Python source), never single backslashes or Unicode? ✅ Required

### **Red Flags — IMMEDIATE STOP:**
- ❌ Direct constructor calls in production code
- ❌ Sensitive values in `.env`, compose files, or source code
- ❌ `print()` statements instead of LoggingConfigManager
- ❌ Missing file version headers or `COMPONENT` field
- ❌ Using `USER` directive in Dockerfile instead of entrypoint privilege dropping
- ❌ Bash scripts for Docker entrypoints
- ❌ Missing `tini` for PID 1 signal handling
- ❌ Missing dedup guard in any event handler
- ❌ Using single backslashes or Unicode characters for spider legs instead of double-escaped backslashes
- ❌ Posting spider output without first attempting to delete the command message
- ❌ Crashing on unknown emotions instead of showing a help message

---

## 🎯 **ARCHITECTURAL SUCCESS METRICS**

### **Code Quality:**
- ✅ All managers/handlers use factory functions
- ✅ All configuration externalized to `.env` / Docker Secrets
- ✅ Clean dependency injection throughout
- ✅ Production-ready resilient error handling
- ✅ Consistent file versioning with `COMPONENT` field across all code files
- ✅ No secrets in source control

### **Bot Reliability:**
- ✅ Every handler implements a dedup guard
- ✅ Command messages are deleted before spider output is posted
- ✅ Unknown emotions produce a help message, not a crash
- ✅ Spider legs use double-escaped backslashes for proper rendering
- ✅ Gateway reconnection works via session resume

### **Production Readiness:**
- ✅ Operational continuity under all failure modes
- ✅ Comprehensive, colorized logging for debugging
- ✅ PUID/PGID working correctly for volume mounts on Lofn

---

## 💪 **COMMITMENT**

**This bot serves the chat by providing:**
- **A fun, expressive spider friend** that anyone can summon
- **Clean command output** through automatic message deletion
- **Resilience** through graceful error handling and automatic recovery
- **Consistent rendering** through double-escaped backslashes that survive Fluxer's markdown engine

**Spooder is small, simple, and reliable. That's the whole point.**

---

**Status**: Living Document
**Authority**: Project Lead + AI Assistant Collaboration
**Enforcement**: Mandatory for ALL code changes
**Version**: v1.0.0

---

## 🏆 **ARCHITECTURE PLEDGE**

*"We commit to maintaining Clean Architecture principles with production-ready
resilience, consistent file versioning, and proper secrets management in every
code change — because even the smallest spider deserves a well-built web."*

---

**Eight legs, one command, zero crashes** 🕷️
