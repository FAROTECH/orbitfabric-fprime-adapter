"""Console entry point for the OrbitFabric F Prime adapter."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .constants import OPERATION_ID, VERSION


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.operation != OPERATION_ID:
        parser.error(f"unsupported operation: {args.operation}")

    print(
        "F Prime projection execution is not included in the initial product bootstrap baseline.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
