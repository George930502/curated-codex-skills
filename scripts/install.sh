#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
codex_home=${CODEX_HOME:-"$HOME/.codex"}
destination="$codex_home/skills"

mkdir -p "$destination"
cp -R "$repo_root/skills"/. "$destination"/

skill_count=0
for skill in "$repo_root"/skills/*; do
    [ -d "$skill" ] || continue
    skill_count=$((skill_count + 1))
done
printf 'Installed %s skills into %s\n' "$skill_count" "$destination"
