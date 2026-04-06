#!/usr/bin/env python3
"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================
Pure-Python Docker entrypoint. Handles PUID/PGID privilege dropping
and exec's the bot process.
----------------------------------------------------------------------------
FILE VERSION: v1.1.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant (Charter Rule #11)
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple

COMPONENT_NAME = "spooder"
APP_USER = "appuser"
APP_GROUP = "appgroup"
DEFAULT_UID = 1000
DEFAULT_GID = 1000
WRITABLE_DIRECTORIES = ["/app/logs"]
DEFAULT_COMMAND = ["python", "src/main.py"]

RESET = "\033[0m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"


def log(level: str, msg: str) -> None:
    colors = {"INFO": CYAN, "SUCCESS": GREEN, "WARNING": YELLOW, "ERROR": RED}
    color = colors.get(level, RESET)
    print(f"{color}[{COMPONENT_NAME}] {level:<8}{RESET} {msg}", flush=True)


def get_puid_pgid() -> Tuple[int, int]:
    puid = int(os.environ.get("PUID", DEFAULT_UID))
    pgid = int(os.environ.get("PGID", DEFAULT_GID))
    return puid, pgid


def setup_user_and_permissions(puid: int, pgid: int) -> None:
    if os.geteuid() != 0:
        log("INFO", "Not running as root — skipping user setup")
        return
    subprocess.run(["groupmod", "-o", "-g", str(pgid), APP_GROUP], capture_output=True)
    subprocess.run(
        ["usermod", "-o", "-u", str(puid), "-g", str(pgid), APP_USER],
        capture_output=True,
    )
    for dir_path in WRITABLE_DIRECTORIES:
        path = Path(dir_path)
        if path.exists():
            os.chown(path, puid, pgid)
            for item in path.rglob("*"):
                try:
                    os.chown(item, puid, pgid)
                except PermissionError:
                    pass
    log("SUCCESS", f"Permissions set — PUID={puid} PGID={pgid}")


def drop_privileges(puid: int, pgid: int) -> None:
    if os.geteuid() != 0:
        return
    os.setgroups([])
    os.setgid(pgid)
    os.setuid(puid)
    log("SUCCESS", f"Dropped privileges to UID={puid} GID={pgid}")


def main() -> None:
    log("INFO", f"Starting {COMPONENT_NAME} entrypoint v1.1.0")
    puid, pgid = get_puid_pgid()
    log("INFO", f"Target identity — PUID={puid} PGID={pgid}")
    setup_user_and_permissions(puid, pgid)
    drop_privileges(puid, pgid)
    command = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_COMMAND
    log("INFO", f"Executing: {' '.join(command)}")
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
