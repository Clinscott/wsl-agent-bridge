# WSL Agent Bridge

A reusable agent skill for bridging Windows-hosted agent apps into WSL-hosted
projects and runtimes.

Supported surfaces:

- Antigravity
- Codex
- Claude

The skill separates shared WSL bridge rules from agent-specific config shapes so
agents do not paste Antigravity JSON into Codex TOML or assume Claude uses one
fixed config location.

Quick audit:

```bash
python3 scripts/audit_wsl_agent_bridge.py --json
```

Then follow `SKILL.md` and load only the relevant reference under
`references/`.

License: MIT. See `LICENSE`.
