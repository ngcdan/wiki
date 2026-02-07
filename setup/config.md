# Config

## Git: identity theo thư mục (GitHub vs Forgejo)

Mục tiêu: tránh commit nhầm `user.name/user.email`.

- **GitHub (default/global):** `nqcdan / linuss1908@gmail.com`
- **Forgejo (OF1):** áp cho repo dưới `/Users/nqcdan/OF1/forgejo/**` → `jesse.vnhph / jesse.vnhph@openfreightone.com`

### Setup

1) Tạo override file cho Forgejo:

```bash
cat > ~/.gitconfig-forgejo <<'EOF'
[user]
  name = jesse.vnhph
  email = jesse.vnhph@openfreightone.com
EOF
```

2) Set default global = GitHub:

```bash
git config --global user.name "nqcdan"
git config --global user.email "linuss1908@gmail.com"
```

3) Add vào `~/.gitconfig`:

```ini
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/"]
  path = ~/.gitconfig-forgejo
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/**"]
  path = ~/.gitconfig-forgejo
```

### Verify

```bash
cd /Users/nqcdan/.openclaw/workspace && git config user.name && git config user.email
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-build && git config user.name && git config user.email
```
