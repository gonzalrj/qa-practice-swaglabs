#!/usr/bin/env python3
import os
import subprocess
import sys
import shlex
import re


def looks_like_nodeid(line: str) -> bool:
    """Return True if the line looks like a pytest nodeid."""
    if "::" in line:
        return True
    if line.endswith(".py") and "/" in line:
        return True
    if re.match(r'^\d+\s+tests?\s+collected', line):
        return False
    if "no tests ran" in line.lower():
        return False
    if line.lower().startswith("error:"):
        return False
    if "tests/" in line or "/test_" in line:
        return True
    return False


def main():
    si = int(os.environ["SHARD_INDEX"])
    sc = int(os.environ["SHARD_COUNT"])

    # Collect tests
    try:
        raw = subprocess.check_output(
            ["pytest", "--collect-only", "-q"],
            text=True
        )
    except subprocess.CalledProcessError as e:
        print("pytest collection failed:", e)
        sys.exit(e.returncode)

    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    tests = [ln for ln in lines if looks_like_nodeid(ln)]

    if not tests:
        print("No valid tests detected from pytest collection:")
        print(raw)
        sys.exit(0)

    shard_tests = [t for i, t in enumerate(tests) if i % sc == si]

    print(f"Collected {len(tests)} tests → running {len(shard_tests)} on shard {si}/{sc}")

    if not shard_tests:
        print("This shard has no tests. Exiting.")
        sys.exit(0)

    # Build pytest command
    cmd = ["pytest", "-q"]

    xdist = os.environ.get("XDIST", "").strip()
    if xdist:
        cmd += ["-n", xdist]

    extra = os.environ.get("EXTRA_ARGS", "").strip()
    if extra:
        cmd += shlex.split(extra)

    cmd += shard_tests

    print("Running:", " ".join(cmd))
    rc = subprocess.call(cmd)
    sys.exit(rc)


if __name__ == "__main__":
    main()
