"""Console entry point for the OrbitFabric F Prime adapter."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .constants import OPERATION_ID, VERSION
from .execution import execute_projection
from .result import failed_result, write_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="orbitfabric-fprime",
        description="OrbitFabric adapter for F Prime (F´).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    subparsers = parser.add_subparsers(dest="command")
    run = subparsers.add_parser(
        "run",
        help="Execute an adapter operation through the OrbitFabric adapter CLI protocol.",
    )
    run.add_argument("--operation", required=True)
    run.add_argument("--input-set-manifest", required=True)
    run.add_argument("--profile", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--operation-input", action="append", default=[])

    return parser


def _write_failure(output_dir: Path, message: str) -> None:
    try:
        write_result(output_dir, failed_result(message))
    except OSError:
        pass


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    output_dir = Path(args.output_dir)
    if args.operation != OPERATION_ID:
        message = f"unsupported operation: {args.operation}"
        _write_failure(output_dir, message)
        print(message, file=sys.stderr)
        return 2

    if args.operation_input:
        message = f"{OPERATION_ID} does not accept operation inputs"
        _write_failure(output_dir, message)
        print(message, file=sys.stderr)
        return 2

    try:
        execute_projection(
            manifest_path=Path(args.input_set_manifest),
            profile_path=Path(args.profile),
            output_dir=output_dir,
        )
    except (OSError, ValueError) as exc:
        message = str(exc)
        _write_failure(output_dir, message)
        print(message, file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
