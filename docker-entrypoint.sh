#!/bin/sh
set -e

# HOME=/data → XDG-style paths resolve to /data/.config/alters-lab, /data/.local/share/alters-lab, etc.
DATA_DIR="$HOME/.local/share/alters-lab"
CONFIG_DIR="$HOME/.config/alters-lab"
STATE_DIR="$HOME/.local/state/alters-lab"
APP_ROOT="${ALTERS_LAB_APP_ROOT:-/opt/alters-lab}"

# Ensure all data directories exist
mkdir -p "$DATA_DIR/alters/current/alters"
mkdir -p "$DATA_DIR/alters/sample"
mkdir -p "$DATA_DIR/alters/product/config"
mkdir -p "$STATE_DIR/logs"
mkdir -p "$DATA_DIR/alters/product/sessions"
mkdir -p "$DATA_DIR/alters/product/weekly_notes"
mkdir -p "$DATA_DIR/alters/product/weekly_reviews"
mkdir -p "$DATA_DIR/alters/product/calibration_records"
mkdir -p "$DATA_DIR/alters/product/pattern_reviews"
mkdir -p "$DATA_DIR/alters/product/behavior_validation"
mkdir -p "$DATA_DIR/alters/product/provider_runs"
mkdir -p "$DATA_DIR/alters/product/workflow_runs"
mkdir -p "$DATA_DIR/alters/product/alter_recommendations"
mkdir -p "$DATA_DIR/alters/product/self_deception_challenges"
mkdir -p "$DATA_DIR/alters/product/reminders"
mkdir -p "$DATA_DIR/alters/product/exports"
mkdir -p "$CONFIG_DIR"

# Copy sample data from installed location to data volume (first run only)
if [ ! -f "$DATA_DIR/alters/sample/snapshot.yaml" ] && [ -f "$APP_ROOT/alters/sample/snapshot.yaml" ]; then
    cp -r "$APP_ROOT/alters/sample/"* "$DATA_DIR/alters/sample/"
    echo "[entrypoint] Sample data initialized."
fi

# Copy default config if not present
if [ ! -f "$CONFIG_DIR/config.yaml" ] && [ -f "$APP_ROOT/alters/product/config/config.yaml" ]; then
    cp "$APP_ROOT/alters/product/config/config.yaml" "$CONFIG_DIR/config.yaml"
    echo "[entrypoint] Default config initialized."
fi

# Auto-load sample data on first run (when current/ is empty)
if [ ! -f "$DATA_DIR/alters/current/snapshot.yaml" ] && [ -f "$DATA_DIR/alters/sample/snapshot.yaml" ]; then
    cp "$DATA_DIR/alters/sample/snapshot.yaml" "$DATA_DIR/alters/current/snapshot.yaml"
    cp "$DATA_DIR/alters/sample/branches.yaml" "$DATA_DIR/alters/current/branches.yaml" 2>/dev/null || true
    if [ -d "$DATA_DIR/alters/sample/alters" ]; then
        cp -r "$DATA_DIR/alters/sample/alters/"* "$DATA_DIR/alters/current/alters/" 2>/dev/null || true
    fi
    if [ -f "$DATA_DIR/alters/sample/reality_trace.yaml" ]; then
        cp "$DATA_DIR/alters/sample/reality_trace.yaml" "$DATA_DIR/alters/current/reality_trace.yaml"
    fi
    echo "[entrypoint] Sample data loaded into active directory."
fi

exec "$@"
