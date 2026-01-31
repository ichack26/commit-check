#!/usr/bin/env bash
set -e

# Must be run from inside a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Not inside a git repository"
  exit 1
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
SOURCE_DIR="$REPO_ROOT/git-diff-tool"
HOOK="$REPO_ROOT/.git/hooks/pre-commit"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "❌ git-diff-tool directory not found"
  exit 1
fi

echo "📦 Installing pre-commit hook..."

# Create pre-commit hook
cat > "$HOOK" << EOF
#!/usr/bin/env bash
set -e

echo "🔍 Running git-diff-tool pre-commit checks"

for script in "$SOURCE_DIR"/*; do
  echo "▶ Running \$(basename "\$script")"
  python3 "\$script"
done

echo "✅ All checks passed"
EOF

chmod +x "$HOOK"

echo "✅ Installed .git/hooks/pre-commit"
