#!/usr/bin/env python3
"""
shard.py - collect pytest nodeids, group them (module/class/none), slice by shard,
and run pytest.

Behavior:
 - GROUP_MARK / GROUP_SHARD_INDEX / GROUP_WORKERS: if GROUP_MARK set, the group shard
   will collect only tests with that marker and run them with --dist=loadgroup.
 - GROUP_BY env controls grouping granularity for non-group shards:
     GROUP_BY=module  -> group by module/file (default)
     GROUP_BY=class   -> group by module::Class
     GROUP_BY=none    -> no grouping (flat modulo)
 - Parent nodeids (module/class) removed if child nodeids exist.
 - No baked-in default test config; workflow should set envs.
 - Set SHARD_DEBUG=1 to print collected nodeids and grouping info.
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from collections import OrderedDict
from typing import List, Optional, Iterable


def looks_like_nodeid(line: str) -> bool:
    if not line:
        return False
    ln = line.strip()
    low = ln.lower()
    if low.startswith(("warning:", "pytestwarning", "deprecationwarning", "error:")):
        return False
    if "no tests ran" in low:
        return False
    if re.match(r"^\d+\s+tests?\s+collected", ln):
        return False
    if "::" in ln:
        return True
    if ln.endswith(".py") and ("/" in ln or "\\" in ln):
        return True
    if "tests/" in ln or "/test_" in ln or "\\test_" in ln:
        return True
    return False


def collect_pytest_nodeids(marker_filter: Optional[str] = None) -> List[str]:
    cmd = ["pytest", "--collect-only", "-q"]
    if marker_filter:
        cmd += ["-m", marker_filter]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"pytest collection failed (exit {e.returncode}). Output:", file=sys.stderr)
        if hasattr(e, "output") and e.output:
            print(e.output, file=sys.stderr)
        raise
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    nodeids = [ln for ln in lines if looks_like_nodeid(ln)]
    return nodeids


def remove_parent_nodeids(nodeids: Iterable[str]) -> List[str]:
    nodeid_list = list(nodeids)
    parents_with_children = set()
    for parent in nodeid_list:
        prefix = parent + "::"
        for candidate in nodeid_list:
            if candidate is parent:
                continue
            if candidate.startswith(prefix):
                parents_with_children.add(parent)
                break
    filtered = [n for n in nodeid_list if n not in parents_with_children]
    return filtered


def group_nodeids(nodeids: List[str], by: str) -> List[List[str]]:
    """
    Group nodeids by 'module' (file), 'class' (module::Class), or 'none'.
    Returns list of groups (each group is a list of nodeids), preserving discovery order.
    """
    groups = OrderedDict()
    for nid in nodeids:
        parts = nid.split("::")
        module = parts[0]
        if by == "module" or len(parts) == 1:
            key = module
        elif by == "class":
            # module::Class if exists, otherwise module
            key = module if len(parts) == 1 else module + "::" + parts[1]
        else:  # "none"
            # Use the full nodeid as key so every nodeid is its own group
            key = nid
        groups.setdefault(key, []).append(nid)
    return list(groups.values())


def build_pytest_cmd(shard_tests: List[str], *, is_group_shard: bool, group_workers: Optional[str]) -> List[str]:
    cmd: List[str] = ["pytest", "-q"]

    # workers / distribution
    if is_group_shard:
        workers_val = (group_workers or os.environ.get("XDIST") or "").strip()
        if workers_val:
            cmd += ["-n", workers_val]
        cmd += ["--dist", "loadgroup"]
    else:
        xdist_val = (os.environ.get("XDIST") or "").strip()
        if xdist_val:
            cmd += ["-n", xdist_val]

    # base-url
    base_url = os.environ.get("BASE_URL", "").strip()
    if base_url:
        cmd += ["--base-url", base_url]

    browser = os.environ.get("BROWSER", "").strip()
    if browser:
        cmd += ["--browser", browser]

    # marker for non-group shards
    marker = os.environ.get("MARKER", "").strip()
    if marker and not is_group_shard:
        cmd += ["-m", marker]

    headless_val = os.environ.get("HEADLESS", "").strip().lower()
    if headless_val in {"1", "true", "yes"}:
        cmd += ["--headless"]

    reruns = os.environ.get("RERUNS", "").strip()
    if reruns:
        cmd += ["--reruns", reruns]

    reruns_delay = os.environ.get("RERUNS_DELAY", "").strip()
    if reruns_delay:
        cmd += ["--reruns-delay", reruns_delay]

    extra = os.environ.get("EXTRA_ARGS", "").strip()
    if extra:
        try:
            cmd += shlex.split(extra)
        except ValueError as e:
            print(f"Warning: failed to split EXTRA_ARGS: {e!r}; appending raw", file=sys.stderr)
            cmd.append(extra)

    cmd += shard_tests
    return cmd


def main() -> None:
    try:
        si = int(os.environ["SHARD_INDEX"])
        sc = int(os.environ["SHARD_COUNT"])
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Invalid shard index/count: {e}", file=sys.stderr)
        sys.exit(2)

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

    is_group_shard = bool(group_mark) and (group_shard_index is not None and group_shard_index == si)

    # choose grouping mode: module | class | none
    group_by = (os.environ.get("GROUP_BY") or "module").strip().lower()
    if group_by not in {"module", "class", "none"}:
        print(f"Invalid GROUP_BY='{group_by}'; falling back to 'module'", file=sys.stderr)
        group_by = "module"

    # decide collection filter
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

    try:
        nodeids = collect_pytest_nodeids(marker_filter=collect_marker_filter)
    except subprocess.CalledProcessError as exc:
        sys.exit(getattr(exc, "returncode", 2))

    if not nodeids:
        print("No tests collected (after marker filtering). Exiting successfully.")
        sys.exit(0)

    # remove parent nodeids (module/class) if children present
    filtered_nodeids = remove_parent_nodeids(nodeids)

    # optional debug
    if os.environ.get("SHARD_DEBUG", "") == "1":
        print("Collected nodeids (post-filter):")
        for n in filtered_nodeids:
            print("  -", n)
        print()

    # partitioning
    if is_group_shard:
        # group shard gets all filtered nodeids for that marker
        shard_tests = filtered_nodeids
    else:
        if group_by == "none":
            # flat modulo slicing
            shard_tests = [t for i, t in enumerate(filtered_nodeids) if i % sc == si]
        else:
            # group by module or class, then round-robin assign groups
            groups = group_nodeids(filtered_nodeids, by=group_by)
            if os.environ.get("SHARD_DEBUG", "") == "1":
                print(f"Grouping by '{group_by}', total groups:", len(groups))
                for gi, g in enumerate(groups):
                    print(f" Group {gi}: {len(g)} tests; example: {g[0]}")
            shard_tests = []
            for gi, group in enumerate(groups):
                if gi % sc == si:
                    shard_tests.extend(group)

    print(f"Collected {len(filtered_nodeids)} total nodeids → running {len(shard_tests)} on shard {si}/{sc}")

    if not shard_tests:
        print("This shard has no tests to run. Exiting successfully.")
        sys.exit(0)

    pytest_cmd = build_pytest_cmd(shard_tests, is_group_shard=is_group_shard, group_workers=group_workers)

    sys.stdout.flush()
    print("Running command:", " ".join(shlex.quote(x) for x in pytest_cmd))

    rc = subprocess.call(pytest_cmd)
    sys.exit(rc)


if __name__ == "__main__":
    main()