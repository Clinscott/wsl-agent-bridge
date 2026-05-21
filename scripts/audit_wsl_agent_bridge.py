#!/usr/bin/env python3
"""Audit Windows-agent to WSL bridge prerequisites without mutating state."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def command_output(args: list[str], timeout: int = 5) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001 - audit should report, not crash.
        return False, str(exc)
    return proc.returncode == 0, proc.stdout.strip()


def exists(path: str) -> dict[str, Any]:
    p = Path(path)
    try:
        return {"path": path, "exists": p.exists(), "is_dir": p.is_dir(), "is_file": p.is_file()}
    except OSError as exc:
        return {
            "path": path,
            "exists": False,
            "is_dir": False,
            "is_file": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def discover_windows_users() -> list[str]:
    root = Path("/mnt/c/Users")
    if not root.exists():
        return []
    ignored = {"All Users", "Default", "Default User", "Public", "desktop.ini"}
    return sorted(p.name for p in root.iterdir() if p.is_dir() and p.name not in ignored)


def choose_windows_user(users: list[str]) -> str | None:
    if not users:
        return None
    scored: list[tuple[int, str]] = []
    for user in users:
        home = Path("/mnt/c/Users") / user
        score = 0
        for rel in [
            ".codex",
            ".gemini",
            ".claude",
            "AppData/Roaming/Claude",
            ".codex/config.toml",
            ".gemini/config/config.json",
        ]:
            try:
                present = (home / rel).exists()
            except OSError:
                present = False
            if present:
                score += 1
        scored.append((score, user))
    scored.sort(key=lambda item: (-item[0], item[1].lower()))
    return scored[0][1] if scored[0][0] > 0 else (users[0] if len(users) == 1 else None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--windows-user", help="Windows user profile name")
    parser.add_argument("--distro", default="Ubuntu", help="WSL distro name")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    wsl_user = getpass.getuser()
    windows_users = discover_windows_users()
    windows_user = args.windows_user or choose_windows_user(windows_users)
    win_home = f"/mnt/c/Users/{windows_user}" if windows_user else None

    wsl_exe = shutil.which("wsl.exe")
    rsync = shutil.which("rsync")
    node = shutil.which("node")
    python3 = shutil.which("python3")

    checks: dict[str, Any] = {
        "wsl_user": wsl_user,
        "distro": args.distro,
        "windows_users": windows_users,
        "selected_windows_user": windows_user,
        "tools": {
            "wsl.exe": wsl_exe,
            "rsync": rsync,
            "node": node,
            "python3": python3,
        },
        "wsl_profiles": {
            "codex": exists(f"/home/{wsl_user}/.codex"),
            "gemini": exists(f"/home/{wsl_user}/.gemini"),
            "claude": exists(f"/home/{wsl_user}/.claude"),
        },
        "windows_profiles": {},
        "versions": {},
    }

    if win_home:
        checks["windows_profiles"] = {
            "home": exists(win_home),
            "codex": exists(f"{win_home}/.codex"),
            "codex_config": exists(f"{win_home}/.codex/config.toml"),
            "gemini": exists(f"{win_home}/.gemini"),
            "gemini_config": exists(f"{win_home}/.gemini/config/config.json"),
            "gemini_projects": exists(f"{win_home}/.gemini/projects.json"),
            "claude_dotdir": exists(f"{win_home}/.claude"),
            "claude_roaming": exists(f"{win_home}/AppData/Roaming/Claude"),
        }

    for name, cmd in {
        "node": [node, "--version"] if node else None,
        "python3": [python3, "--version"] if python3 else None,
        "rsync": [rsync, "--version"] if rsync else None,
        "wsl": [wsl_exe, "-d", args.distro, "-e", "bash", "-lc", "printf ok"] if wsl_exe else None,
    }.items():
        if not cmd:
            checks["versions"][name] = {"ok": False, "output": "not found"}
            continue
        ok, out = command_output(cmd)
        checks["versions"][name] = {"ok": ok, "output": out.splitlines()[0] if out else ""}

    if args.json:
        print(json.dumps(checks, indent=2, sort_keys=True))
    else:
        for key, value in checks.items():
            print(f"{key}: {value}")

    hard_fail = not python3
    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
