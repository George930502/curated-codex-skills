from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FEATURE = "default_mode_request_user_input"
TRANSACTION_MARKER = ".curated-codex-skills-transaction"
EXPECTED_DIAGNOSTICS = {
    "enabled": f"{FEATURE} is enabled.",
    "enabled-crlf": f"{FEATURE} is enabled.",
    "disabled": f"{FEATURE} is disabled",
    "disabled-crlf": f"{FEATURE} is disabled",
    "absent": f"does not list {FEATURE}",
    "malformed": f"unrecognized state for {FEATURE}",
    "failure": "Codex feature inspection failed",
    "missing-cli": "Codex CLI was not found",
}
SPEC = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
assert SPEC and SPEC.loader
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="curated skills 測試 ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fake_bin = self.root / "fake bin"
        self.write_fake_codex(self.fake_bin)

    def write_fake_codex(self, directory: Path) -> None:
        directory.mkdir(parents=True)
        shell = directory / "codex"
        shell.write_text(
            """#!/usr/bin/env sh
case "${CODEX_SCENARIO:-enabled}" in
  enabled) printf '%s  under development  true\\n' 'default_mode_request_user_input' ;;
  enabled-crlf) printf '%s  under development  true\\r\\n' 'default_mode_request_user_input' ;;
  disabled) printf '%s  under development  false\\n' 'default_mode_request_user_input' ;;
  disabled-crlf) printf '%s  under development  false\\r\\n' 'default_mode_request_user_input' ;;
  absent) printf 'apps  stable  true\\n' ;;
  malformed) printf '%s  under development  maybe\\n' 'default_mode_request_user_input' ;;
  failure) exit 7 ;;
esac
""",
            encoding="utf-8",
        )
        shell.chmod(0o755)
        (directory / "codex.cmd").write_text(
            """@echo off
if "%CODEX_SCENARIO%"=="failure" exit /b 7
if "%CODEX_SCENARIO%"=="absent" echo apps  stable  true
if "%CODEX_SCENARIO%"=="malformed" echo default_mode_request_user_input  under development  maybe
if "%CODEX_SCENARIO%"=="disabled" echo default_mode_request_user_input  under development  false
if "%CODEX_SCENARIO%"=="disabled-crlf" echo default_mode_request_user_input  under development  false
if "%CODEX_SCENARIO%"=="enabled" echo default_mode_request_user_input  under development  true
if "%CODEX_SCENARIO%"=="enabled-crlf" echo default_mode_request_user_input  under development  true
""",
            encoding="ascii",
        )
        if os.name == "nt":
            for name in ("subst.exe", "cygpath.exe"):
                shadow = directory / name
                shadow.write_text("#!/usr/bin/env sh\nexit 99\n", encoding="ascii")
                shadow.chmod(0o755)

    def write_failing_codex_script(self, directory: Path) -> None:
        directory.mkdir(parents=True)
        (directory / "codex.ps1").write_text(
            "throw 'simulated script failure'\n",
            encoding="utf-8",
        )

    def write_failing_copy(self, directory: Path) -> None:
        directory.mkdir(parents=True)
        command = directory / "cp"
        command.write_text("#!/usr/bin/env sh\nexit 9\n", encoding="ascii")
        command.chmod(0o755)

    def write_failing_swap(self, directory: Path) -> None:
        directory.mkdir(parents=True)
        command = directory / "mv"
        command.write_text(
            "#!/usr/bin/env sh\n"
            "case \"$1\" in */new) exit 10 ;; esac\n"
            "exec /bin/mv \"$@\"\n",
            encoding="ascii",
        )
        command.chmod(0o755)

    def write_failing_cleanup(self, directory: Path) -> None:
        directory.mkdir(parents=True)
        command = directory / "rm"
        command.write_text(
            "#!/usr/bin/env sh\n"
            "case \"$*\" in *.install.*) exit 11 ;; esac\n"
            "exec /bin/rm \"$@\"\n",
            encoding="ascii",
        )
        command.chmod(0o755)

    def run_powershell_copy_failure(
        self,
        executable: str,
        destination: Path,
        repository: Path = ROOT,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["TEST_INSTALLER"] = str(repository / "scripts" / "install.ps1")
        environment["TEST_DESTINATION"] = str(destination)
        return subprocess.run(
            [
                executable,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "function Copy-Item { throw 'simulated copy failure' }; "
                "& $env:TEST_INSTALLER -Destination $env:TEST_DESTINATION",
            ],
            cwd=repository,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_powershell_swap_failure(
        self,
        executable: str,
        destination: Path,
        repository: Path = ROOT,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["TEST_INSTALLER"] = str(repository / "scripts" / "install.ps1")
        environment["TEST_DESTINATION"] = str(destination)
        return subprocess.run(
            [
                executable,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "function Move-Item { param([string]$LiteralPath, [string]$Destination); "
                "if ((Split-Path -Leaf $LiteralPath) -eq 'new') { throw 'simulated swap failure' }; "
                "Microsoft.PowerShell.Management\\Move-Item -LiteralPath $LiteralPath -Destination $Destination }; "
                "& $env:TEST_INSTALLER -Destination $env:TEST_DESTINATION",
            ],
            cwd=repository,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_powershell_restricted_path(
        self,
        executable: str,
        destination: Path,
        repository: Path = ROOT,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PATH"] = str(self.fake_bin)
        environment["CODEX_SCENARIO"] = "enabled"
        return subprocess.run(
            [
                executable,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(repository / "scripts" / "install.ps1"),
                "-Destination",
                str(destination),
            ],
            cwd=repository,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_shell(
        self,
        executable: str,
        destination: Path,
        fake_bin: Path | None,
        scenario: str,
        repository: Path = ROOT,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["CODEX_SCENARIO"] = scenario
        if os.name == "nt":
            environment["TEST_DESTINATION"] = str(destination)
            environment["TEST_FAKE_BIN"] = str(fake_bin) if fake_bin else ""
            command = [
                executable,
                "-lc",
                'destination=$(cygpath -u "$TEST_DESTINATION"); '
                'if [ -n "$TEST_FAKE_BIN" ]; then '
                'fake_bin=$(cygpath -u "$TEST_FAKE_BIN"); PATH="$fake_bin:$PATH"; '
                'else PATH=/usr/bin:/bin; fi; '
                'SKILLS_INSTALL_DIR="$destination" bash scripts/install.sh',
            ]
        else:
            environment["SKILLS_INSTALL_DIR"] = str(destination)
            environment["PATH"] = (
                f"{fake_bin}{os.pathsep}{environment['PATH']}"
                if fake_bin
                else "/usr/bin:/bin"
            )
            command = [executable, str(repository / "scripts" / "install.sh")]
        return subprocess.run(
            command,
            cwd=repository,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_shell_dot_segment(
        self,
        executable: str,
        base: Path,
        repository: Path = ROOT,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        if os.name == "nt":
            environment["TEST_BASE"] = str(base)
            command = [
                executable,
                "-lc",
                'base=$(cygpath -u "$TEST_BASE"); '
                'SKILLS_INSTALL_DIR="$base/unresolved/../destination" bash scripts/install.sh',
            ]
        else:
            environment["SKILLS_INSTALL_DIR"] = str(base / "unresolved" / ".." / "destination")
            command = [executable, str(repository / "scripts" / "install.sh")]
        return subprocess.run(
            command,
            cwd=repository,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_shell_missing_cygpath(self, destination: Path) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["SKILLS_INSTALL_DIR"] = str(destination)
        environment["MSYSTEM"] = "MINGW64"
        environment["PATH"] = "/bin"
        return subprocess.run(
            [shutil.which("bash") or "bash", str(ROOT / "scripts" / "install.sh")],
            cwd=ROOT,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_shell_unc_root(
        self,
        executable: str,
        repository: Path = ROOT,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["SKILLS_INSTALL_DIR"] = "//server/share"
        return subprocess.run(
            [executable, str(repository / "scripts" / "install.sh")],
            cwd=repository,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_shell_double_slash_root(self, executable: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                executable,
                "-c",
                "mktemp() { printf 'REACHED_MKTEMP\\n' >&2; return 99; }; "
                "SKILLS_INSTALL_DIR=// source \"$1\"",
                str(ROOT / "scripts" / "install.sh"),
                str(ROOT / "scripts" / "install.sh"),
            ],
            cwd=ROOT,
            env=os.environ.copy(),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_shell_raw_destination(
        self,
        executable: str,
        destination: str,
        repository: Path = ROOT,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["SKILLS_INSTALL_DIR"] = destination
        environment["PATH"] = f"{self.fake_bin}{os.pathsep}{environment['PATH']}"
        environment["CODEX_SCENARIO"] = "enabled"
        return subprocess.run(
            [executable, str(repository / "scripts" / "install.sh")],
            cwd=repository,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_git_bash_drive_root(self, executable: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["SKILLS_INSTALL_DIR"] = "/c/"
        return subprocess.run(
            [executable, str(ROOT / "scripts" / "install.sh")],
            cwd=ROOT,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_powershell(
        self,
        executable: str,
        destination: Path,
        fake_bin: Path | None,
        scenario: str,
        repository: Path = ROOT,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["CODEX_SCENARIO"] = scenario
        environment["PATH"] = (
            f"{fake_bin}{os.pathsep}{environment['PATH']}"
            if fake_bin
            else os.pathsep.join(
                filter(
                    None,
                    [
                        str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"),
                        os.environ.get("SystemRoot"),
                    ],
                )
            )
        )
        return subprocess.run(
            [
                executable,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(repository / "scripts" / "install.ps1"),
                "-Destination",
                str(destination),
            ],
            cwd=repository,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def adapters(self):
        if os.name != "nt":
            return [
                (
                    "bash",
                    lambda destination, fake_bin, scenario, repository=ROOT: self.run_shell(
                        shutil.which("bash") or "bash",
                        destination,
                        fake_bin,
                        scenario,
                        repository,
                    ),
                )
            ]

        git_bash = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe"
        found = {
            "powershell": shutil.which("powershell"),
            "pwsh": shutil.which("pwsh"),
            "bash": str(git_bash) if git_bash.is_file() else None,
        }
        adapters = []
        for name in ("powershell", "pwsh"):
            if found[name]:
                adapters.append(
                    (
                        name,
                        lambda destination, fake_bin, scenario, repository=ROOT, exe=found[name]: self.run_powershell(
                            exe or name, destination, fake_bin, scenario, repository
                        ),
                    )
                )
        if found["bash"]:
            adapters.append(
                (
                    "git-bash",
                    lambda destination, fake_bin, scenario, repository=ROOT: self.run_shell(
                        found["bash"] or "bash",
                        destination,
                        fake_bin,
                        scenario,
                        repository,
                    ),
                )
            )
        return adapters

    def assert_source_parity(self, destination: Path) -> None:
        for source in sorted((ROOT / "skills").iterdir()):
            if not source.is_dir():
                continue
            installed = destination / source.name
            self.assertEqual([], validate.compare_packaged_skill(source, installed))

    def snapshot_tree(self, directory: Path) -> dict[str, bytes | None]:
        snapshot: dict[str, bytes | None] = {}
        for path in sorted(directory.rglob("*")):
            relative = path.relative_to(directory).as_posix()
            snapshot[relative] = None if path.is_dir() else path.read_bytes()
        return snapshot

    def make_directory_link(self, link: Path, target: Path) -> None:
        if os.name == "nt":
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout)
        else:
            link.symlink_to(target, target_is_directory=True)

    def make_subst(self, target: Path) -> Path:
        for letter in "ZYXWVUTSRQPONMLKJIHGFED":
            drive = f"{letter}:"
            if Path(f"{drive}/").exists():
                continue
            result = subprocess.run(
                ["subst", drive, str(target)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if result.returncode == 0:
                self.addCleanup(subprocess.run, ["subst", drive, "/d"], check=False)
                return Path(f"{drive}/")
        self.fail("no drive letter available for subst test")

    def test_supported_shell_identities(self) -> None:
        adapters = self.adapters()
        names = {name for name, _ in adapters}
        print("TESTED_INSTALLERS=" + ",".join(name for name, _ in adapters))
        if os.name != "nt":
            self.assertEqual({"bash"}, names)
            return

        if os.environ.get("GITHUB_ACTIONS"):
            self.assertEqual({"powershell", "pwsh", "git-bash"}, names)
        identities = {}
        for name, expected in (("powershell", "5"), ("pwsh", "7")):
            executable = shutil.which(name)
            if not executable:
                continue
            result = subprocess.run(
                [executable, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"],
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            identities[name] = result.stdout.strip()
            self.assertEqual(expected, identities[name], result.stdout)
        if "git-bash" in names:
            executable = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe"
            result = subprocess.run(
                [str(executable), "-lc", 'printf "%s|%s" "$OSTYPE" "$MSYSTEM"'],
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            identities["bash"] = result.stdout.strip()
            self.assertRegex(identities["bash"], r"^[^|]+\|MINGW(32|64|ARM64)$")
        print("WINDOWS_SHELL_IDENTITIES=" + ",".join(f"{key}:{value}" for key, value in identities.items()))

    def test_install_upgrade_and_copy_failure(self) -> None:
        for adapter_name, run in self.adapters():
            with self.subTest(adapter=adapter_name):
                destination = self.root / adapter_name / "skills with spaces 測試"
                collision = destination / "prompt-review-and-dispatch"
                collision.parent.mkdir(parents=True)
                collision.write_text("old install", encoding="utf-8")
                first = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, first.returncode, first.stdout)
                self.assertIn(EXPECTED_DIAGNOSTICS["enabled"], first.stdout)
                self.assert_source_parity(destination)

                linked = destination / "prompt-review-and-dispatch"
                shutil.rmtree(linked)
                outside = self.root / adapter_name / "outside link target"
                outside.mkdir()
                sentinel = outside / "preserve.txt"
                sentinel.write_text("preserve me", encoding="utf-8")
                self.make_directory_link(linked, outside)
                linked_result = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, linked_result.returncode, linked_result.stdout)
                self.assertTrue(sentinel.is_file())

                first_skill = sorted(path.name for path in (ROOT / "skills").iterdir() if path.is_dir())[0]
                nested_link = destination / first_skill / "nested outside link"
                self.make_directory_link(nested_link, outside)
                nested_link_result = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, nested_link_result.returncode, nested_link_result.stdout)
                self.assertTrue(sentinel.is_file(), nested_link_result.stdout)

                stale = destination / "prompt-review-and-dispatch" / "stale.txt"
                stale.write_text("remove me", encoding="utf-8")
                unrelated = destination / "user-owned-skill"
                unrelated.mkdir()
                second = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, second.returncode, second.stdout)
                self.assertFalse(stale.exists())
                self.assertTrue(unrelated.is_dir())
                self.assert_source_parity(destination)

                affected_target = destination / first_skill
                marker = affected_target / "preserve-on-failure.txt"
                marker.write_text("working install", encoding="utf-8")
                before_failure = self.snapshot_tree(affected_target)
                interrupted = destination / f".{first_skill}.install.interrupted"
                interrupted.mkdir()
                shutil.move(str(affected_target), str(interrupted / "old"))
                (interrupted / TRANSACTION_MARKER).write_bytes(f"{first_skill}\r\n".encode())
                if adapter_name in {"powershell", "pwsh"}:
                    failed_copy = self.run_powershell_copy_failure(
                        shutil.which(adapter_name) or adapter_name,
                        destination,
                    )
                else:
                    failing_bin = self.root / adapter_name / "failing copy bin"
                    self.write_failing_copy(failing_bin)
                    failed_copy = run(destination, failing_bin, "enabled")
                self.assertNotEqual(0, failed_copy.returncode, failed_copy.stdout)
                self.assertEqual(before_failure, self.snapshot_tree(affected_target), failed_copy.stdout)
                self.assertFalse(interrupted.exists(), failed_copy.stdout)

                if adapter_name in {"powershell", "pwsh"}:
                    failed_swap = self.run_powershell_swap_failure(
                        shutil.which(adapter_name) or adapter_name,
                        destination,
                    )
                else:
                    failing_bin = self.root / adapter_name / "failing swap bin"
                    self.write_failing_swap(failing_bin)
                    failed_swap = run(destination, failing_bin, "enabled")
                self.assertNotEqual(0, failed_swap.returncode, failed_swap.stdout)
                self.assertEqual(before_failure, self.snapshot_tree(affected_target), failed_swap.stdout)

                recovered = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, recovered.returncode, recovered.stdout)
                self.assert_source_parity(destination)

    def test_post_commit_cleanup_failure_is_nonfatal(self) -> None:
        for adapter_name, run in self.adapters():
            with self.subTest(adapter=adapter_name):
                destination = self.root / adapter_name / "cleanup failure"
                installed = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, installed.returncode, installed.stdout)

                first_skill = sorted(path.name for path in (ROOT / "skills").iterdir() if path.is_dir())[0]
                stale = destination / f".{first_skill}.install.test-residue"
                (stale / "old").mkdir(parents=True)
                (stale / TRANSACTION_MARKER).write_bytes(f"{first_skill}\r\n".encode())
                recovered = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, recovered.returncode, recovered.stdout)
                self.assertFalse(stale.exists(), recovered.stdout)

                if adapter_name not in {"powershell", "pwsh"}:
                    failing_bin = self.root / adapter_name / "failing cleanup bin"
                    self.write_failing_cleanup(failing_bin)
                    result = run(destination, failing_bin, "missing-cli")

                    self.assertEqual(0, result.returncode, result.stdout)
                    self.assertIn("could not remove transaction", result.stdout)
                    self.assertTrue(list(destination.glob(".*.install.*")), result.stdout)

                    recovered = run(destination, self.fake_bin, "enabled")
                    self.assertEqual(0, recovered.returncode, recovered.stdout)
                    self.assertFalse(list(destination.glob(".*.install.*")), recovered.stdout)
                self.assert_source_parity(destination)

    def test_transaction_recovery_rejects_ambiguous_or_forged_state(self) -> None:
        for adapter_name, run in self.adapters():
            with self.subTest(adapter=adapter_name):
                destination = self.root / adapter_name / "adversarial recovery"
                installed = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, installed.returncode, installed.stdout)
                skill_names = sorted(path.name for path in (ROOT / "skills").iterdir() if path.is_dir())
                first_skill = skill_names[0]
                last_skill = skill_names[-1]
                target = destination / first_skill

                nonexact = destination / f".{first_skill}.install.nonexact"
                nonexact.mkdir()
                (nonexact / TRANSACTION_MARKER).write_bytes(f"{first_skill}\nextra\n".encode())
                unrelated = nonexact / "preserve.txt"
                unrelated.write_text("user owned", encoding="utf-8")
                ignored = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, ignored.returncode, ignored.stdout)
                self.assertTrue(unrelated.is_file(), ignored.stdout)
                shutil.rmtree(nonexact)

                outside = self.root / adapter_name / "forged transaction target"
                (outside / "old").mkdir(parents=True)
                sentinel = outside / "old" / "preserve.txt"
                sentinel.write_text("outside", encoding="utf-8")
                (outside / TRANSACTION_MARKER).write_bytes(f"{last_skill}\r\n".encode())
                transaction_alias = destination / f".{last_skill}.install.forged"
                self.make_directory_link(transaction_alias, outside)
                first_target_sentinel = target / "catalog-preflight-sentinel.txt"
                first_target_sentinel.write_text("must survive", encoding="utf-8")
                forged = run(destination, self.fake_bin, "enabled")
                self.assertNotEqual(0, forged.returncode, forged.stdout)
                self.assertIn("transaction filesystem alias", forged.stdout)
                self.assertTrue(sentinel.is_file(), forged.stdout)
                self.assertTrue(first_target_sentinel.is_file(), forged.stdout)
                if transaction_alias.is_symlink():
                    transaction_alias.unlink()
                else:
                    os.rmdir(transaction_alias)

                older = destination / f".{first_skill}.install.aaaaaa"
                newer = destination / f".{first_skill}.install.zzzzzz"
                older.mkdir()
                shutil.move(str(target), str(older / "old"))
                shutil.copytree(older / "old", newer / "old")
                (older / TRANSACTION_MARKER).write_bytes(f"{first_skill}\n".encode())
                (newer / TRANSACTION_MARKER).write_bytes(f"{first_skill}\r\n".encode())
                ambiguous = run(destination, self.fake_bin, "enabled")
                self.assertNotEqual(0, ambiguous.returncode, ambiguous.stdout)
                self.assertIn("refusing ambiguous recovery", ambiguous.stdout)
                self.assertFalse(target.exists(), ambiguous.stdout)
                self.assertTrue((older / "old").is_dir(), ambiguous.stdout)
                self.assertTrue((newer / "old").is_dir(), ambiguous.stdout)

    def test_source_and_alias_guards(self) -> None:
        for adapter_name, run in self.adapters():
            with self.subTest(adapter=adapter_name):
                if adapter_name == "bash" and os.name != "nt":
                    missing_cygpath_destination = self.root / adapter_name / "missing cygpath"
                    missing_cygpath = self.run_shell_missing_cygpath(missing_cygpath_destination)
                    self.assertNotEqual(0, missing_cygpath.returncode, missing_cygpath.stdout)
                    self.assertIn("Cannot inspect Git Bash paths without cygpath", missing_cygpath.stdout)
                    self.assertFalse(missing_cygpath_destination.exists())

                    executable = shutil.which("bash") or "bash"
                    double_slash_root = self.run_shell_double_slash_root(executable)
                    self.assertNotEqual(0, double_slash_root.returncode, double_slash_root.stdout)
                    self.assertIn("Refusing to install skills into the filesystem root", double_slash_root.stdout)
                    self.assertNotIn("REACHED_MKTEMP", double_slash_root.stdout)

                    triple_destination = self.root / adapter_name / "triple slash destination"
                    triple_slash = self.run_shell_raw_destination(
                        executable,
                        "///" + str(triple_destination).lstrip("/"),
                    )
                    self.assertEqual(0, triple_slash.returncode, triple_slash.stdout)
                    self.assert_source_parity(triple_destination)

                if adapter_name in {"bash", "git-bash"}:
                    base = self.root / adapter_name / "dot segment guard"
                    base.mkdir(parents=True)
                    executable = (
                        str(Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe")
                        if adapter_name == "git-bash"
                        else shutil.which("bash") or "bash"
                    )
                    dot_segment = self.run_shell_dot_segment(executable, base)
                    self.assertNotEqual(0, dot_segment.returncode, dot_segment.stdout)
                    self.assertIn("Refusing to install through an unresolved parent segment", dot_segment.stdout)
                    self.assertEqual([], list(base.iterdir()))
                else:
                    base = self.root / adapter_name / "dot segment guard"
                    base.mkdir(parents=True)
                    dot_destination = Path(str(base / "unresolved") + "\\..\\destination")
                    dot_segment = run(dot_destination, self.fake_bin, "enabled")
                    self.assertNotEqual(0, dot_segment.returncode, dot_segment.stdout)
                    self.assertIn("Refusing to install through an unresolved parent segment", dot_segment.stdout)
                    self.assertEqual([], list(base.iterdir()))

                    root_destination = Path(os.environ.get("SystemDrive", "C:") + "\\")
                    root_result = run(root_destination, self.fake_bin, "enabled")
                    self.assertNotEqual(0, root_result.returncode, root_result.stdout)
                    self.assertIn("Refusing to install skills into the filesystem root", root_result.stdout)

                sandbox = self.root / adapter_name / "guard repo"
                shutil.copytree(ROOT / "scripts", sandbox / "scripts")
                shutil.copytree(ROOT / "skills", sandbox / "skills")

                aliased_catalog_repo = self.root / adapter_name / "aliased catalog repo"
                shutil.copytree(ROOT / "scripts", aliased_catalog_repo / "scripts")
                actual_catalog = self.root / adapter_name / "actual source catalog"
                shutil.copytree(ROOT / "skills", actual_catalog)
                self.make_directory_link(aliased_catalog_repo / "skills", actual_catalog)
                source_alias_destination = actual_catalog / "nested destination"
                source_alias_result = run(
                    source_alias_destination,
                    self.fake_bin,
                    "enabled",
                    aliased_catalog_repo,
                )
                self.assertNotEqual(0, source_alias_result.returncode, source_alias_result.stdout)
                self.assertIn("filesystem alias", source_alias_result.stdout)
                self.assertFalse(source_alias_destination.exists())

                nested = sandbox / "skills" / "new destination"
                guarded_nested = run(nested, self.fake_bin, "enabled", sandbox)
                self.assertNotEqual(0, guarded_nested.returncode, guarded_nested.stdout)
                self.assertIn("Refusing to install into the packaged source catalog", guarded_nested.stdout)
                self.assertFalse(nested.exists())

                guarded = run(sandbox / "skills", self.fake_bin, "enabled", sandbox)
                self.assertNotEqual(0, guarded.returncode, guarded.stdout)
                self.assertIn("Refusing to install into the packaged source catalog", guarded.stdout)

                if adapter_name == "bash" and os.name != "nt":
                    guarded_double_slash = self.run_shell_raw_destination(
                        shutil.which("bash") or "bash",
                        "/" + str(sandbox / "skills"),
                        sandbox,
                    )
                    self.assertNotEqual(0, guarded_double_slash.returncode, guarded_double_slash.stdout)
                    self.assertIn("Refusing to install skills into the filesystem root", guarded_double_slash.stdout)

                    guarded_triple_slash = self.run_shell_raw_destination(
                        shutil.which("bash") or "bash",
                        "///" + str(sandbox / "skills").lstrip("/"),
                        sandbox,
                    )
                    self.assertNotEqual(0, guarded_triple_slash.returncode, guarded_triple_slash.stdout)
                    self.assertIn("Refusing to install into the packaged source catalog", guarded_triple_slash.stdout)

                source_alias_message = (
                    "Refusing to install through a filesystem alias"
                    if adapter_name in {"powershell", "pwsh"}
                    else "Refusing to install into the packaged source catalog"
                )
                repository_alias = self.root / adapter_name / "repository alias"
                self.make_directory_link(repository_alias, sandbox)
                aliased_source = run(sandbox / "skills", self.fake_bin, "enabled", repository_alias)
                self.assertNotEqual(0, aliased_source.returncode, aliased_source.stdout)
                self.assertIn(source_alias_message, aliased_source.stdout)

                destination_alias = sandbox / "source alias"
                self.make_directory_link(destination_alias, sandbox / "skills")
                aliased = run(destination_alias, self.fake_bin, "enabled", sandbox)
                self.assertNotEqual(0, aliased.returncode, aliased.stdout)
                destination_alias_message = (
                    "Refusing to install through a filesystem alias"
                    if adapter_name in {"powershell", "pwsh", "git-bash"}
                    else "Refusing to install into the packaged source catalog"
                )
                self.assertIn(destination_alias_message, aliased.stdout)
                self.assertTrue((sandbox / "skills" / "prompt-review-and-dispatch" / "SKILL.md").is_file())

                if adapter_name in {"bash", "git-bash"}:
                    executable = (
                        str(Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe")
                        if adapter_name == "git-bash"
                        else shutil.which("bash") or "bash"
                    )
                    unc_root = self.run_shell_unc_root(executable)
                    self.assertNotEqual(0, unc_root.returncode, unc_root.stdout)
                    self.assertIn("Refusing to install skills into the filesystem root", unc_root.stdout)

                if adapter_name == "git-bash":
                    outside_destination = self.root / adapter_name / "outside destination"
                    outside_destination.mkdir()
                    destination_junction = self.root / adapter_name / "destination junction"
                    self.make_directory_link(destination_junction, outside_destination)
                    junction_result = run(destination_junction, self.fake_bin, "enabled")
                    self.assertNotEqual(0, junction_result.returncode, junction_result.stdout)
                    self.assertIn("Refusing to install through a filesystem alias", junction_result.stdout)
                    self.assertEqual([], list(outside_destination.iterdir()))

                if os.name == "nt":
                    substituted_repo = self.make_subst(sandbox)
                    substituted_source = run(sandbox / "skills", self.fake_bin, "enabled", substituted_repo)
                    self.assertNotEqual(0, substituted_source.returncode, substituted_source.stdout)
                    self.assertIn("Refusing to install through a filesystem alias", substituted_source.stdout)

                    substituted_destination = run(
                        substituted_repo / "skills",
                        self.fake_bin,
                        "enabled",
                        sandbox,
                    )
                    self.assertNotEqual(0, substituted_destination.returncode, substituted_destination.stdout)
                    self.assertIn("Refusing to install through a filesystem alias", substituted_destination.stdout)

                    if adapter_name in {"powershell", "pwsh"}:
                        restricted_subst = self.run_powershell_restricted_path(
                            shutil.which(adapter_name) or adapter_name,
                            substituted_repo / "skills",
                            sandbox,
                        )
                    else:
                        restricted_subst = run(
                            substituted_repo / "skills",
                            None,
                            "missing-cli",
                            sandbox,
                        )
                    self.assertNotEqual(0, restricted_subst.returncode, restricted_subst.stdout)
                    self.assertIn("Refusing to install through a filesystem alias", restricted_subst.stdout)

                    if adapter_name == "git-bash":
                        executable = str(
                            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe"
                        )
                        drive_root = self.run_git_bash_drive_root(executable)
                        self.assertNotEqual(0, drive_root.returncode, drive_root.stdout)
                        self.assertIn("Refusing to install skills into the filesystem root", drive_root.stdout)

    def test_capability_diagnostics(self) -> None:
        for adapter_name, run in self.adapters():
            for scenario, message in EXPECTED_DIAGNOSTICS.items():
                with self.subTest(adapter=adapter_name, scenario=scenario):
                    result = run(
                        self.root / adapter_name / scenario,
                        None if scenario == "missing-cli" else self.fake_bin,
                        scenario,
                    )
                    self.assertEqual(0, result.returncode, result.stdout)
                    self.assertIn(message, result.stdout)

            if adapter_name in {"powershell", "pwsh"}:
                with self.subTest(adapter=adapter_name, scenario="external-script-failure"):
                    script_bin = self.root / adapter_name / "failing script bin"
                    self.write_failing_codex_script(script_bin)
                    result = run(self.root / adapter_name / "script failure", script_bin, "enabled")
                    self.assertEqual(0, result.returncode, result.stdout)
                    self.assertIn(EXPECTED_DIAGNOSTICS["failure"], result.stdout)


if __name__ == "__main__":
    unittest.main()
