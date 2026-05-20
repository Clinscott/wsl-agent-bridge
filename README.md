# WSL Agent Bridge

A reusable agentic developer skill and lifecycle integration workflow to bridge Windows-native agent IDE environments (Antigravity and Codex) with WSL (Ubuntu) filesystems and command execution layers.

## Features
- **WSL MCP Redirection**: Guide to running host MCP servers inside WSL via `wsl.exe` with absolute runtime pathing.
- **Symlink-Preserving Two-Way Sync**: Setup for a lifecycle-hooked synchronization pipeline that preserves git-symlinked directories (`rsync -auK`).
- **Sidebar Integration**: Configuration for mapping workspaces using Windows UNC paths (`\\wsl.localhost\...`).
- **Cross-Platform Path Translation**: Lightweight helper libraries in Python and TypeScript to transparently sanitize host-supplied UNC or mapped-drive paths down to native Linux directories before runtime.

## Installation and Setup
Refer to [SKILL.md](SKILL.md) for step-by-step instructions.

## License
MIT License. See [LICENSE](LICENSE) for details.
