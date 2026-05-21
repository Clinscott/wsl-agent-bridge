---
name: wsl-agent-bridge
description: >-
  Set up, audit, or repair Windows-hosted Antigravity, Codex, and Claude agent
  environments so they can work reliably against WSL projects, runtimes, MCP
  servers, skills, and plugins without breaking symlinks or path handling.
---

# WSL Agent Bridge

Use this when a Windows-native agent app must operate on a WSL repo or run
tools inside WSL. It supports the big three surfaces:

- **Antigravity**: Gemini/Antigravity config, projects, hooks, skills/plugins.
- **Codex**: Windows Codex profile, TOML MCP config, WSL launcher wrappers,
  skills/plugins, project state.
- **Claude**: Claude Desktop/Code MCP config, project memory, Windows-to-WSL
  command wrapping.

## Rules

- Treat WSL as the runtime/filesystem authority and Windows as the UI shell.
- Do not edit host profiles until after a preflight audit and backup.
- Prefer absolute WSL binary paths; non-login shells often do not load NVM,
  pyenv, or shell aliases.
- Keep Antigravity, Codex, and Claude config shapes separate. Do not paste one
  agent's JSON/TOML format into another agent's config.
- For two-way sync, start with dry runs and an explicit source of truth. Never
  run broad sync against live skill/plugin trees before checking symlinks.

## Workflow

1. **Preflight**
   Run:

   ```bash
   python3 scripts/audit_wsl_agent_bridge.py --json
   ```

   Confirm Windows user, WSL distro, profile roots, `wsl.exe`, `rsync`, Node,
   Python, and current agent config files.

2. **Choose Target Agent**
   Load only the reference for the requested surface:

   - Antigravity: `references/antigravity.md`
   - Codex: `references/codex.md`
   - Claude: `references/claude.md`
   - Shared sync/path rules: `references/sync-and-paths.md`

3. **Back Up Before Mutation**
   Copy each target config to a timestamped sibling backup before changing it.
   If the app is open and profile/storage files are being edited, ask the user
   to close the app first.

4. **Configure**
   Use `wsl.exe -d <Distro> -e <absolute WSL command>` from Windows-side agent
   configs when the tool must run in WSL. Use direct WSL paths inside WSL-side
   wrappers and scripts.

5. **Verify**
   Prove the setup from the same side the app will use:

   ```powershell
   wsl.exe -d Ubuntu -e bash -lc 'pwd; node --version; python3 --version'
   ```

   Then verify the specific surface: MCP list/smoke, project registration,
   skill/plugin visibility, launcher version, and path translation tests.

## Common Repairs

- **Command not found / code 127**: The app is launching a missing binary or
  wrapper. Check the exact path in the error, then repair that path or point the
  config at a stable wrapper.
- **Codex missing hashed WSL launcher**: If Codex Desktop reports
  `/home/<user>/.codex/bin/wsl/<hash>/codex: No such file or directory`, create
  that exact wrapper and delegate it to `/home/<user>/.codex/bin/wsl/codex`.
  See `references/codex.md`.
- **MCP works in terminal but not app**: Replace shell aliases with absolute
  binary paths and test through `wsl.exe`.
- **Windows paths passed into WSL tools**: Normalize UNC paths with the helpers
  in `references/sync-and-paths.md`.
- **Skill/plugin sync corrupts repos**: Stop syncing. Restore backup, inspect
  symlinks, then rerun dry-run sync with `--keep-dirlinks` where appropriate.

## Done Criteria

- Audit script passes required checks or clearly names remaining external
  blockers.
- The chosen agent can open the WSL project.
- The chosen agent can launch a WSL command from its normal UI/config path.
- MCP/tooling smoke checks pass from the Windows app side.
- Any sync job has been dry-run first and has a rollback backup.
