#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
source_catalog_requested="$repo_root/skills"
destination=${SKILLS_INSTALL_DIR:-"$HOME/.agents/skills"}

if [ -z "${MSYSTEM:-}" ]; then
    case "$destination" in
        ///*)
            while [ "${destination#//}" != "$destination" ]; do
                destination=${destination#/}
            done
            ;;
    esac
fi

case "/$destination/" in
    */../*)
        printf 'Refusing to install through an unresolved parent segment.\n' >&2
        exit 2
        ;;
esac

cygpath_path=
if [ -n "${MSYSTEM:-}" ]; then
    for candidate in /usr/bin/cygpath.exe /usr/bin/cygpath; do
        if [ -x "$candidate" ]; then
            cygpath_path=$candidate
            break
        fi
    done
    if [ -z "$cygpath_path" ]; then
        printf 'Cannot inspect Git Bash paths without cygpath.\n' >&2
        exit 2
    fi
else
    cygpath_path=$(command -v cygpath 2>/dev/null || true)
fi

is_subst_path() {
    [ -n "${MSYSTEM:-}" ] || return 1
    windows_root=${SystemRoot:-${SYSTEMROOT:-C:\\Windows}}
    subst_path=$("$cygpath_path" -u "$windows_root")/System32/subst.exe
    if [ ! -x "$subst_path" ]; then
        printf 'Cannot inspect Windows substituted drives without subst.exe.\n' >&2
        return 2
    fi
    windows_path=$("$cygpath_path" -w "$1")
    drive=$(printf '%.2s' "$windows_path")
    if subst_output=$("$subst_path" 2>/dev/null); then
        subst_output=$(printf '%s' "$subst_output" | tr -d '\r')
    else
        printf 'Windows substituted-drive inspection failed.\n' >&2
        return 2
    fi
    case "$subst_output" in
        *"$drive\\: =>"*) return 0 ;;
        *) return 1 ;;
    esac
}

is_filesystem_root() {
    [ "$1" = / ] && return 0
    if [ -z "${MSYSTEM:-}" ]; then
        case "$1" in
            //*) return 0 ;;
        esac
    fi
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
    [ -n "$cygpath_path" ] || return 1
    root_path=$("$cygpath_path" -w "$1")
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

assert_no_windows_reparse_path() {
    [ -n "${MSYSTEM:-}" ] || return 0
    windows_root=${SystemRoot:-${SYSTEMROOT:-C:\\Windows}}
    powershell_path=$("$cygpath_path" -u "$windows_root")/System32/WindowsPowerShell/v1.0/powershell.exe
    [ -x "$powershell_path" ] || {
        printf 'Cannot inspect Windows filesystem aliases without powershell.exe.\n' >&2
        return 2
    }
    windows_path=$("$cygpath_path" -w "$1")
    if REPARSE_CHECK_PATH=$windows_path "$powershell_path" -NoProfile -NonInteractive -Command '
        $full = [IO.Path]::GetFullPath($env:REPARSE_CHECK_PATH)
        $current = [IO.Path]::GetPathRoot($full)
        foreach ($part in $full.Substring($current.Length) -split "[\\/]") {
            if (-not $part) { continue }
            $current = Join-Path $current $part
            if ((Get-Item -LiteralPath $current -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { exit 3 }
        }
    ' >/dev/null; then
        return 0
    else
        status=$?
    fi
    if [ "$status" -eq 3 ]; then
        printf 'Refusing to install through a filesystem alias.\n' >&2
    else
        printf 'Windows filesystem alias inspection failed.\n' >&2
    fi
    return 2
}

transaction_marker_matches() {
    marker_path=$1
    expected_name=$2
    if printf '%s\n' "$expected_name" | cmp -s - "$marker_path"; then
        return 0
    fi
    printf '%s\r\n' "$expected_name" | cmp -s - "$marker_path"
}

if is_filesystem_root "$destination"; then
    printf 'Refusing to install skills into the filesystem root.\n' >&2
    exit 2
fi

assert_no_windows_reparse_path "$source_catalog_requested"
source_catalog=$(CDPATH= cd -- "$source_catalog_requested" && pwd -P)
if [ "$source_catalog_requested" != "$source_catalog" ]; then
    printf 'Refusing to install from a filesystem alias.\n' >&2
    exit 2
fi

existing=$destination
while [ ! -d "$existing" ]; do
    parent=$(dirname -- "$existing")
    [ "$parent" != "$existing" ] || break
    existing=$parent
done
assert_no_windows_reparse_path "$existing"
existing=$(CDPATH= cd -- "$existing" && pwd -P)
for inspected_path in "$source_catalog" "$existing"; do
    if is_subst_path "$inspected_path"; then
        printf 'Refusing to install through a filesystem alias.\n' >&2
        exit 2
    else
        status=$?
        [ "$status" -eq 1 ] || exit "$status"
    fi
done
case "$existing/" in
    "$source_catalog/"*)
        printf 'Refusing to install into the packaged source catalog.\n' >&2
        exit 2
        ;;
esac
mkdir -p "$destination"
destination=$(CDPATH= cd -- "$destination" && pwd -P)
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

recovery_transactions=()
recovery_transaction_names=()
for skill in "$source_catalog"/*; do
    [ -d "$skill" ] || continue
    name=${skill##*/}
    target="$destination/$name"
    backup_count=0
    for stale_transaction in "$destination/.$name.install."*; do
        marker="$stale_transaction/.curated-codex-skills-transaction"
        [ -e "$stale_transaction" ] || [ -L "$stale_transaction" ] || continue
        if [ -L "$stale_transaction" ]; then
            printf 'Refusing to recover through a transaction filesystem alias.\n' >&2
            exit 2
        fi
        if [ -n "${MSYSTEM:-}" ]; then
            if assert_no_windows_reparse_path "$stale_transaction"; then
                :
            else
                exit $?
            fi
        fi
        if [ -L "$marker" ]; then
            printf 'Refusing to recover through a transaction marker filesystem alias.\n' >&2
            exit 2
        fi
        if [ -n "${MSYSTEM:-}" ] && [ -e "$marker" ]; then
            if assert_no_windows_reparse_path "$marker"; then
                :
            else
                exit $?
            fi
        fi
        [ -d "$stale_transaction" ] && [ -f "$marker" ] || continue
        transaction_marker_matches "$marker" "$name" || continue
        recovery_transactions+=("$stale_transaction")
        recovery_transaction_names+=("$name")
        stale_backup="$stale_transaction/old"
        if [ -e "$stale_backup" ] || [ -L "$stale_backup" ]; then
            backup_count=$((backup_count + 1))
        fi
    done
    if [ ! -e "$target" ] && [ ! -L "$target" ] && [ "$backup_count" -gt 1 ]; then
        printf 'Multiple interrupted transactions exist for %s; refusing ambiguous recovery.\n' "$name" >&2
        exit 2
    fi
done

skill_count=0
for skill in "$source_catalog"/*; do
    [ -d "$skill" ] || continue
    name=${skill##*/}
    target="$destination/$name"
    if [ "${#recovery_transactions[@]}" -gt 0 ]; then
        for recovery_index in "${!recovery_transactions[@]}"; do
            if [ "${recovery_transaction_names[$recovery_index]}" = "$name" ]; then
                stale_transaction=${recovery_transactions[$recovery_index]}
                stale_backup="$stale_transaction/old"
                if [ ! -e "$target" ] && [ ! -L "$target" ] &&
                    { [ -e "$stale_backup" ] || [ -L "$stale_backup" ]; }; then
                    if ! mv "$stale_backup" "$target"; then
                        printf 'Could not restore interrupted transaction %s.\n' "$stale_transaction" >&2
                        exit 2
                    fi
                fi
                if ! rm -rf "$stale_transaction"; then
                    printf 'Warning: could not remove stale transaction %s.\n' "$stale_transaction" >&2
                fi
            fi
        done
    fi
    transaction=$(mktemp -d "$destination/.$name.install.XXXXXX")
    if printf '%s\n' "$name" > "$transaction/.curated-codex-skills-transaction"; then
        :
    else
        status=$?
        rm -rf "$transaction"
        exit "$status"
    fi
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
        if ! rm -rf "$transaction"; then
            printf 'Warning: installed %s, but could not remove transaction %s.\n' "$name" "$transaction" >&2
        fi
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
            feature_state=$(printf '%s\n' "$feature_line" | awk '{ state = $NF; sub(/\r$/, "", state); print state }')
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
