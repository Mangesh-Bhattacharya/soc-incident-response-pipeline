import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).parent.parent
spec = importlib.util.spec_from_file_location("launch", ROOT / "launch.py")
launch = importlib.util.module_from_spec(spec)
sys.modules["launch"] = launch
spec.loader.exec_module(launch)


def _proc(returncode=0, stdout="", stderr=""):
    return MagicMock(returncode=returncode, stdout=stdout, stderr=stderr)


def test_missing_docker_is_a_blocking_failure_with_a_fix():
    with patch.object(launch.shutil, "which", return_value=None):
        (check,) = launch.check_docker()
    assert check.status == launch.FAIL and "Docker Desktop" in check.fix


def test_docker_permission_denied_points_at_the_docker_group():
    with patch.object(launch.shutil, "which", return_value="/usr/bin/docker"), \
         patch.object(launch, "_run", return_value=_proc(1, stderr="permission denied while trying to connect")):
        checks = launch.check_docker()
    daemon = next(c for c in checks if c.name == "docker-daemon")
    assert daemon.status == launch.FAIL and "docker group" in daemon.fix


def test_compose_v1_only_is_rejected():
    def fake_run(cmd, timeout=20):
        return _proc(0) if cmd[1] == "info" else _proc(1)

    with patch.object(launch.shutil, "which", return_value="/usr/bin/docker"), patch.object(launch, "_run", fake_run):
        checks = launch.check_docker()
    assert next(c for c in checks if c.name == "docker-compose").status == launch.FAIL


def test_busy_port_owned_by_someone_else_fails_but_our_own_stack_is_fine():
    with patch.object(launch, "port_is_free", return_value=False), patch.object(launch, "stack_is_healthy", return_value=False):
        assert launch.check_port().status == launch.FAIL
    with patch.object(launch, "port_is_free", return_value=False), patch.object(launch, "stack_is_healthy", return_value=True):
        assert launch.check_port().status == launch.OK


def test_env_check_reports_key_names_never_values(tmp_path):
    (tmp_path / ".env").write_text("VT_API_KEY=super-secret-value\nABUSEIPDB_API_KEY=\n", encoding="utf-8")
    check = launch.check_env(tmp_path)
    assert "VT_API_KEY" in check.detail and "super-secret-value" not in check.detail
    assert "ABUSEIPDB_API_KEY" not in check.detail


def test_fix_creates_env_from_example_and_never_overwrites(tmp_path):
    (tmp_path / ".env.example").write_text("VT_API_KEY=\n", encoding="utf-8")
    assert launch.apply_fixes(tmp_path)
    (tmp_path / ".env").write_text("VT_API_KEY=mine\n", encoding="utf-8")
    assert launch.apply_fixes(tmp_path) == []
    assert (tmp_path / ".env").read_text(encoding="utf-8") == "VT_API_KEY=mine\n"


def test_json_report_has_no_paths_or_hostnames(capsys):
    launch.report([launch.Check("env-file", launch.OK, "present; keys set: none (demo mode)")], as_json=True)
    payload = json.loads(capsys.readouterr().out)
    assert set(payload) == {"platform", "python", "checks"}
    assert str(ROOT) not in json.dumps(payload)


def test_launch_without_docker_falls_back_to_dashboard_demo(monkeypatch):
    fails = [launch.Check("docker-daemon", launch.FAIL, "down", "start it")]
    monkeypatch.setattr(launch, "run_doctor", lambda: fails + [launch.Check("node", launch.OK, "ok")])
    monkeypatch.setattr(launch, "apply_fixes", list)
    demo = MagicMock(return_value=0)
    monkeypatch.setattr(launch, "start_dashboard_demo", demo)
    assert launch.main(["--no-open"]) == 0
    demo.assert_called_once()


def test_launch_with_docker_ok_starts_stack(monkeypatch):
    monkeypatch.setattr(launch, "run_doctor", lambda: [launch.Check("docker-daemon", launch.OK, "running")])
    monkeypatch.setattr(launch, "apply_fixes", list)
    start = MagicMock(return_value=0)
    monkeypatch.setattr(launch, "start_docker", start)
    assert launch.main(["--no-open"]) == 0
    start.assert_called_once_with(open_browser=False)
