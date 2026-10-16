"""One-command launcher and self-diagnosis for the SOC pipeline console.

    python launch.py              # check, start the stack, wait until healthy, open the dashboard
    python launch.py --doctor     # diagnose only; prints what is wrong and the exact fix
    python launch.py --doctor --json   # same, safe to paste into a bug report (no secrets, paths or hostnames)
    python launch.py --fix        # apply the safe auto-fixes (currently: create .env from .env.example)
    python launch.py --down       # stop the stack

Standard library only, so it runs before anything else is installed. On Windows use `py launch.py`.
"""
from __future__ import annotations

import argparse
import json
import platform
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = 8080
URL = f"http://127.0.0.1:{PORT}/"
HEALTH_URL = f"http://127.0.0.1:{PORT}/api/health"
MIN_PYTHON = (3, 10)
HEALTH_TIMEOUT_S = 180
SECRET_KEYS = ("VT_API_KEY", "ABUSEIPDB_API_KEY", "JIRA_API_TOKEN")

OK, WARN, FAIL = "ok", "warn", "fail"


@dataclass
class Check:
    name: str
    status: str
    detail: str
    fix: str = ""


def _run(cmd: list[str], timeout: int = 20) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None


def check_python() -> Check:
    have = sys.version_info[:2]
    if have >= MIN_PYTHON:
        return Check("python", OK, platform.python_version())
    return Check(
        "python", WARN,
        f"{platform.python_version()} (the native CLI needs {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+; Docker does not)",
        "Install Python 3.10+ from python.org, or use the Docker path, which needs no host Python.",
    )


def check_docker() -> list[Check]:
    if not shutil.which("docker"):
        return [Check(
            "docker", FAIL, "docker not found on PATH",
            "Install Docker Desktop (Windows/macOS) or Docker Engine + Compose v2 (Linux), then reopen your terminal.",
        )]
    out = [Check("docker-cli", OK, "found")]
    info = _run(["docker", "info"], timeout=25)
    if info is None or info.returncode != 0:
        stderr = (info.stderr if info else "timed out").lower()
        if "permission denied" in stderr:
            fix = "Linux: add yourself to the docker group (`sudo usermod -aG docker $USER`), then log out and back in."
        else:
            fix = "Start Docker Desktop (wait for the whale icon to settle) or run `sudo systemctl start docker`."
        out.append(Check("docker-daemon", FAIL, "the Docker daemon is not reachable", fix))
        return out
    out.append(Check("docker-daemon", OK, "running"))
    compose = _run(["docker", "compose", "version"])
    if compose is None or compose.returncode != 0:
        out.append(Check(
            "docker-compose", FAIL, "Compose v2 plugin missing",
            "Update Docker Desktop, or install the `docker-compose-plugin` package. The old `docker-compose` v1 is not supported.",
        ))
    else:
        out.append(Check("docker-compose", OK, compose.stdout.strip().splitlines()[0]))
    return out


def port_is_free(port: int = PORT) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def stack_is_healthy(url: str = HEALTH_URL) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.status == 200 and b'"ok"' in resp.read()
    except (urllib.error.URLError, OSError, ValueError):
        return False


def check_port() -> Check:
    if port_is_free():
        return Check("port-8080", OK, "free")
    if stack_is_healthy():
        return Check("port-8080", OK, "in use by this console (already running)")
    return Check(
        "port-8080", FAIL, "another program is using port 8080",
        "Windows: `netstat -ano | findstr :8080`. macOS/Linux: `lsof -i :8080`. Stop it, or change the left-hand port "
        'in docker-compose.yml, e.g. "127.0.0.1:8081:8080".',
    )


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def check_env(root: Path = ROOT) -> Check:
    env = root / ".env"
    if not env.exists():
        return Check(
            "env-file", FAIL, ".env missing (docker compose refuses to start without it)",
            "Run `python launch.py --fix`, or copy .env.example to .env. Leave keys blank for demo mode.",
        )
    configured = [k for k in SECRET_KEYS if read_env(env).get(k)]
    # Report which keys are set, never their values.
    detail = f"present; keys set: {', '.join(configured) if configured else 'none (demo mode)'}"
    return Check("env-file", OK, detail)


def check_node() -> Check:
    if shutil.which("npm"):
        return Check("node", OK, "npm found (dashboard-only demo mode available)")
    return Check("node", WARN, "npm not found (only needed for the no-Docker dashboard demo)", "Install Node.js 20+.")


def run_doctor(root: Path = ROOT) -> list[Check]:
    return [check_python(), *check_docker(), check_port(), check_env(root), check_node()]


def apply_fixes(root: Path = ROOT) -> list[str]:
    """Only fixes that cannot lose data or touch secrets."""
    applied: list[str] = []
    env, example = root / ".env", root / ".env.example"
    if not env.exists() and example.exists():
        shutil.copyfile(example, env)
        applied.append("created .env from .env.example (blank keys = demo mode)")
    return applied


def report(checks: list[Check], as_json: bool) -> None:
    if as_json:
        payload = {
            "platform": f"{platform.system()} {platform.release()} {platform.machine()}",
            "python": platform.python_version(),
            "checks": [asdict(c) for c in checks],
        }
        print(json.dumps(payload, indent=2))
        return
    icon = {OK: "[ ok ]", WARN: "[warn]", FAIL: "[FAIL]"}
    for check in checks:
        print(f"{icon[check.status]} {check.name}: {check.detail}")
        if check.status != OK and check.fix:
            print(f"        fix: {check.fix}")


def blocking(checks: list[Check]) -> list[Check]:
    return [c for c in checks if c.status == FAIL]


def wait_until_healthy(timeout_s: int = HEALTH_TIMEOUT_S) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if stack_is_healthy():
            return True
        time.sleep(2)
    return False


def compose(*args: str) -> int:
    return subprocess.call(["docker", "compose", *args], cwd=ROOT)


def start_docker(open_browser: bool) -> int:
    if stack_is_healthy():
        print(f"Already running at {URL}")
    else:
        print("Building and starting the stack (the first run takes a few minutes)...")
        if compose("up", "--build", "-d") != 0:
            print("docker compose failed. Logs: `docker compose logs`. See docs/TROUBLESHOOTING.md.", file=sys.stderr)
            return 1
        if not wait_until_healthy():
            print("Containers started but never became healthy. Run `docker compose logs`.", file=sys.stderr)
            return 1
    print(f"Dashboard ready: {URL}")
    if open_browser:
        webbrowser.open(URL)
    return 0


def start_dashboard_demo() -> int:
    dashboard = ROOT / "dashboard"
    npm = shutil.which("npm")
    if not npm:
        return 1
    print("Docker is unavailable; starting the dashboard in demo mode with Node (no backend, canned scenarios).")
    if subprocess.call([npm, "install"], cwd=dashboard) != 0:
        return 1
    return subprocess.call([npm, "run", "dev", "--", "--open"], cwd=dashboard)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--doctor", action="store_true", help="diagnose only; do not start anything")
    parser.add_argument("--json", action="store_true", help="machine-readable doctor output")
    parser.add_argument("--fix", action="store_true", help="apply safe auto-fixes, then re-check")
    parser.add_argument("--down", action="store_true", help="stop the stack")
    parser.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = parser.parse_args(argv)

    if args.down:
        return compose("down")

    # --doctor alone only reports; launching also self-heals the .env file
    if args.fix or not args.doctor:
        for line in apply_fixes():
            print(f"fixed: {line}", file=sys.stderr)

    checks = run_doctor()
    if args.doctor:
        report(checks, args.json)
        return 1 if blocking(checks) else 0

    docker_ok = not any(c.name.startswith("docker") and c.status == FAIL for c in checks)
    other_blockers = [c for c in blocking(checks) if not c.name.startswith("docker")]
    if other_blockers:
        report(other_blockers, False)
        return 1
    if docker_ok:
        return start_docker(open_browser=not args.no_open)
    report([c for c in checks if c.name.startswith("docker")], False)
    return start_dashboard_demo() if check_node().status == OK else 1


if __name__ == "__main__":
    raise SystemExit(main())
