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
SPEC = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
assert SPEC and SPEC.loader
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


class InstallerTests(unittest.TestCase):
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
            yield "bash", lambda destination, fake_bin, scenario, repository=ROOT: self.run_shell(
                shutil.which("bash") or "bash",
                destination,
                fake_bin,
                scenario,
                repository,
            )
            return

        git_bash = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe"
        found = {
            "powershell": shutil.which("powershell"),
            "pwsh": shutil.which("pwsh"),
            "bash": str(git_bash) if git_bash.is_file() else None,
        }
        if os.environ.get("GITHUB_ACTIONS"):
            self.assertTrue(all(found.values()), f"missing CI shells: {found}")
        identities = {}
        for name, expected in (("powershell", "5"), ("pwsh", "7")):
            if found[name]:
                result = subprocess.run(
                    [found[name] or name, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"],
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                identities[name] = result.stdout.strip()
                self.assertEqual(expected, identities[name], result.stdout)
        if found["bash"]:
            result = subprocess.run(
                [found["bash"] or "bash", "-lc", 'printf "%s|%s" "$OSTYPE" "$MSYSTEM"'],
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
        for name in ("powershell", "pwsh"):
            if found[name]:
                yield name, lambda destination, fake_bin, scenario, repository=ROOT, exe=found[name]: self.run_powershell(
                    exe or name, destination, fake_bin, scenario, repository
                )
        if found["bash"]:
            yield "git-bash", lambda destination, fake_bin, scenario, repository=ROOT: self.run_shell(
                found["bash"] or "bash",
                destination,
                fake_bin,
                scenario,
                repository,
            )

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

    def test_install_upgrade_and_capability_diagnostics(self) -> None:
        expected = {
            "enabled": f"{FEATURE} is enabled.",
            "disabled": f"{FEATURE} is disabled",
            "absent": f"does not list {FEATURE}",
            "malformed": f"unrecognized state for {FEATURE}",
            "failure": "Codex feature inspection failed",
            "missing-cli": "Codex CLI was not found",
        }
        with tempfile.TemporaryDirectory(prefix="curated skills 測試 ") as temporary:
            root = Path(temporary)
            fake_bin = root / "fake bin"
            self.write_fake_codex(fake_bin)
            adapters = list(self.adapters())
            print("TESTED_INSTALLERS=" + ",".join(name for name, _ in adapters))
            for adapter_name, run in adapters:
                with self.subTest(adapter=adapter_name, behavior="upgrade"):
                    destination = root / adapter_name / "skills with spaces 測試"
                    collision = destination / "prompt-review-and-dispatch"
                    collision.parent.mkdir(parents=True)
                    collision.write_text("old install", encoding="utf-8")
                    first = run(destination, fake_bin, "enabled")
                    self.assertEqual(0, first.returncode, first.stdout)
                    self.assertIn(expected["enabled"], first.stdout)
                    self.assert_source_parity(destination)

                    linked = destination / "prompt-review-and-dispatch"
                    shutil.rmtree(linked)
                    outside = root / adapter_name / "outside link target"
                    outside.mkdir()
                    sentinel = outside / "preserve.txt"
                    sentinel.write_text("preserve me", encoding="utf-8")
                    self.make_directory_link(linked, outside)
                    linked_result = run(destination, fake_bin, "enabled")
                    self.assertEqual(0, linked_result.returncode, linked_result.stdout)
                    self.assertTrue(sentinel.is_file())
                    self.assert_source_parity(destination)

                    stale = destination / "prompt-review-and-dispatch" / "stale.txt"
                    stale.write_text("remove me", encoding="utf-8")
                    unrelated = destination / "user-owned-skill"
                    unrelated.mkdir()
                    second = run(destination, fake_bin, "enabled")
                    self.assertEqual(0, second.returncode, second.stdout)
                    self.assertFalse(stale.exists())
                    self.assertTrue(unrelated.is_dir())
                    self.assert_source_parity(destination)

                with self.subTest(adapter=adapter_name, behavior="source-guard"):
                    sandbox = root / adapter_name / "guard repo"
                    shutil.copytree(ROOT / "scripts", sandbox / "scripts")
                    shutil.copytree(ROOT / "skills", sandbox / "skills")
                    guarded = run(sandbox / "skills", fake_bin, "enabled", sandbox)
                    self.assertNotEqual(0, guarded.returncode, guarded.stdout)
                    self.assertIn("Refusing to install into the packaged source catalog", guarded.stdout)
                    self.assertTrue((sandbox / "skills" / "prompt-review-and-dispatch" / "SKILL.md").is_file())

                for scenario, message in expected.items():
                    with self.subTest(adapter=adapter_name, scenario=scenario):
                        result = run(
                            root / adapter_name / scenario,
                            None if scenario == "missing-cli" else fake_bin,
                            scenario,
                        )
                        self.assertEqual(0, result.returncode, result.stdout)
                        self.assertIn(message, result.stdout)


if __name__ == "__main__":
    unittest.main()
