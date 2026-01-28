"""
SBC Gen-I (350) to Jeep AX-15 (4.0L) Adapter Plate Generator
Outputs: SBC_to_AX15_adapter.stl

NOTE:
- Bolt patterns are REFERENCE ONLY.
- Verify all dimensions before machining.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np  # optional (kept for future math)
import trimesh


# Defaults (mm)
DEFAULT_THICKNESS = 25.4
DEFAULT_OUTER_RADIUS = 180.0
DEFAULT_CENTER_BORE_RADIUS = 60.0
DEFAULT_BOLT_RADIUS = 5.0

# Bolt patterns (mm) — reference only
CHEVY_BOLTS = [
    (76.0, 95.0), (-76.0, 95.0), (100.0, 0.0),
    (76.0, -95.0), (-76.0, -95.0), (-100.0, 0.0)
]

JEEP_BOLTS = [
    (85.0, 110.0), (-85.0, 110.0), (120.0, 0.0),
    (85.0, -110.0), (-85.0, -110.0), (-120.0, 0.0)
]


def desktop_dir() -> Path:
    """Return the user's Desktop if it exists; otherwise, use current working dir."""
    d = Path.home() / "Desktop"
    return d if d.exists() else Path.cwd()


def prompt_float(label: str, default: float) -> float:
    """Prompt user; Enter accepts default."""
    while True:
        raw = input(f"{label} [{default}]: ").strip()
        if raw == "":
            return default
        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number.")


def build_adapter(
    thickness: float,
    outer_radius: float,
    center_bore_radius: float,
    bolt_radius: float
) -> trimesh.Trimesh:
    plate = trimesh.creation.cylinder(radius=outer_radius, height=thickness, sections=160)
    plate.apply_translation([0, 0, thickness / 2])

    center_bore = trimesh.creation.cylinder(radius=center_bore_radius, height=thickness + 2, sections=80)
    center_bore.apply_translation([0, 0, thickness / 2])

    adapter = plate.difference(center_bore)

    for (x, y) in (CHEVY_BOLTS + JEEP_BOLTS):
        hole = trimesh.creation.cylinder(radius=bolt_radius, height=thickness + 2, sections=48)
        hole.apply_translation([x, y, thickness / 2])
        adapter = adapter.difference(hole)

    return adapter


def main() -> int:
    parser = argparse.ArgumentParser(description="SBC -> AX15 Adapter Plate STL Generator")
    parser.add_argument("--thickness", type=float, default=None, help="Plate thickness (mm)")
    parser.add_argument("--outer-radius", type=float, default=None, help="Outer radius (mm)")
    parser.add_argument("--center-bore-radius", type=float, default=None, help="Center bore radius (mm)")
    parser.add_argument("--bolt-radius", type=float, default=None, help="Bolt hole radius (mm)")
    parser.add_argument("--output-name", type=str, default="SBC_to_AX15_adapter.stl", help="Output STL filename")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory (default: Desktop)")
    args = parser.parse_args()

    print("\nEnter dimensions in millimeters. Press Enter to accept the default.\n")

    thickness = args.thickness if args.thickness is not None else prompt_float("THICKNESS", DEFAULT_THICKNESS)
    outer_radius = args.outer_radius if args.outer_radius is not None else prompt_float("OUTER_RADIUS", DEFAULT_OUTER_RADIUS)
    center_bore_radius = args.center_bore_radius if args.center_bore_radius is not None else prompt_float("CENTER_BORE_RADIUS", DEFAULT_CENTER_BORE_RADIUS)
    bolt_radius = args.bolt_radius if args.bolt_radius is not None else prompt_float("BOLT_RADIUS", DEFAULT_BOLT_RADIUS)

    out_dir = Path(args.output_dir) if args.output_dir else desktop_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / args.output_name

    print("\nGenerating STL with:")
    print(f"  thickness          = {thickness}")
    print(f"  outer_radius       = {outer_radius}")
    print(f"  center_bore_radius = {center_bore_radius}")
    print(f"  bolt_radius        = {bolt_radius}")
    print(f"\nSaving to: {out_path}\n")

    adapter = build_adapter(thickness, outer_radius, center_bore_radius, bolt_radius)
    adapter.export(str(out_path))

    print(f"Export complete: {out_path}")
    input("\nPress Enter to close...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())