#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
source_catalog="$repo_root/skills"
destination=${SKILLS_INSTALL_DIR:-"$HOME/.agents/skills"}

case "/$destination/" in
    */../*)
        printf 'Refusing to install through an unresolved parent segment.\n' >&2
        exit 2
        ;;
esac

is_subst_path() {
    command -v cygpath >/dev/null 2>&1 || return 1
    command -v subst.exe >/dev/null 2>&1 || return 1
    windows_path=$(cygpath -w "$1")
    drive=$(printf '%.2s' "$windows_path")
    subst_output=$(subst.exe 2>/dev/null | tr -d '\r')
    case "$subst_output" in
        *"$drive\\: =>"*) return 0 ;;
        *) return 1 ;;
    esac
}

is_filesystem_root() {
    [ "$1" = / ] && return 0
    normalized=${1%/}
    case "$normalized" in
        //*)
            unc_tail=${normalized#//}
            case "$unc_tail" in
                */*/*) ;;
                */*) return 0 ;;
            esac
            ;;
    esac
    command -v cygpath >/dev/null 2>&1 || return 1
    root_path=$(cygpath -w "$1")
    case "$root_path" in
        [A-Za-z]:\\) return 0 ;;
        \\\\*)
            unc_tail=${root_path#\\\\}
            unc_tail=${unc_tail%\\}
            case "$unc_tail" in
                *\\*\\*) ;;
                *\\*) return 0 ;;
            esac
            ;;
        *) return 1 ;;
    esac
    return 1
}

resolve_unaliased_windows_directory() {
    logical=$(CDPATH= cd -- "$1" && pwd -L)
    physical=$(CDPATH= cd -- "$1" && pwd -P)
    if command -v cygpath >/dev/null 2>&1 && [ "$logical" != "$physical" ]; then
        printf 'Refusing to install through a filesystem alias.\n' >&2
        return 2
    fi
    printf '%s\n' "$physical"
}

existing=$destination
while [ ! -d "$existing" ]; do
    parent=$(dirname -- "$existing")
    [ "$parent" != "$existing" ] || break
    existing=$parent
done
existing=$(resolve_unaliased_windows_directory "$existing")
if is_subst_path "$source_catalog" || is_subst_path "$existing"; then
    printf 'Refusing to install through a filesystem alias.\n' >&2
    exit 2
fi
if is_filesystem_root "$destination"; then
    printf 'Refusing to install skills into the filesystem root.\n' >&2
    exit 2
fi
case "$existing/" in
    "$source_catalog/"*)
        printf 'Refusing to install into the packaged source catalog.\n' >&2
        exit 2
        ;;
esac
mkdir -p "$destination"
destination=$(resolve_unaliased_windows_directory "$destination")
if is_filesystem_root "$destination"; then
    printf 'Refusing to install skills into the filesystem root.\n' >&2
    exit 2
fi
case "$destination/" in
    "$source_catalog/"*)
        printf 'Refusing to install into the packaged source catalog.\n' >&2
        exit 2
        ;;
esac

skill_count=0
for skill in "$source_catalog"/*; do
    [ -d "$skill" ] || continue
    name=${skill##*/}
    target="$destination/$name"
    transaction=$(mktemp -d "$destination/.$name.install.XXXXXX")
    staging="$transaction/new"
    backup="$transaction/old"
    if cp -R "$skill" "$staging"; then
        :
    else
        status=$?
        rm -rf "$transaction"
        exit "$status"
    fi
    had_target=false
    if [ -e "$target" ] || [ -L "$target" ]; then
        if mv "$target" "$backup"; then
            had_target=true
        else
            status=$?
            rm -rf "$transaction"
            exit "$status"
        fi
    fi
    if mv "$staging" "$target"; then
        rm -rf "$transaction"
    else
        status=$?
        if [ "$had_target" = true ] && ! mv "$backup" "$target"; then
            printf 'Install failed and rollback is preserved at %s.\n' "$backup" >&2
            exit "$status"
        fi
        rm -rf "$transaction"
        exit "$status"
    fi
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
