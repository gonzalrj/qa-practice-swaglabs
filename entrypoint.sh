#!/bin/sh
# entrypoint.sh - build pytest args from env or run explicit args

# defaults (can be overridden by export or CI env vars)
: "${BASE_URL:=https://www.saucedemo.com/}"
: "${BROWSER:=chrome}"
: "${HEADLESS:=true}"
: "${MARKER:=regression}"
: "${XDIST:=auto}"
: "${RERUNS:=1}"
: "${RERUNS_DELAY:=1}"
: "${EXTRA_ARGS:=}"

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