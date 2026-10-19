#!/bin/bash
set -euo pipefail
CODE_DIR="$(cd "$(dirname "$0")" && pwd)"
: "${E1S_SOURCE:?Set exact source PCB path}"; : "${KICAD_APP:?Set native KiCad AppRun path}"
OUT="${1:-${E1S_OUT_DIR:-}}"; PY="${ROUTE_PYTHON:-python3}"
[[ -n "$OUT" && -f "$E1S_SOURCE" && -x "$KICAD_APP" ]] || { echo 'Need source, executable KiCad AppRun and new output directory' >&2; exit 2; }
export E1S_SOURCE="$("$PY" -c 'from pathlib import Path;import sys;print(Path(sys.argv[1]).resolve())' "$E1S_SOURCE")"
APP="$("$PY" -c 'from pathlib import Path;import sys;print(Path(sys.argv[1]).resolve())' "$KICAD_APP")"
OUT="$("$PY" -c 'from pathlib import Path;import sys;print(Path(sys.argv[1]).resolve())' "$OUT")"
if [[ -e "$OUT" ]]; then [[ -d "$OUT" && -z "$(find "$OUT" -mindepth 1 -print -quit)" ]] || { echo 'Refusing nonempty output' >&2; exit 2; }; fi
mkdir -p "$OUT"
for n in extract_geometry.py check_via_diameters.py joint_routing_trial.py reserved_escape_trial.py directed_port_trial.py test_directed_ports.py validate_reserved_results.py validate_direction_properties.py REGRESSION_OLD_RX1_THEN_RX0.json replay_directed.sh; do cp "$CODE_DIR/$n" "$OUT/$n"; done
cd "$OUT"; exec > >(tee "$OUT/replay.log") 2>&1
export HOME="$OUT/tool-home" XDG_CONFIG_HOME="$OUT/tool-home/config" XDG_CACHE_HOME="$OUT/tool-home/cache" TMPDIR="$OUT/tmp"
mkdir -p "$HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$TMPDIR"
"$APP" python3.11 extract_geometry.py --source "$E1S_SOURCE" --out "$OUT"
"$APP" python3.11 check_via_diameters.py
if [[ -n "${ROUTE_PYTHONPATH:-}" ]]; then export PYTHONPATH="$ROUTE_PYTHONPATH${PYTHONPATH:+:$PYTHONPATH}"; fi
"$PY" -c 'import numpy,shapely,scipy;print("Runtime",numpy.__version__,shapely.__version__,scipy.__version__)'
"$PY" test_directed_ports.py
"$PY" directed_port_trial.py
"$PY" validate_reserved_results.py
"$PY" validate_direction_properties.py
"$PY" test_directed_ports.py
printf '\nBounded direction-aware replay finished. Check exact reports; no native PCB/signoff.\n'
