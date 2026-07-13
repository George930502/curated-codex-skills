#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
destination="$HOME/.agents/skills"

mkdir -p "$destination"
cp -R "$repo_root/skills"/. "$destination"/

skill_count=0
for skill in "$repo_root"/skills/*; do
    [ -d "$skill" ] || continue
    skill_count=$((skill_count + 1))
done
printf 'Installed %s skills into %s\n' "$skill_count" "$destination"

feature=default_mode_request_user_input
if ! command -v codex >/dev/null 2>&1; then
    printf 'Warning: Codex CLI was not found. After installing Codex, run: codex features enable %s\n' "$feature" >&2
    exit 0
fi

feature_line=$(codex features list 2>/dev/null | awk -v name="$feature" '$1 == name { print; exit }')
if [ -z "$feature_line" ]; then
    printf 'Warning: this Codex version does not list %s. Update Codex before using native approval.\n' "$feature" >&2
elif [ "${feature_line##* }" != true ]; then
    printf 'Warning: %s is disabled; enable it, then restart Codex:\n' "$feature" >&2
    printf '  codex features enable %s\n' "$feature" >&2
else
    printf '%s is enabled.\n' "$feature"
fi
