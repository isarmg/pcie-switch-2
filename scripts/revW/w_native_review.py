"""Read-only native ERC/DRC/parity review of RevW, using Python's stdlib only.

Example (quote a multi-word command as ONE argument):
  python w_native_review.py --kicad-cli "/path/AppRun kicad-cli" \
      --output-dir /tmp/revw-review-001 \
      --pad-audit /path/to/NATIVE_ALL_PAD_AUDIT.json

Requires KiCad >=10. The output directory must be new or empty. Does not edit
design files, refill zones, lower rules, or run historical generation scripts.
Exit 0: native checks have no reported findings (still NOT production approval).
Exit 2: review completed with findings. Exit 3: tool/input/review failure.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S/Main_12E1S.kicad_pro"
SOURCE_SUFFIXES = {".kicad_pcb", ".kicad_sch", ".kicad_pro", ".kicad_dru", ".kicad_sym", ".kicad_mod"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_manifest(folder):
    return {str(path.relative_to(folder)): sha256(path)
            for path in sorted(folder.rglob("*"))
            if path.is_file() and (path.suffix in SOURCE_SUFFIXES or
                                   path.name in {"fp-lib-table", "sym-lib-table"})}


def counts(items):
    return {"count": len(items),
            "by_severity": dict(Counter(x.get("severity", "unknown") for x in items)),
            "by_type": dict(Counter(x.get("type", "unknown") for x in items))}


def command_prefix(value):
    # A real path can contain spaces (notably Windows Program Files).
    if Path(value).is_file():
        return [value]
    parts = shlex.split(value, posix=os.name != "nt")
    if os.name == "nt":
        parts = [x[1:-1] if len(x) > 1 and x[0] == x[-1] and x[0] in "\"'" else x for x in parts]
    return parts


def review(args):
    project = args.project.resolve()
    board, schematic = project.with_suffix(".kicad_pcb"), project.with_suffix(".kicad_sch")
    for path in (project, board, schematic):
        if not path.is_file():
            raise ValueError(f"Missing input: {path}")
    out = args.output_dir.resolve()
    # An output folder beneath the project would pollute source-manifest scans.
    if out == project.parent or project.parent in out.parents:
        raise ValueError("Output must be outside the input project directory")
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"Refusing to overwrite nonempty output directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    tool_home = tempfile.TemporaryDirectory(prefix="revw-review-tool-")
    home = Path(tool_home.name)
    for key, path in {"HOME": home, "XDG_CONFIG_HOME": home / "config",
                      "XDG_CACHE_HOME": home / "cache", "XDG_DATA_HOME": home / "data"}.items():
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    prefix = command_prefix(args.kicad_cli)
    if not prefix:
        raise ValueError("Empty KiCad CLI command")
    before = source_manifest(project.parent)
    report = {
        "schema_version": 1, "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "review_script_sha256": sha256(Path(__file__)),
        "project": str(project), "cli_command_prefix": prefix,
        "isolated_temporary_tool_configuration": True,
        "source_hashes_before": before, "commands": [],
        "review_status": "incomplete", "production_ready": False,
        "limitations": [
            "Native DRC/ERC do not qualify real part pinouts, electrical operation, firmware, SI, impedance, current, thermal design, or HDI manufacture.",
            "DRC uses saved zone fills; this read-only review does not refill or reroute the board.",
            "KiCad can cap reported findings (observed 199 per type and 499 unconnected items); counts are reported findings, not guaranteed totals.",
            "Local project/library sources are hashed; externally referenced libraries and application configuration are not comprehensively archived.",
        ],
    }
    failed = False

    def run(label, arguments):
        command = prefix + arguments
        record = {"label": label, "argv": command}
        report["commands"].append(record)
        try:
            proc = subprocess.run(command, env=env, capture_output=True,
                                  timeout=args.timeout, check=False)
            (out / f"{label}.stdout.log").write_bytes(proc.stdout)
            (out / f"{label}.stderr.log").write_bytes(proc.stderr)
            record["returncode"] = proc.returncode
            return proc.returncode, proc.stdout.decode("utf-8", errors="replace")
        except (OSError, subprocess.TimeoutExpired) as exc:
            record["error"] = str(exc)
            return None, ""

    try:
        code, version = run("version", ["version"])
        report["kicad_version_output"] = version.strip()
        match = re.search(r"(?m)^\s*(\d+)\.(\d+)(?:\.(\d+))?", version)
        if code != 0 or not match or int(match.group(1)) < 10:
            raise RuntimeError("KiCad >=10 is required; see version logs")
        jobs = {
            "ERC": ["sch", "erc", "--severity-all", "--format", "json", "-o", str(out / "ERC.json"), str(schematic)],
            "DRC": ["pcb", "drc", "--schematic-parity", "--all-track-errors", "--severity-all", "--format", "json", "-o", str(out / "DRC.json"), str(board)],
        }
        for label, command in jobs.items():
            code, _ = run(label, command)
            if code != 0 or not (out / f"{label}.json").is_file():
                failed = True
                report[label] = {"tool_failed": True}
                continue
            native = json.loads((out / f"{label}.json").read_text(encoding="utf-8"))
            if label == "ERC":
                if not isinstance(native.get("sheets"), list):
                    raise ValueError("ERC output has no sheets list; native report schema not recognized")
                items = [v for sheet in native.get("sheets", []) for v in sheet.get("violations", [])]
                report[label] = counts(items)
            else:
                if not all(isinstance(native.get(key), list) for key in
                           ("violations", "unconnected_items", "schematic_parity")):
                    raise ValueError("DRC output lacks required finding/parity lists; native report schema not recognized")
                report[label] = {key: counts(native.get(key, [])) for key in
                                 ("violations", "unconnected_items", "schematic_parity")}
                report[label]["ignored_checks"] = native.get("ignored_checks", [])
                report[label]["possible_report_cap_detected"] = (
                    len(native["unconnected_items"]) >= 499 or any(
                        n >= 199 for key in ("violations", "schematic_parity")
                        for n in Counter(x.get("type") for x in native[key]).values()))
            report[label]["native_report_sha256"] = sha256(out / f"{label}.json")
            report[label]["native_kicad_version"] = native.get("kicad_version")
        if args.pad_audit:
            source = args.pad_audit.resolve()
            data = json.loads(source.read_text(encoding="utf-8"))
            bound = data.get("board_sha256") == before[board.name]
            report["supplemental_pad_audit"] = {
                "source": str(source), "sha256": sha256(source),
                "matches_reviewed_board_sha256": bound,
                "data": data,
            }
            if not bound:
                failed = True
                report["limitations"].append("Supplemental pad audit is stale or lacks matching board hash; do not treat it as verification of this board.")
    except (ValueError, OSError, RuntimeError) as exc:
        failed = True
        report["failure"] = str(exc)
    finally:
        after = source_manifest(project.parent)
        report["source_hashes_after"] = after
        report["sources_unchanged_during_review"] = before == after
        if before != after:
            failed = True
            report["limitations"].append("Design sources changed during review; rerun after edits stop.")
        findings = report.get("ERC", {}).get("count", 0) + sum(
            report.get("DRC", {}).get(key, {}).get("count", 0)
            for key in ("violations", "unconnected_items", "schematic_parity"))
        report["native_checks_status"] = "review_failed" if failed else ("findings_present" if findings else "no_reported_findings")
        report["review_status"] = "review_failed" if failed else "incomplete_not_production_qualified"
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        (out / "REVIEW.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tool_home.cleanup()
    print(json.dumps({"report": str(out / "REVIEW.json"),
                      "native_checks_status": report["native_checks_status"],
                      "production_ready": False}, ensure_ascii=False))
    return 3 if failed else (2 if findings else 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--kicad-cli", default="kicad-cli", help="Executable path or quoted command prefix")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pad-audit", type=Path, help="Optional all-pad audit JSON; board hash must match")
    parser.add_argument("--timeout", type=float, default=600, help="Timeout in seconds per native invocation")
    args = parser.parse_args()
    try:
        return review(args)
    except (ValueError, OSError) as exc:
        print(f"Review failed: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
