# Sync And Path Rules

Use this only after choosing what must be shared between Windows and WSL.

## Sync Policy

Two-way sync is dangerous unless there is a conflict policy. Default to:

1. Audit both trees.
2. Back up both trees.
3. Dry-run WSL to Windows.
4. Dry-run Windows to WSL.
5. Run one direction at a time.
6. Enable hooks only after manual verification.

Recommended excludes:

```text
.git
node_modules
.venv
__pycache__
*.sqlite
*.db
*.db-shm
*.db-wal
```

WSL to Windows, dereferencing symlinks so Windows tools can read content:

```bash
rsync -aunL --delete --exclude '.git' --exclude 'node_modules' "$WSL_SRC/" "$WIN_DST/"
```

Windows to WSL, preserving existing symlinked directories:

```bash
rsync -aunK --exclude '.git' --exclude 'node_modules' "$WIN_SRC/" "$WSL_DST/"
```

Remove `n` from `-aunL` or `-aunK` only after reviewing dry-run output.

## Path Translation

Python:

```python
def translate_path(p_str: str, distro: str = "Ubuntu") -> str:
    if not p_str:
        return p_str
    p = p_str.replace("\\", "/")
    prefixes = [f"//wsl.localhost/{distro}", f"//wsl$/{distro}"]
    for prefix in prefixes:
        if p.lower().startswith(prefix.lower()):
            rest = p[len(prefix):]
            return rest if rest.startswith("/") else "/" + rest
    if len(p) >= 2 and p[1] == ":":
        drive = p[0].lower()
        rest = p[2:].lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return p
```

TypeScript:

```typescript
export function translatePath(p: string, distro = "Ubuntu"): string {
  if (!p) return p;
  const normalized = p.replace(/\\/g, "/");
  const prefixes = [`//wsl.localhost/${distro}`, `//wsl$/${distro}`];
  for (const prefix of prefixes) {
    if (normalized.toLowerCase().startsWith(prefix.toLowerCase())) {
      const rest = normalized.slice(prefix.length);
      return rest.startsWith("/") ? rest : `/${rest}`;
    }
  }
  if (/^[a-zA-Z]:/.test(normalized)) {
    const drive = normalized[0].toLowerCase();
    const rest = normalized.slice(2).replace(/^\/+/, "");
    return `/mnt/${drive}/${rest}`;
  }
  return normalized;
}
```

Test cases:

```text
\\wsl.localhost\Ubuntu\home\alice\repo -> /home/alice/repo
\\wsl$\Ubuntu\home\alice\repo -> /home/alice/repo
C:\Users\alice\.codex -> /mnt/c/Users/alice/.codex
```
