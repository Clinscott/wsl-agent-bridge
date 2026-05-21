# Claude WSL Bridge

Use this for Claude Desktop or Claude Code when the app/config lives on Windows
and the target repo/runtime lives in WSL.

## Typical Roots

Claude installs vary by product and version. Discover first; do not hardcode.
Common Windows-side locations to check from WSL:

- `/mnt/c/Users/<WindowsUser>/AppData/Roaming/Claude`
- `/mnt/c/Users/<WindowsUser>/.claude`
- `/mnt/c/Users/<WindowsUser>/.config/claude`
- Project memory files named `CLAUDE.md`

## MCP Pattern

Claude Desktop commonly uses JSON MCP server entries. For WSL-hosted servers,
wrap through `wsl.exe`:

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

For Claude Code, prefer CLI-managed MCP config when available:

```bash
claude mcp add example-server --scope user -- wsl.exe -d Ubuntu -e /home/<WSLUser>/.nvm/versions/node/<version>/bin/node /home/<WSLUser>/<repo>/server.js
claude mcp list
```

Then inspect the resulting config. Preserve the product's existing schema.

## Project Memory

For repo instructions, keep `CLAUDE.md` in the WSL repo itself. Do not sync it
into an unrelated Windows copy of the repo. If a Windows UI asks for a folder,
point it at:

```text
\\wsl.localhost\Ubuntu\home\<WSLUser>\<repo>
```

## Verification

Verify from Windows app side:

```powershell
wsl.exe -d Ubuntu -e bash -lc 'cd /home/<WSLUser>/<repo> && pwd && ls CLAUDE.md 2>/dev/null || true'
```

For MCP, run the product's MCP list/diagnostic command if available, then smoke
the server directly with the same `wsl.exe` args used in config.

## Common Failures

- Claude sees a Windows copy instead of WSL repo: re-register using UNC path.
- MCP server launches in Windows and cannot find Linux paths: wrap with
  `wsl.exe -d <Distro> -e`.
- Server works in an interactive WSL shell only: replace aliases with absolute
  runtime paths.
