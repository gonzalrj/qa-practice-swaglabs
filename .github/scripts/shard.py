"""
Collect pytest nodeids once, split them across shards, and run the subset for this shard.

Environment variables this script reads:
 - SHARD_INDEX (required)
 - SHARD_COUNT (required)
 - XDIST (optional)         -> added as: -n <XDIST>
 - BASE_URL (optional)      -> added as: --base-url <BASE_URL>
 - MARKER (optional)        -> added as: -m <MARKER>
 - HEADLESS (optional)      -> if present and truthy, add --headless
 - EXTRA_ARGS (optional)    -> shell-split and appended (e.g. "--alluredir=allure-results-0")
 - RERUNS (optional)        -> added as: --reruns <RERUNS>
 - RERUNS_DELAY (optional)  -> added as: --reruns-delay <RERUNS_DELAY>
 - SHARD_DEBUG (optional)   -> if "1", prints collected nodeids for debugging
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from typing import List


def looks_like_nodeid(line: str) -> bool:
    """Return True if the line looks like a pytest nodeid or file path pytest would accept."""
    if not line:
        return False
    ln = line.strip()

    # skip obvious noise
    low = ln.lower()
    if low.startswith(("warning:", "pytestwarning", "deprecationwarning", "error:")):
        return False
    if "no tests ran" in low:
        return False
    if re.match(r'^\d+\s+tests?\s+collected', ln):
        return False

    # direct nodeid (module::test or module::class::test)
    if "::" in ln:
        return True

    # unix-style file path ending with .py
    if "/" in ln and ln.endswith(".py"):
        return True

    # windows-style path
    if "\\" in ln and ln.endswith(".py"):
        return True

    # common heuristic
    if "tests/" in ln or "/test_" in ln or "\\test_" in ln:
        return True

    return False


def collect_pytest_nodeids() -> List[str]:
    """Run pytest --collect-only -q and return a list of candidate nodeid lines."""
    try:
        out = subprocess.check_output(["pytest", "--collect-only", "-q"], text=True)
    except subprocess.CalledProcessError as e:
        print("pytest collection failed:", e, file=sys.stderr)
        # If pytest fails during collection, propagate its exit code
        sys.exit(e.returncode)

    lines = [l.strip() for l in out.splitlines() if l.strip()]
    nodeids = [ln for ln in lines if looks_like_nodeid(ln)]
    return nodeids


def build_pytest_cmd(shard_tests: List[str]) -> List[str]:
    """Assemble the pytest command from env vars and the provided nodeids."""
    cmd: List[str] = ["pytest", "-q"]

    # xdist
    xdist = os.environ.get("XDIST", "auto").strip()
    if xdist:
        cmd += ["-n", xdist]

    # base url (pytest option expected by your tests)
    base_url = os.environ.get("BASE_URL", "https://www.saucedemo.com").strip()
    if base_url:
        cmd += ["--base-url", base_url]

    # marker
    marker = os.environ.get("MARKER", "regression").strip()
    if marker:
        cmd += ["-m", marker]

    # headless flag - only add if TEST harness expects --headless as CLI flag
    headless = os.environ.get("HEADLESS", "").strip()
    if headless and headless.lower() not in ("0", "false", "no", ""):
        cmd += ["--headless"]

    # reruns
    reruns = os.environ.get("RERUNS", 1).strip()
    if reruns:
        cmd += ["--reruns", reruns]

    # reruns delay
    reruns_delay = os.environ.get("RERUNS_DELAY", 1).strip()
    if reruns_delay:
        cmd += ["--reruns-delay", reruns_delay]

    # extra args (e.g. --alluredir=allure-results-0). Shell-split safely.
    extra = os.environ.get("EXTRA_ARGS", "--alluredir allure-results").strip()
    if extra:
        try:
            cmd += shlex.split(extra)
        except Exception:
            # fallback: append as a single token (shouldn't normally happen)
            cmd.append(extra)

    # finally, the nodeids for this shard
    cmd += shard_tests
    return cmd


def main() -> None:
    # required envs
    try:
        si = int(os.environ["SHARD_INDEX"])
        sc = int(os.environ["SHARD_COUNT"])
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Invalid shard index/count: {e}", file=sys.stderr)
        sys.exit(2)

    nodeids = collect_pytest_nodeids()

    if not nodeids:
        print("No valid tests detected from pytest collection. Output of pytest --collect-only -q follows:")
        try:
            raw = subprocess.check_output(["pytest", "--collect-only", "-q"], text=True, stderr=subprocess.STDOUT)
            print(raw)
        except Exception:
            pass
        # Exit 0 so the pipeline does not treat an empty shard as a failure
        sys.exit(0)

    # optional debug printing of all collected nodeids
    if os.environ.get("SHARD_DEBUG", "") == "1":
        print("Collected nodeids (debug):")
        for n in nodeids:
            print("  -", n)
        print()

    # slice tests for this shard
    shard_tests = [t for i, t in enumerate(nodeids) if i % sc == si]

    print(f"Collected {len(nodeids)} tests → running {len(shard_tests)} on shard {si}/{sc}")

    if not shard_tests:
        print("This shard has no tests to run. Exiting successfully.")
        sys.exit(0)

    pytest_cmd = build_pytest_cmd(shard_tests)

    # flush stdout to keep logs clean
    sys.stdout.flush()

    print("Running command:", " ".join(pytest_cmd))
    rc = subprocess.call(pytest_cmd)
    sys.exit(rc)


if __name__ == "__main__":
    main()
