from __future__ import annotations

import argparse
import json
import sys
from . import __version__
from .scanner import SEVERITY, scan_project

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="docker-doctor", description="Statically diagnose common Dockerfile and Compose risks.")
    p.add_argument("path", nargs="?", default=".", help="Docker project directory (default: current directory)")
    p.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable JSON")
    p.add_argument("--fail-on", choices=("info", "warning", "error", "never"), default="error", help="Exit 1 when this severity or higher is found (default: error)")
    p.add_argument("--version", action="version", version=f"docker-doctor {__version__} — Radwan Abdulhadi Ahmed (@rad03i2)")
    return p

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = scan_project(args.path)
    except (OSError, ValueError) as exc:
        print(f"docker-doctor: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"Docker Doctor — {report.root}")
        print(f"Scanned: {', '.join(report.files_scanned) if report.files_scanned else 'none'}")
        if not report.findings:
            print("No findings.")
        for f in report.findings:
            where = f"{f.path}:{f.line}" if f.line else f.path
            print(f"[{f.severity.upper():7}] {f.code} {where} — {f.message}")
            if f.hint:
                print(f"          Hint: {f.hint}")
        c = report.counts
        print(f"Summary: {c['error']} error(s), {c['warning']} warning(s), {c['info']} info")
    if args.fail_on == "never":
        return 0
    threshold = SEVERITY[args.fail_on]
    return 1 if any(SEVERITY[f.severity] >= threshold for f in report.findings) else 0

if __name__ == "__main__":
    raise SystemExit(main())
