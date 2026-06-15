#!/usr/bin/env python3
"""Convert STL mesh file(s) to PCD point clouds.

Examples:
    # Single file
    python stl2pcd.py model.stl

    # Single file, custom output path, visualize
    python stl2pcd.py model.stl -o output.pcd --visualize

    # Folder of STL files -> output folder
    python stl2pcd.py ./Model_STL/ -o ./clouds/

    # Custom sample count
    python stl2pcd.py model.stl -n 80000
"""

import argparse
import os
import sys

import open3d as o3d
import trimesh


SUPPORTED_EXTS = {".stl", ".ply", ".obj"}


def convert_mesh_to_pcd(input_path: str, output_path: str, num_points: int, visualize: bool) -> bool:
    """Convert a single mesh file to a PCD. Returns True on success."""
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in SUPPORTED_EXTS:
        print(f"[SKIP] Unsupported format: {input_path}")
        return False

    print(f"[INFO] Loading  : {input_path}")
    try:
        mesh = trimesh.load_mesh(input_path)
    except Exception as e:
        print(f"[ERROR] Failed to load {input_path}: {e}")
        return False

    # Export to PLY so Open3D can read it (trimesh -> open3d bridge)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    ply_path = output_path.rsplit(".", 1)[0] + ".ply"
    mesh.export(ply_path)

    mesh_o3d = o3d.io.read_triangle_mesh(ply_path)
    mesh_o3d.compute_vertex_normals()

    pcd = mesh_o3d.sample_points_uniformly(number_of_points=num_points)
    print(f"[INFO] Sampled  : {num_points} points")

    if visualize:
        print("[INFO] Visualizing — close the window to continue.")
        o3d.visualization.draw_geometries([pcd], window_name=os.path.basename(input_path))

    o3d.io.write_point_cloud(output_path, pcd)
    print(f"[INFO] Saved PCD: {output_path}\n")

    # Clean up intermediate PLY if it wasn't the original input
    if ext != ".ply" and os.path.exists(ply_path):
        os.remove(ply_path)

    return True


def resolve_output_path(input_path: str, output_arg: str | None) -> str:
    """Determine where to write the PCD for a given input file."""
    stem = os.path.splitext(os.path.basename(input_path))[0]
    pcd_name = stem + ".pcd"

    if output_arg is None:
        return os.path.join(os.path.dirname(os.path.abspath(input_path)), pcd_name)

    # If output looks like a directory (ends with / or has no extension), treat it as dir
    if output_arg.endswith(os.sep) or output_arg.endswith("/") or not os.path.splitext(output_arg)[1]:
        return os.path.join(output_arg, pcd_name)

    return output_arg


def collect_inputs(input_path: str) -> list[str]:
    """Return a list of mesh file paths from a file or directory."""
    if os.path.isfile(input_path):
        return [input_path]

    if os.path.isdir(input_path):
        files = []
        for fname in sorted(os.listdir(input_path)):
            if os.path.splitext(fname)[1].lower() in SUPPORTED_EXTS:
                files.append(os.path.join(input_path, fname))
        if not files:
            print(f"[ERROR] No supported mesh files found in: {input_path}")
            sys.exit(1)
        return files

    print(f"[ERROR] Path does not exist: {input_path}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert STL/PLY/OBJ mesh(es) to PCD point clouds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="Path to a mesh file or folder of mesh files.")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output .pcd file or output folder. Defaults to same directory as input.",
    )
    parser.add_argument(
        "-n", "--num-points",
        type=int,
        default=40000,
        help="Number of points to sample uniformly from the mesh (default: 40000).",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Open an Open3D viewer for each converted point cloud.",
    )

    args = parser.parse_args()

    inputs = collect_inputs(args.input)
    is_batch = len(inputs) > 1

    if is_batch:
        print(f"[INFO] Found {len(inputs)} mesh file(s) to convert.\n")

    success, failed = 0, 0
    for input_path in inputs:
        out = resolve_output_path(input_path, args.output)
        ok = convert_mesh_to_pcd(input_path, out, args.num_points, args.visualize)
        if ok:
            success += 1
        else:
            failed += 1

    if is_batch:
        print(f"[DONE] {success} converted, {failed} failed.")


if __name__ == "__main__":
    main()
