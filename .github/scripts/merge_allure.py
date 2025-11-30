#!/usr/bin/env python3
"""
Merge Allure results downloaded by actions/download-artifact.

- Looks for directories matching artifacts/**/allure-results*
- Copies files into merged-allure-results/
- If a file name collision occurs, prefixes the copied file with a safe shard prefix
- Optionally runs `allure generate merged-allure-results -o allure-reports --clean`
  if the `allure` CLI is available on PATH.

Usage (in workflow merge job, after artifacts are downloaded):
  python .github/scripts/merge_allure.py
"""
import os
import shutil
import sys
import hashlib
import subprocess

ARTIFACTS_ROOT = os.path.join(os.getcwd(), "artifacts")
MERGED_DIR = os.path.join(os.getcwd(), "merged-allure-results")
REPORT_DIR = os.path.join(os.getcwd(), "allure-reports")


def safe_prefix_from_path(path):
    # create a short unique prefix for a path (uses sha1 of path)
    h = hashlib.sha1(path.encode("utf-8")).hexdigest()[:8]
    # make a filesystem-friendly prefix
    prefix = os.path.basename(os.path.dirname(path)) or os.path.basename(path)
    return f"{prefix}-{h}"


def merge_allure_results():
    if not os.path.isdir(ARTIFACTS_ROOT):
        print(f"No artifacts directory found at '{ARTIFACTS_ROOT}'. Nothing to merge.")
        return False

    os.makedirs(MERGED_DIR, exist_ok=True)

    merged_any = False

    # Walk artifacts root for any dir named starting with "allure-results"
    for root, dirs, files in os.walk(ARTIFACTS_ROOT):
        for d in dirs:
            if d.startswith("allure-results"):
                src_dir = os.path.join(root, d)
                shard_prefix = safe_prefix_from_path(src_dir)
                print(f"Merging from: {src_dir} (prefix: {shard_prefix})")

                # Copy files — handle collisions
                for subroot, _, filenames in os.walk(src_dir):
                    rel_root = os.path.relpath(subroot, src_dir)
                    target_dir = os.path.join(MERGED_DIR, rel_root) if rel_root != "." else MERGED_DIR
                    os.makedirs(target_dir, exist_ok=True)

                    for fn in filenames:
                        src_file = os.path.join(subroot, fn)
                        dest_file = os.path.join(target_dir, fn)

                        if not os.path.exists(dest_file):
                            # simple copy if not exists
                            shutil.copy2(src_file, dest_file)
                        else:
                            # collision: copy with shard prefix to avoid overwriting
                            name, ext = os.path.splitext(fn)
                            new_name = f"{shard_prefix}--{name}{ext}"
                            new_dest = os.path.join(target_dir, new_name)
                            print(f"File name collision for {fn} -> saving as {new_name}")
                            shutil.copy2(src_file, new_dest)

                merged_any = True

    if not merged_any:
        print("No allure-results* directories found under artifacts/. Nothing merged.")
        return False

    print("Merged results written to:", MERGED_DIR)
    return True


def try_generate_report():
    # try to run allure generate if available
    try:
        # check availability
        ret = subprocess.run(["which", "allure"], capture_output=True, text=True)
        if ret.returncode != 0 or not ret.stdout.strip():
            print("Allure CLI not found in PATH. Skipping report generation.")
            return False

        cmd = ["allure", "generate", MERGED_DIR, "-o", REPORT_DIR, "--clean"]
        print("Running:", " ".join(cmd))
        rc = subprocess.call(cmd)
        if rc == 0:
            print("Allure report generated at:", REPORT_DIR)
            return True
        else:
            print("Allure generate returned non-zero exit code:", rc)
            return False
    except Exception as e:
        print("Error while attempting to run Allure CLI:", e)
        return False


def main():
    merged = merge_allure_results()
    if not merged:
        # Nothing to generate
        sys.exit(0)

    generated = try_generate_report()
    if not generated:
        print("Merged results are ready in 'merged-allure-results'. Please run Allure CLI manually to generate HTML report.")
    sys.exit(0)


if __name__ == "__main__":
    main()