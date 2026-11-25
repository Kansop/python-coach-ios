#!/usr/bin/env python3
"""Run every lesson check and print pass counts. Does not write any files.

  python3 Scripts/check_lessons.py                      # this machine's Python
  python3 Scripts/check_lessons.py --pyodide DIR         # real Pyodide 0.26.4 under Node

For --pyodide, DIR is a folder where `npm install pyodide@0.26.4` has been run.
"""

from __future__ import annotations

import argparse
import sys

from build_curriculum import audit, print_report
from coach_checks import CPythonRunner, PyodideRunner, self_test


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pyodide", metavar="DIR", help="folder with the pyodide npm package installed")
    args = parser.parse_args()
    self_test()
    runner = PyodideRunner(args.pyodide) if args.pyodide else CPythonRunner()
    try:
        _, report = audit(runner)
    finally:
        runner.close()
    print_report(report)
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
