"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================

MISSION:
    Give every chat a tiny spider friend that expresses emotions
    through ASCII art, one command at a time.

============================================================================
Pure Python Docker entrypoint. Reads PUID/PGID from environment,
fixes ownership of writable directories, drops privileges, then
execs the application.
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import os
import sys
import pwd
import grp


DEFAULT_UID = 1000
DEFAULT_GID = 1000
APP_DIR = "/app"
WRITABLE_DIRS = ["/app/logs"]


def main() -> None:
    puid = int(os.environ.get("PUID", DEFAULT_UID))
    pgid = int(os.environ.get("PGID", DEFAULT_GID))

    print(f"[entrypoint] Configuring UID={puid} GID={pgid}")

    # Ensure writable directories exist and have correct ownership
    for d in WRITABLE_DIRS:
        os.makedirs(d, exist_ok=True)
        os.chown(d, puid, pgid)

    # Drop privileges: set group first, then user
    try:
        os.setgid(pgid)
        os.setuid(puid)
    except PermissionError:
        print(
            f"[entrypoint] WARNING: Cannot drop to UID={puid}/GID={pgid}. "
            f"Running as UID={os.getuid()}/GID={os.getgid()}.",
            file=sys.stderr,
        )

    print(f"[entrypoint] Running as UID={os.getuid()} GID={os.getgid()}")

    # Exec the application (replaces this process)
    cmd = sys.argv[1:] if len(sys.argv) > 1 else ["python", "src/main.py"]
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
