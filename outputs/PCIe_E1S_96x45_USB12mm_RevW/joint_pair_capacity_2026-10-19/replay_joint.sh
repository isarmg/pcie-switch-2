#!/bin/bash
# Recompute into a NEW scratch directory. Never overwrite frozen evidence.
set -euo pipefail
CODE_DIR="$(cd "$(dirname "$0")" && pwd)"
: "${E1S_SOURCE:?Set E1S_SOURCE to the exact input .kicad_pcb path}"
: "${KICAD_APP:?Set KICAD_APP to the KiCad AppRun launcher path}"
OUT="${1:-${E1S_OUT_DIR:-}}"
if [[ -z "$OUT" ]]; then echo "Usage: E1S_SOURCE=/path/board.kicad_pcb KICAD_APP=/path/AppRun $0 /new/scratch/output" >&2; exit 2; fi
PY="${ROUTE_PYTHON:-python3}"
RENDER_PY="${RENDER_PYTHON:-python3}"
[[ -f "$E1S_SOURCE" ]] || { echo "Input board not found: $E1S_SOURCE" >&2; exit 2; }
[[ -x "$KICAD_APP" ]] || { echo "KiCad launcher is not executable: $KICAD_APP" >&2; exit 2; }
export E1S_SOURCE="$("$PY" -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$E1S_SOURCE")"
APP="$("$PY" -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$KICAD_APP")"
OUT="$("$PY" -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$OUT")"
if [[ -e "$OUT" ]]; then
  [[ -d "$OUT" ]] || { echo "Output exists and is not a directory: $OUT" >&2; exit 2; }
  [[ -z "$(find "$OUT" -mindepth 1 -print -quit)" ]] || { echo "Refusing to overwrite nonempty output: $OUT" >&2; exit 2; }
fi
mkdir -p "$OUT"
for name in extract_geometry.py check_via_diameters.py joint_routing_trial.py extend_x2_trial.py repair_rx1_escape_trial.py validate_joint_results.py render_joint_geometry.py; do
  cp "$CODE_DIR/$name" "$OUT/$name"
done
cp "$CODE_DIR/replay_joint.sh" "$OUT/replay_joint.sh"
cd "$OUT"
exec > >(tee "$OUT/replay.log") 2>&1
export HOME="$OUT/tool-home" XDG_CONFIG_HOME="$OUT/tool-home/config" XDG_CACHE_HOME="$OUT/tool-home/cache" TMPDIR="$OUT/tmp"
mkdir -p "$HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$TMPDIR"
printf 'Input: %s\nOutput: %s\nKiCad launcher: %s\n' "$E1S_SOURCE" "$OUT" "$APP"
"$APP" python3.11 extract_geometry.py --source "$E1S_SOURCE" --out "$OUT"
"$APP" python3.11 check_via_diameters.py
# Dependencies are explicit environment inputs, never inferred from a sibling study.
if [[ -n "${ROUTE_PYTHONPATH:-}" ]]; then export PYTHONPATH="$ROUTE_PYTHONPATH${PYTHONPATH:+:$PYTHONPATH}"; fi
"$PY" -c 'import sys,numpy,shapely; print("Route runtime:",sys.version.split()[0],"NumPy",numpy.__version__,"Shapely",shapely.__version__)'
"$PY" joint_routing_trial.py
"$PY" extend_x2_trial.py
"$PY" repair_rx1_escape_trial.py
"$PY" validate_joint_results.py
if [[ "${E1S_RENDER:-1}" == 1 ]]; then
  # Drawing is not the geometry check. Uses host matplotlib/Pillow only.
  env -u PYTHONPATH "$RENDER_PY" render_joint_geometry.py
else
  echo "Review drawing skipped by explicit E1S_RENDER=0; geometry checks were run."
fi
printf '\nReplay finished. Check JOINT_VALIDATION_SUMMARY.json. This is NOT a 24-layer PCB.\n'
