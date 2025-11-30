#!/bin/sh
# entrypoint.sh - build pytest args from env or run explicit args
# Supports: ./entrypoint.sh --print-env  (prints export lines and exits)
#           ./entrypoint.sh [pytest-args...]  (exec pytest with args)
#           ./entrypoint.sh               (builds args from env/defaults and execs pytest)

# -------------------------
# Defaults (can be overridden by export or CI env vars)
# -------------------------
: "${BASE_URL:=https://www.saucedemo.com/}"
: "${BROWSER:=chrome}"
: "${HEADLESS:=true}"
: "${MARKER:=regression}"
: "${XDIST:=auto}"
: "${RERUNS:=1}"
: "${RERUNS_DELAY:=1}"
: "${EXTRA_ARGS:=}"

# Prefer workflow-provided *_INPUT variables if present.
# For CI, pass inputs into the step as BASE_URL_INPUT etc.
if [ -n "${BASE_URL_INPUT:-}" ]; then
  BASE_URL="${BASE_URL_INPUT}"
fi
if [ -n "${BROWSER_INPUT:-}" ]; then
  BROWSER="${BROWSER_INPUT}"
fi
if [ -n "${HEADLESS_INPUT:-}" ]; then
  HEADLESS="${HEADLESS_INPUT}"
fi
if [ -n "${MARKER_INPUT:-}" ]; then
  MARKER="${MARKER_INPUT}"
fi
if [ -n "${XDIST_INPUT:-}" ]; then
  XDIST="${XDIST_INPUT}"
fi
if [ -n "${RERUNS_INPUT:-}" ]; then
  RERUNS="${RERUNS_INPUT}"
fi
if [ -n "${RERUNS_DELAY_INPUT:-}" ]; then
  RERUNS_DELAY="${RERUNS_DELAY_INPUT}"
fi
if [ -n "${EXTRA_ARGS_INPUT:-}" ]; then
  EXTRA_ARGS="${EXTRA_ARGS_INPUT}"
fi

# Helper: produce safe escaped value for export printing
_escape_for_export() {
  # POSIX-safe escaping of backslash and double-quote
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

print_env_mode() {
  # Print export lines suitable for "source"
  printf 'export BASE_URL="%s"\n' "$(_escape_for_export "$BASE_URL")"
  printf 'export BROWSER="%s"\n' "$(_escape_for_export "$BROWSER")"
  printf 'export HEADLESS="%s"\n' "$(_escape_for_export "$HEADLESS")"
  printf 'export MARKER="%s"\n' "$(_escape_for_export "$MARKER")"
  printf 'export XDIST="%s"\n' "$(_escape_for_export "$XDIST")"
  printf 'export RERUNS="%s"\n' "$(_escape_for_export "$RERUNS")"
  printf 'export RERUNS_DELAY="%s"\n' "$(_escape_for_export "$RERUNS_DELAY")"
  printf 'export EXTRA_ARGS="%s"\n' "$(_escape_for_export "$EXTRA_ARGS")"
  # also emit a default results dir if you need it
  printf 'export RESULTS_PATH="%s"\n' "$(_escape_for_export "${RESULTS_PATH:-allure-results}")"
  exit 0
}

usage() {
  cat <<'USAGE'
entrypoint.sh - build pytest args from env or run explicit args

Usage:
  ./entrypoint.sh            # run pytest with args built from envs / defaults
  ./entrypoint.sh --print-env  # print `export VAR="value"` lines and exit (safe to source)
  ./entrypoint.sh --help     # show this message
USAGE
  exit 0
}

# Help
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
fi

# print-env mode: output export lines then exit (no side effects)
if [ "${1:-}" = "--print-env" ]; then
  print_env_mode
fi

# Convert HEADLESS env to pytest --headless flag
if [ "$HEADLESS" = "1" ] || [ "$HEADLESS" = "true" ] || [ "$HEADLESS" = "yes" ]; then
  HEADLESS_FLAG="--headless"
else
  HEADLESS_FLAG=""
fi

# If explicit args were passed, bypass defaults and run pytest directly
if [ "$#" -gt 0 ]; then
  exec pytest "$@"
else
  # Build pytest argument list (each item becomes separate argv entry)
  # We use -vv (verbose) — keep it if you like or change to -q
  set -- \
    -vv \
    --base-url "$BASE_URL" \
    --browser "$BROWSER" \
    -m "$MARKER" \
    -n "$XDIST" \
    $HEADLESS_FLAG \
    --reruns "$RERUNS" \
    --reruns-delay "$RERUNS_DELAY" \
    $EXTRA_ARGS

  # Run pytest with constructed args
  exec pytest "$@"
fi