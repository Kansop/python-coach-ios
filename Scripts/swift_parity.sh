#!/usr/bin/env bash
# Builds the app's Foundation-only Swift files with a test main and checks them against real Python runs.
# Needs python3.12 and a Swift 5.10 toolchain on PATH. Works on Linux and macOS.
set -euo pipefail
cd "$(dirname "$0")"
out="${TMPDIR:-/tmp}/pycoach-parity"
mkdir -p "$out"
python3.12 swift_parity.py "$out/fixture.json"
app=../PythonCoach
swiftc -swift-version 5 -O -o "$out/parity" \
  "$app/Curriculum/Curriculum.swift" "$app/Curriculum/CurriculumJSON.swift" \
  "$app/Engine/LessonChecker.swift" "$app/Engine/FriendlyErrors.swift" "$app/Engine/RunModels.swift" \
  "$app/Engine/OutputNormalizer.swift" "$app/Engine/SourceScan.swift" \
  parity/main.swift
"$out/parity" "$out/fixture.json"
