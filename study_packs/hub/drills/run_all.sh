#!/usr/bin/env bash
# Run all 5 drills anonymously, logging to ../evidence/. Usage: bash run_all.sh [/path/to/python]
set -uo pipefail
PY=${1:-/workspace/hf-venv/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
EVID="$HERE/../evidence"
mkdir -p "$EVID"
export HF_HOME=$(mktemp -d -t hf-home-drills-XXXX)   # isolated: no stored token, throwaway cache
export HF_HUB_DISABLE_TELEMETRY=1
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
SUMMARY="$EVID/run_summary.tsv"
printf "drill\texit_code\tstarted_local\n" > "$SUMMARY"
cd "$HERE"
for d in drill_0*.py; do
  name=${d%.py}
  ts=$(date '+%Y-%m-%d %H:%M:%S %Z')
  "$PY" "$d" > "$EVID/$name.log" 2>&1
  rc=$?
  echo "exit_code=$rc" >> "$EVID/$name.log"
  printf "%s\t%s\t%s\n" "$name" "$rc" "$ts" >> "$SUMMARY"
  echo "$name -> exit $rc"
done
rm -rf "$HF_HOME"
