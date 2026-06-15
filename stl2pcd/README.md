# stl2pcd

Convert STL, PLY, or OBJ mesh files to PCD point clouds using Open3D uniform sampling.
Supports single-file and batch (folder) conversion.

## Setup

```bash
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r ../requirements.txt
```

## Usage

```
python stl2pcd.py <input> [-o OUTPUT] [-n NUM_POINTS] [--visualize]
```

### Arguments

| Argument | Description |
|---|---|
| `input` | Path to a mesh file or a folder of mesh files |
| `-o`, `--output` | Output `.pcd` file or folder. Defaults to same directory as input |
| `-n`, `--num-points` | Number of points to sample uniformly (default: `40000`) |
| `--visualize` | Open an Open3D 3D viewer after each conversion |

### Input formats

`.stl` `.ply` `.obj`

## Examples

```bash
# Single file — output written next to input
python stl2pcd.py ../Model_STL/T1.STL

# Single file with explicit output path
python stl2pcd.py ../Model_STL/T1.STL -o /tmp/T1.pcd

# Single file, open viewer after conversion
python stl2pcd.py ../Model_STL/T1.STL --visualize

# Custom point count
python stl2pcd.py ../Model_STL/T1.STL -n 80000

# Batch: convert all meshes in a folder
python stl2pcd.py ../Model_STL/

# Batch: convert all meshes, write PCDs to a separate folder
python stl2pcd.py ../Model_STL/ -o /tmp/clouds/

# Batch with viewer (opens a window per file — close each to continue)
python stl2pcd.py ../Model_STL/ --visualize
```

## How it works

1. Loads the mesh with **trimesh**
2. Exports to a temporary `.ply` for Open3D compatibility
3. Samples `N` points uniformly across the mesh surface via **Open3D**
4. Optionally visualizes the point cloud
5. Writes the output `.pcd`
6. Cleans up the intermediate `.ply`

## Notes

- **Headless environments** (SSH, CI): omit `--visualize`; the rest of the pipeline runs fine without a display.
- **Output path rules**: if `-o` ends with `/` or has no file extension, it is treated as a directory and the filename is derived from the input stem. Otherwise it is used as the exact output file path (only meaningful for single-file conversion).
- **Batch output naming**: each output file takes the stem of its input (e.g. `T1.STL` → `T1.pcd`).
