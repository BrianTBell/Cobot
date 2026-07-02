#!/usr/bin/env bash
set -euo pipefail

workspace_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$workspace_dir"

if [ -f /opt/ros/humble/setup.bash ]; then
  # Make colcon classify packages as ros.ament_* even from a fresh terminal.
  set +u
  source /opt/ros/humble/setup.bash
  set -u
fi

echo "Validating ROS package metadata..."

while IFS= read -r -d '' package_xml; do
  python3 - "$package_xml" <<'PY'
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
try:
    root = ET.parse(path).getroot()
except ET.ParseError as exc:
    raise SystemExit(f"{path}: invalid XML: {exc}")

name = root.findtext("name") or "<unknown>"
build_type = root.findtext("export/build_type")
if build_type not in {"ament_python", "ament_cmake"}:
    raise SystemExit(
        f"{path}: package '{name}' must export build_type "
        "ament_python or ament_cmake"
    )
PY
done < <(find src -mindepth 2 -maxdepth 2 -name package.xml -print0 | sort -z)

echo "Building workspace..."
colcon build "$@"

echo
echo "Done. Source with:"
echo "  source $workspace_dir/install/setup.bash"
