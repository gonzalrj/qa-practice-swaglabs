#!/bin/sh
# entrypoint.sh - build pytest args from env or run explicit args

# defaults (can be overridden by -e ENV=)
: "${BASE_URL:=https://www.saucedemo.com/}"
: "${MARKER:=regression}"
: "${XDIST:=auto}"
: "${HEADLESS:=true}"
: "${EXTRA_ARGS:=}"

# Convert HEADLESS env to pytest --headless flag presence
if [ "$HEADLESS" = "1" ] || [ "$HEADLESS" = "true" ] || [ "$HEADLESS" = "yes" ]; then
  HEADLESS_FLAG="--headless"
else
  HEADLESS_FLAG=""
fi

# If user passed explicit args to docker run, use them (they take precedence)
if [ "$#" -gt 0 ]; then
  exec pytest "$@"
else
  # Build positional args safely so each option becomes its own argv entry
  set -- \
    -v \
    --base-url "$BASE_URL" \
    -m "$MARKER" \
    -n "$XDIST" \
    $HEADLESS_FLAG \
    "$EXTRA_ARGS"

  # Run pytest with constructed args
  exec pytest "$@"
fi