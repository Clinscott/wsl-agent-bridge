---
name: wsl-agent-bridge
description: >-
  Configures a persistent, symlink-preserving, bi-directional sync and
  path-translating bridge between a Windows host-side Antigravity/Codex IDE
  installation and a WSL Linux environment.
---

# WSL Agent Bridge

## Overview
This skill provides a step-by-step procedure to establish a persistent, transparent connection between a Windows-native agent environment (Antigravity or Codex) and a WSL Linux distribution (e.g., Ubuntu). It solves the path mismatch issues when files reside in WSL but commands are triggered from Windows, and handles bi-directional synchronization of agent skills and plugins while preserving symlinks.

## Dependencies
- **Windows Host OS**: Active installation of Antigravity or Codex
- **WSL Linux Distribution**: A running WSL instance (default: `Ubuntu`)
- **rsync**: Installed inside WSL (`sudo apt install rsync`)
- **wsl.exe**: Accessible from the Windows host Command Prompt/PowerShell

## Quick Start
1. Ensure your WSL distro has `rsync` installed:
   ```bash
   sudo apt update && sudo apt install -y rsync
   ```
2. Wrap your host's MCP server command inside `wsl.exe` to run natively in Linux:
   ```json
   "command": "wsl.exe",
   "args": ["-d", "Ubuntu", "-e", "/home/username/.nvm/versions/node/v25.8.1/bin/node", "path/to/server.js"]
   ```
3. Establish a bi-directional `rsync` sync script in WSL to bridge skill updates.

---

## Workflow

### 1. Configure Host MCP Servers for WSL Execution
Redirect Windows host tool execution to run natively inside WSL:
- For **Antigravity**: Edit `C:\Users\<WindowsUser>\.gemini\config\config.json`.
- For **Codex**: Edit `C:\Users\<WindowsUser>\.codex\config.toml`.
- Wrap the MCP server definitions under the `mcpServers` block.
- **Example configuration (`config.json`)**:
  ```json
  "mcpServers": {
    "<mcp-server-name>": {
      "command": "wsl.exe",
      "args": [
        "-d", "Ubuntu", "-e",
        "/home/<WSLUser>/.nvm/versions/node/v.../bin/node",
        "--import", "file:///home/<WSLUser>/<project-root>/node_modules/tsx/dist/loader.mjs",
        "/home/<WSLUser>/<project-root>/path/to/server.ts"
      ]
    }
  }
  ```

### 2. Deploy Symlink-Preserving Bi-Directional Sync
Create an automated script in WSL to sync custom skills and plugins between Windows and Linux without breaking symlinks in active Git repositories:
- Create the script `/home/<WSLUser>/.gemini/sync_two_way.sh` in WSL:
  ```bash
  #!/bin/bash
  WSL_SKILLS="/home/<WSLUser>/.gemini/skills/"
  WIN_SKILLS="/mnt/c/Users/<WindowsUser>/.gemini/skills/"
  WSL_PLUGINS="/home/<WSLUser>/.gemini/antigravity-cli/plugins/"
  WIN_PLUGINS="/mnt/c/Users/<WindowsUser>/.gemini/config/plugins/"

  mkdir -p "$WIN_SKILLS"
  mkdir -p "$WIN_PLUGINS"

  # Sync WSL -> Windows (dereferences symlinks to make scripts readable on Windows)
  rsync -auL --exclude "node_modules" --exclude ".git" "$WSL_SKILLS" "$WIN_SKILLS"
  rsync -auL "$WSL_PLUGINS" "$WIN_PLUGINS"

  # Sync Windows -> WSL (preserves and writes THROUGH existing symlinks to avoid destroying Git mappings)
  rsync -auK --exclude "node_modules" --exclude ".git" "$WIN_SKILLS" "$WSL_SKILLS"
  rsync -auK "$WIN_PLUGINS" "$WSL_PLUGINS"
  ```
- Grant executable permissions: `chmod +x ~/.gemini/sync_two_way.sh`.

### 3. Register IDE Session Hooks
Integrate the sync script into the IDE lifecycle so changes propagate automatically at start and end of sessions:
- Add the following hooks to your host's `config.json` (`.gemini/config/config.json`):
  ```json
  "hooks": {
    "sessionStart": "wsl.exe -d Ubuntu -e bash -lc \"~/.gemini/sync_two_way.sh\"",
    "sessionEnd": "wsl.exe -d Ubuntu -e bash -lc \"~/.gemini/sync_two_way.sh\""
  }
  ```

### 4. Register WSL Projects in IDE Sidebar
Configure the sidebar to recognize WSL repository locations:
- Create or update `C:\Users\<WindowsUser>\.gemini\projects.json`.
- Map the projects using Windows UNC paths pointing to the WSL instance:
  ```json
  {
    "projects": {
      "\\\\wsl.localhost\\Ubuntu\\home\\<WSLUser>\\<ParentRepoDir>": "<parent-slug>",
      "\\\\wsl.localhost\\Ubuntu\\home\\<WSLUser>\\<ParentRepoDir>\\<SubRepoDir1>": "<sub-slug-1>",
      "\\\\wsl.localhost\\Ubuntu\\home\\<WSLUser>\\<ParentRepoDir>\\<SubRepoDir2>": "<sub-slug-2>"
    }
  }
  ```
- Generate matching project workspace configurations in `C:\Users\<WindowsUser>\.gemini\config\projects\<project-slug>.json`.

### 5. Implement Path Translation
When running commands inside WSL that accept path arguments from the Windows host, implement a conversion step to rewrite Windows UNC or mapped drive paths to their local Linux path equivalents before processing:
- **Python Translation Helper**:
  ```python
  def translate_path(p_str: str) -> str:
      if not p_str:
          return p_str
      p_str = p_str.replace('\\', '/')
      # 1. Strip WSL UNC prefix
      for prefix in ["//wsl.localhost/Ubuntu", "//wsl$/Ubuntu"]:
          if p_str.startswith(prefix):
              res = p_str[len(prefix):]
              return res if res.startswith('/') else '/' + res
      # 2. Strip Windows mapped drive prefix (e.g. Z:)
      if p_str.lower().startswith("z:"):
          res = p_str[2:]
          return res if res.startswith('/') else '/' + res
      return p_str
  ```
- **TypeScript/JavaScript Translation Helper**:
  ```typescript
  function translatePath(p: string): string {
      if (!p) return p;
      let res = p.replace(/\\/g, '/');
      if (process.platform !== 'win32') {
          for (const prefix of ['//wsl.localhost/Ubuntu', '//wsl$/Ubuntu']) {
              if (res.startsWith(prefix)) {
                  const sub = res.slice(prefix.length);
                  return sub.startsWith('/') ? sub : '/' + sub;
              }
          }
          if (res.toLowerCase().startsWith('z:')) {
              const sub = res.slice(2);
              return sub.startsWith('/') ? sub : '/' + sub;
          }
      }
      return res;
  }
  ```

---

## Common Mistakes
- **Breaking Symlinks (Crucial)**: Running standard `rsync` from Windows to WSL without the `-K` (`--keep-dirlinks`) flag will overwrite WSL-side directory symlinks, turning them into standard physical folders and disconnecting them from active git repositories. Always use the `-auK` configuration.
- **Node/Python Path Mismatches**: Specifying global alias names (like `node` or `python`) inside `config.json` args. WSL non-login shells do not source profiles like `.bashrc` or NVM. Always specify absolute paths to binary runtimes (e.g., `/home/username/.nvm/versions/node/v.../bin/node`).
- **Parentheses in PATH**: If Windows environment variables contain parentheses (like `Program Files (x86)`), exporting them inside a non-interactive bash session can trigger parsing errors. Clean the environment or isolate path definitions using `env -i`.
