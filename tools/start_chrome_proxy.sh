#!/usr/bin/env bash
set -euo pipefail

# Start a GUI Chrome instance for CDP automation with all external traffic
# routed through the local Clash Verge HTTP proxy.

CDP_PORT="${CDP_PORT:-9222}"
CDP_ADDRESS="${CDP_ADDRESS:-127.0.0.1}"
PROXY_SERVER="${PROXY_SERVER:-http://127.0.0.1:7897}"
CHROME_USER_DATA_DIR="${CHROME_USER_DATA_DIR:-/tmp/chrome-debug-profile}"
CHROME_START_URL="${CHROME_START_URL:-about:blank}"
CHROME_LOG="${CHROME_LOG:-/tmp/chrome-proxy-cdp.log}"

DISPLAY="${DISPLAY:-:0}"
XAUTHORITY="${XAUTHORITY:-/run/user/1000/.mutter-Xwaylandauth.DZGGP3}"
WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export DISPLAY XAUTHORITY WAYLAND_DISPLAY

find_chrome() {
  if [[ -n "${CHROME_BIN:-}" ]]; then
    printf '%s\n' "$CHROME_BIN"
    return
  fi

  command -v google-chrome \
    || command -v google-chrome-stable \
    || command -v chromium \
    || command -v chromium-browser
}

port_is_listening() {
  ss -ltn "sport = :$CDP_PORT" | grep -q "$CDP_ADDRESS:$CDP_PORT"
}

warn_if_proxy_is_down() {
  local proxy_address proxy_host proxy_port
  proxy_address="${PROXY_SERVER#*://}"
  proxy_address="${proxy_address%%/*}"
  proxy_host="${proxy_address%:*}"
  proxy_port="${proxy_address##*:}"

  if [[ -z "$proxy_host" || -z "$proxy_port" || "$proxy_host" == "$proxy_port" ]]; then
    printf 'Could not parse PROXY_SERVER=%s; Chrome will still receive it as-is.\n' "$PROXY_SERVER" >&2
    return 0
  fi

  if ! ss -ltn "sport = :$proxy_port" | grep -q "$proxy_host:$proxy_port"; then
    printf 'Warning: proxy %s does not appear to be listening right now.\n' "$PROXY_SERVER" >&2
  fi
}

wait_for_port_down() {
  for _ in {1..50}; do
    if ! port_is_listening; then
      return 0
    fi
    sleep 0.1
  done
  return 1
}

wait_for_cdp() {
  for _ in {1..100}; do
    if curl -fsS "http://$CDP_ADDRESS:$CDP_PORT/json/version" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.1
  done
  return 1
}

matching_chrome_pids() {
  pgrep -af 'chrome|chromium' \
    | grep -- "--remote-debugging-port=$CDP_PORT" \
    | grep -- "--user-data-dir=$CHROME_USER_DATA_DIR" \
    | awk '$0 !~ / --type=/ { print $1 }' \
    || true
}

close_existing_chrome() {
  local pids
  pids="$(matching_chrome_pids)"

  if [[ -z "$pids" ]]; then
    return 0
  fi

  printf 'Closing existing Chrome for CDP port %s and profile %s: %s\n' "$CDP_PORT" "$CHROME_USER_DATA_DIR" "$pids"
  # shellcheck disable=SC2086
  kill -TERM $pids
  if wait_for_port_down; then
    return 0
  fi

  printf 'Chrome did not stop after SIGTERM; sending SIGKILL to the same matched process(es).\n' >&2
  # shellcheck disable=SC2086
  kill -KILL $pids 2>/dev/null || true
  wait_for_port_down
}

clear_stale_singleton_files() {
  if [[ -n "$(matching_chrome_pids)" ]] || port_is_listening; then
    return 0
  fi

  rm -f \
    "$CHROME_USER_DATA_DIR/SingletonCookie" \
    "$CHROME_USER_DATA_DIR/SingletonLock" \
    "$CHROME_USER_DATA_DIR/SingletonSocket"
}

main() {
  local chrome_bin
  chrome_bin="$(find_chrome)"

  if [[ -z "$chrome_bin" ]]; then
    printf 'Could not find google-chrome or chromium on PATH. Set CHROME_BIN explicitly.\n' >&2
    return 1
  fi

  warn_if_proxy_is_down

  close_existing_chrome
  mkdir -p "$CHROME_USER_DATA_DIR"
  clear_stale_singleton_files

  printf 'Starting Chrome with proxy %s, CDP %s:%s, profile %s\n' \
    "$PROXY_SERVER" "$CDP_ADDRESS" "$CDP_PORT" "$CHROME_USER_DATA_DIR"

  setsid -f "$chrome_bin" \
    --remote-debugging-address="$CDP_ADDRESS" \
    --remote-debugging-port="$CDP_PORT" \
    --user-data-dir="$CHROME_USER_DATA_DIR" \
    --proxy-server="$PROXY_SERVER" \
    --no-first-run \
    --no-default-browser-check \
    "$CHROME_START_URL" \
    >"$CHROME_LOG" 2>&1

  if ! wait_for_cdp; then
    printf 'Chrome did not expose CDP at http://%s:%s. See %s\n' "$CDP_ADDRESS" "$CDP_PORT" "$CHROME_LOG" >&2
    return 1
  fi

  printf 'Chrome is ready: http://%s:%s/json/version\n' "$CDP_ADDRESS" "$CDP_PORT"
  printf 'Log: %s\n' "$CHROME_LOG"
}

main "$@"
