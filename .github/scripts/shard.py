#!/usr/bin/env python3
"""
Collect pytest nodeids, slice them for this shard, and run pytest.

This version contains NO baked defaults. Provide all desired defaults via
the GitHub Actions workflow environment variables.

Environment variables used:
  SHARD_INDEX (required)
  SHARD_COUNT (required)

  BASE_URL
  BROWSER
  MARKER
  HEADLESS
  XDIST
  EXTRA_ARGS
  RERUNS
  RERUNS_DELAY

Group-specific envs:
  GROUP_MARK
  GROUP_SHARD_INDEX
  GROUP_WORKERS

Set SHARD_DEBUG=1 to print collected nodeids and additional debug info.
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from typing import List, Optional


def looks_like_nodeid(line: str) -> bool:
    """Return True if line looks like a pytest nodeid or file path pytest would accept."""
    if not line:
        return False
    ln = line.strip()
    low = ln.lower()

    # Skip obvious noise
    if low.startswith(("warning:", "pytestwarning", "deprecationwarning", "error:")):
        return False
    if "no tests ran" in low:
        return False
    if re.match(r"^\d+\s+tests?\s+collected", ln):
        return False

    # Direct nodeid (module::class::test)
    if "::" in ln:
        return True

    # Unix or Windows paths to python file
    if ln.endswith(".py") and ("/" in ln or "\\" in ln):
        return True

    # Heuristic: contains common test folder or filename prefix
    if "tests/" in ln or "/test_" in ln or "\\test_" in ln:
        return True

    return False


def collect_pytest_nodeids(marker_filter: Optional[str] = None) -> List[str]:
    """
    Run pytest --collect-only -q (optionally with -m marker_filter) and return candidate nodeid lines.
    Raises subprocess.CalledProcessError on collection failure (caller will exit).
    """
    cmd = ["pytest", "--collect-only", "-q"]
    if marker_filter:
        cmd += ["-m", marker_filter]

    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"pytest collection failed (exit {e.returncode}). Output:", file=sys.stderr)
        # Print captured output for debugging
        if hasattr(e, "output") and e.output:
            print(e.output, file=sys.stderr)
        raise

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    nodeids = [ln for ln in lines if looks_like_nodeid(ln)]
    return nodeids


def build_pytest_cmd(
        shard_tests: List[str], *, is_group_shard: bool, group_workers: Optional[str]
) -> List[str]:
    """Assemble the pytest command from environment variables and provided nodeids."""
    cmd: List[str] = ["pytest", "-q"]

    # Debug print of envs
    print(
        "ENV:",
        "BASE_URL=%r" % os.environ.get("BASE_URL"),
        "BROWSER=%r" % os.environ.get("BROWSER"),
        "MARKER=%r" % os.environ.get("MARKER"),
        "HEADLESS=%r" % os.environ.get("HEADLESS"),
        "XDIST=%r" % os.environ.get("XDIST"),
        "EXTRA_ARGS=%r" % os.environ.get("EXTRA_ARGS"),
        "RERUNS=%r" % os.environ.get("RERUNS"),
        "RERUNS_DELAY=%r" % os.environ.get("RERUNS_DELAY"),
    )

    # Xdist / workers
    if is_group_shard:
        workers_val = (group_workers or os.environ.get("XDIST") or "").strip()
        if workers_val:
            cmd += ["-n", workers_val]
        # Use loadgroup distribution for grouped tests
        cmd += ["--dist", "loadgroup"]
    else:
        xdist_val = (os.environ.get("XDIST") or "").strip()
        if xdist_val:
            cmd += ["-n", xdist_val]

    # Standard flags: base-url, browser
    base_url = os.environ.get("BASE_URL", "").strip()
    if base_url:
        cmd += ["--base-url", base_url]

    browser = os.environ.get("BROWSER", "").strip()
    if browser:
        cmd += ["--browser", browser]

    # Marker: add only for non-group shards if provided
    marker = os.environ.get("MARKER", "").strip()
    if marker and not is_group_shard:
        cmd += ["-m", marker]

    # Headless
    headless_val = os.environ.get("HEADLESS", "").strip().lower()
    if headless_val in {"1", "true", "yes"}:
        cmd += ["--headless"]

    # Reruns and delay
    reruns = os.environ.get("RERUNS", "").strip()
    if reruns:
        cmd += ["--reruns", reruns]

    reruns_delay = os.environ.get("RERUNS_DELAY", "").strip()
    if reruns_delay:
        cmd += ["--reruns-delay", reruns_delay]

    # Extra args (shell-split)
    extra = os.environ.get("EXTRA_ARGS", "").strip()
    if extra:
        try:
            cmd += shlex.split(extra)
        except ValueError as e:
            # shlex.split raises ValueError on malformed quoting — fall back to appending raw string
            print(f"Warning: failed to shell-split EXTRA_ARGS ({e!r}); appending raw EXTRA_ARGS", file=sys.stderr)
            cmd.append(extra)

    # Finally the nodeids
    cmd += shard_tests
    return cmd


def main() -> None:
    # Required envs (explicit error handling)
    try:
        si = int(os.environ["SHARD_INDEX"])
        sc = int(os.environ["SHARD_COUNT"])
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Invalid shard index/count: {e}", file=sys.stderr)
        sys.exit(2)

    # Group configuration
    group_mark = (os.environ.get("GROUP_MARK") or "").strip()
    group_shard_index_raw = (os.environ.get("GROUP_SHARD_INDEX") or "").strip()
    group_workers = (os.environ.get("GROUP_WORKERS") or "").strip() or None

    group_shard_index: Optional[int] = None
    if group_shard_index_raw:
        try:
            group_shard_index = int(group_shard_index_raw)
        except ValueError:
            print("Invalid GROUP_SHARD_INDEX; ignoring group shard behaviour", file=sys.stderr)
            group_shard_index = None

    # Determine whether this is the designated group shard (explicit boolean)
    is_group_shard = bool(group_mark) and (group_shard_index is not None and group_shard_index == si)

    # Decide collection filter
    collect_marker_filter: Optional[str]
    if group_mark:
        if is_group_shard:
            collect_marker_filter = group_mark
            print(f"Shard {si} is the GROUP_SHARD and will collect tests with marker: {group_mark}")
        else:
            collect_marker_filter = f"not {group_mark}"
            print(f"Shard {si} will collect tests excluding marker: {group_mark}")
    else:
        collect_marker_filter = None
        print("No GROUP_MARK specified — normal sharding will be used.")

    # Collect nodeids (may raise CalledProcessError which we let bubble up)
    try:
        nodeids = collect_pytest_nodeids(marker_filter=collect_marker_filter)
    except subprocess.CalledProcessError as exc:
        # collect_pytest_nodeids already printed useful debugging info
        sys.exit(getattr(exc, "returncode", 2))

    if not nodeids:
        print("No tests collected (after marker filtering). Exiting successfully.")
        sys.exit(0)

    # Optional debug printing of nodeids
    if os.environ.get("SHARD_DEBUG", "") == "1":
        print("Collected nodeids (debug):")
        for n in nodeids:
            print("  -", n)
        print()

    # Partition tests for this shard
    if is_group_shard:
        shard_tests = nodeids  # all group-marked tests run on this shard
    else:
        shard_tests = [t for i, t in enumerate(nodeids) if i % sc == si]

    print(f"Collected {len(nodeids)} total nodeids → running {len(shard_tests)} on shard {si}/{sc}")

    if not shard_tests:
        print("This shard has no tests to run. Exiting successfully.")
        sys.exit(0)

    # Build pytest command and execute
    pytest_cmd = build_pytest_cmd(shard_tests, is_group_shard=is_group_shard, group_workers=group_workers)

    sys.stdout.flush()
    print("Running command:", " ".join(shlex.quote(x) for x in pytest_cmd))

    rc = subprocess.call(pytest_cmd)
    sys.exit(rc)


if __name__ == "__main__":
    main()
