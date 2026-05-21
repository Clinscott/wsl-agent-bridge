# Codex WSL Bridge

Use this for Codex Desktop or Codex CLI when Windows is the app shell and WSL is
the runtime.

## Typical Roots

- WSL profile: `/home/<WSLUser>/.codex`
- Windows profile from WSL: `/mnt/c/Users/<WindowsUser>/.codex`
- Windows config: `/mnt/c/Users/<WindowsUser>/.codex/config.toml`
- Stable WSL launcher: `/home/<WSLUser>/.codex/bin/wsl/codex`
- Windows app state:
  - `/mnt/c/Users/<WindowsUser>/.codex/.codex-global-state.json`
  - `/mnt/c/Users/<WindowsUser>/.codex/state_5.sqlite`

## MCP Pattern

Codex config is TOML, not Antigravity JSON. Use `[mcp_servers.<name>]` sections:

```toml
[mcp_servers.example_server]
command = "wsl.exe"
args = [
  "-d",
  "Ubuntu",
  "-e",
  "/home/<WSLUser>/.nvm/versions/node/<version>/bin/node",
  "/home/<WSLUser>/<repo>/server.js"
]
```

Useful checks:

```bash
codex mcp list
codex mcp get example_server
```

## WSL Launcher Check

From WSL:

```bash
/home/<WSLUser>/.codex/bin/wsl/codex --version
env -i HOME=/home/<WSLUser> PATH=/usr/bin:/bin /usr/bin/bash -lc '/home/<WSLUser>/.codex/bin/wsl/codex --version'
```

## Hashed Launcher Repair

If Codex Desktop reports:

```text
/home/<WSLUser>/.codex/bin/wsl/<hash>/codex: No such file or directory
```

repair the exact missing path by creating this executable file:

```text
/home/<WSLUser>/.codex/bin/wsl/<hash>/codex
```

```bash
#!/usr/bin/env bash
set -euo pipefail

exec /home/<WSLUser>/.codex/bin/wsl/codex "$@"
```

Then:

```bash
chmod 755 /home/<WSLUser>/.codex/bin/wsl/<hash>/codex
```

Then verify with the clean launch form:

```bash
env -i HOME=/home/<WSLUser> PATH=/usr/bin:/bin /usr/bin/bash -lc '/home/<WSLUser>/.codex/bin/wsl/<hash>/codex --version'
```

If maintaining this host, also run any local Codex profile audit skill/script
that checks project state and sqlite thread rows.

## Project Registration

Use WSL-native roots in runtime state and UNC roots only where the Windows UI
requires a folder picker:

```text
/home/<WSLUser>/<ParentRepoDir>
\\wsl.localhost\Ubuntu\home\<WSLUser>\<ParentRepoDir>
```

If backing state looks correct but the UI still shows no project, use the app's
"Use existing folder" flow once with the UNC path. Some app versions write
private UI state only after that manual selection.
