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
EXPECTED_DIAGNOSTICS = {
    "enabled": f"{FEATURE} is enabled.",
    "disabled": f"{FEATURE} is disabled",
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
  disabled) printf '%s  under development  false\\n' 'default_mode_request_user_input' ;;
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
if "%CODEX_SCENARIO%"=="enabled" echo default_mode_request_user_input  under development  true
""",
            encoding="ascii",
        )

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

    def write_drive_root_probe(self, directory: Path) -> None:
        self.write_fake_codex(directory)
        command = directory / "cygpath"
        command.write_text(
            "#!/usr/bin/env sh\n"
            "if [ \"$1\" = -w ]; then printf 'C:\\\\\n'; else exit 2; fi\n",
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

                stale = destination / "prompt-review-and-dispatch" / "stale.txt"
                stale.write_text("remove me", encoding="utf-8")
                unrelated = destination / "user-owned-skill"
                unrelated.mkdir()
                second = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, second.returncode, second.stdout)
                self.assertFalse(stale.exists())
                self.assertTrue(unrelated.is_dir())
                self.assert_source_parity(destination)

                marker = destination / "prompt-review-and-dispatch" / "preserve-on-failure.txt"
                marker.write_text("working install", encoding="utf-8")
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
                self.assertTrue(marker.is_file(), failed_copy.stdout)

                recovered = run(destination, self.fake_bin, "enabled")
                self.assertEqual(0, recovered.returncode, recovered.stdout)
                self.assert_source_parity(destination)

    def test_source_and_alias_guards(self) -> None:
        for adapter_name, run in self.adapters():
            with self.subTest(adapter=adapter_name):
                sandbox = self.root / adapter_name / "guard repo"
                shutil.copytree(ROOT / "scripts", sandbox / "scripts")
                shutil.copytree(ROOT / "skills", sandbox / "skills")
                nested = sandbox / "skills" / "new destination"
                guarded_nested = run(nested, self.fake_bin, "enabled", sandbox)
                self.assertNotEqual(0, guarded_nested.returncode, guarded_nested.stdout)
                self.assertIn("Refusing to install into the packaged source catalog", guarded_nested.stdout)
                self.assertFalse(nested.exists())

                guarded = run(sandbox / "skills", self.fake_bin, "enabled", sandbox)
                self.assertNotEqual(0, guarded.returncode, guarded.stdout)
                self.assertIn("Refusing to install into the packaged source catalog", guarded.stdout)

                alias_message = (
                    "Refusing to install through a filesystem alias"
                    if adapter_name in {"powershell", "pwsh"}
                    else "Refusing to install into the packaged source catalog"
                )
                repository_alias = self.root / adapter_name / "repository alias"
                self.make_directory_link(repository_alias, sandbox)
                aliased_source = run(sandbox / "skills", self.fake_bin, "enabled", repository_alias)
                self.assertNotEqual(0, aliased_source.returncode, aliased_source.stdout)
                self.assertIn(alias_message, aliased_source.stdout)

                destination_alias = sandbox / "source alias"
                self.make_directory_link(destination_alias, sandbox / "skills")
                aliased = run(destination_alias, self.fake_bin, "enabled", sandbox)
                self.assertNotEqual(0, aliased.returncode, aliased.stdout)
                self.assertIn(alias_message, aliased.stdout)
                self.assertTrue((sandbox / "skills" / "prompt-review-and-dispatch" / "SKILL.md").is_file())

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

                    if adapter_name == "git-bash":
                        probe_bin = self.root / adapter_name / "drive root probe"
                        self.write_drive_root_probe(probe_bin)
                        isolated_root = self.root / adapter_name / "isolated drive root"
                        isolated_root.mkdir()
                        drive_root = run(isolated_root, probe_bin, "enabled")
                        self.assertNotEqual(0, drive_root.returncode, drive_root.stdout)
                        self.assertIn("Refusing to install skills into the filesystem root", drive_root.stdout)
                        self.assertEqual([], list(isolated_root.iterdir()))

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
