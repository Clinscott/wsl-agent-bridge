# Antigravity WSL Bridge

Use this for Google Antigravity/Gemini-style Windows profiles.

## Typical Roots

- Windows profile from WSL: `/mnt/c/Users/<WindowsUser>/.gemini`
- Host config: `/mnt/c/Users/<WindowsUser>/.gemini/config/config.json`
- MCP config variants seen in the field:
  - `/mnt/c/Users/<WindowsUser>/.gemini/config/mcp_config.json`
  - `/mnt/c/Users/<WindowsUser>/.gemini/antigravity-ide/mcp_config.json`
  - `/mnt/c/Users/<WindowsUser>/.gemini/antigravity-backup/mcp_config.json`
- Projects: `/mnt/c/Users/<WindowsUser>/.gemini/projects.json`
- WSL skills: `/home/<WSLUser>/.gemini/skills`
- Windows skills: `/mnt/c/Users/<WindowsUser>/.gemini/skills`

## MCP Pattern

Wrap WSL-hosted servers through `wsl.exe` from Windows JSON configs:

```json
{
  "mcpServers": {
    "example-server": {
      "command": "wsl.exe",
      "args": [
        "-d",
        "Ubuntu",
        "-e",
        "/home/<WSLUser>/.nvm/versions/node/<version>/bin/node",
        "/home/<WSLUser>/<repo>/server.js"
      ]
    }
  }
}
```

For TypeScript servers, prefer a checked-in launcher script or absolute `node`
plus absolute loader path. Do not rely on `npx`, `tsx`, or shell aliases unless
the app is proven to load the same shell environment.

## Hooks

Only add hooks after the sync script has passed dry run:

```json
{
  "hooks": {
    "sessionStart": "wsl.exe -d Ubuntu -e bash -lc '~/.gemini/sync_two_way.sh --safe'",
    "sessionEnd": "wsl.exe -d Ubuntu -e bash -lc '~/.gemini/sync_two_way.sh --safe'"
  }
}
```

If the app uses a different hook schema, preserve existing keys and follow the
local config shape instead of forcing this example.

## Project Registration

Use UNC roots for Windows UI project pickers:

```text
\\wsl.localhost\Ubuntu\home\<WSLUser>\<ParentRepoDir>
```

Fallback:

```text
\\wsl$\Ubuntu\home\<WSLUser>\<ParentRepoDir>
```

Verify that Antigravity opens the WSL project and that commands run in WSL, not
against copied Windows files.
