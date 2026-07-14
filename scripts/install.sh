#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
destination=${SKILLS_INSTALL_DIR:-"$HOME/.agents/skills"}

mkdir -p "$destination"
destination=$(CDPATH= cd -- "$destination" && pwd -P)
if [ "$destination" = / ]; then
    printf 'Refusing to install skills into the filesystem root.\n' >&2
    exit 2
fi
case "$destination/" in
    "$repo_root/skills/"*)
        printf 'Refusing to install into the packaged source catalog.\n' >&2
        exit 2
        ;;
esac

skill_count=0
for skill in "$repo_root"/skills/*; do
    [ -d "$skill" ] || continue
    target="$destination/${skill##*/}"
    rm -rf "$target"
    cp -R "$skill" "$target"
    skill_count=$((skill_count + 1))
done
printf 'Installed %s skills into %s\n' "$skill_count" "$destination"

feature=default_mode_request_user_input
if ! command -v codex >/dev/null 2>&1; then
    printf 'Warning: Codex CLI was not found. After installing Codex, run: codex features enable %s\n' "$feature" >&2
else
    if feature_output=$(codex features list 2>/dev/null); then
        feature_line=$(printf '%s\n' "$feature_output" | awk -v name="$feature" '$1 == name { print; exit }')
        if [ -z "$feature_line" ]; then
            printf 'Warning: this Codex version does not list %s. Update Codex before using native approval.\n' "$feature" >&2
        else
            feature_state=$(printf '%s\n' "$feature_line" | awk '{ print $NF }')
            case "$feature_state" in
                true)
                    printf '%s is enabled.\n' "$feature"
                    ;;
                false)
                    printf 'Warning: %s is disabled; enable it, then restart Codex:\n' "$feature" >&2
                    printf '  codex features enable %s\n' "$feature" >&2
                    ;;
                *)
                    printf 'Warning: Codex reported an unrecognized state for %s. Update Codex before using native approval.\n' "$feature" >&2
                    ;;
            esac
        fi
    else
        printf 'Warning: Codex feature inspection failed. Run "codex features list" and resolve the error before using native approval.\n' >&2
    fi
fi

printf 'Codex detects skill changes automatically; restart it if the skills do not appear.\n'
