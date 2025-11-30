#! python3
# r: numpy

import scriptcontext as sc
import Rhino.Geometry as rg
import sys
import os

sys.path.append(os.path.expandvars(r'%USERPROFILE%\Documents\RC10\2025_2026\RC10_2025\Lesson_1\external_imports'))
import Cube_walk


# Get state from sticky variables
grid = sc.sticky.get("cube_walk_grid")
current_position = sc.sticky.get("cube_walk_current_position")
game_over = sc.sticky.get("cube_walk_game_over", False)

# Initialize on reset or if not yet initialized
if _reset or grid is None:
    grid, current_position, game_over = Cube_walk.initialize_cube_walk(_xSize, _ySize)
    sc.sticky["cube_walk_grid"] = grid
    sc.sticky["cube_walk_current_position"] = current_position
    sc.sticky["cube_walk_game_over"] = game_over
    # Reset geometry list on initialization
    sc.sticky["geo_out"] = []
    sc.sticky["rendered_path_length"] = 0

# Step forward when ticker runs
if _run:
    grid, current_position, game_over = Cube_walk.step_cube_walk(
        grid, current_position, game_over
    )
    sc.sticky["cube_walk_grid"] = grid
    sc.sticky["cube_walk_current_position"] = current_position
    sc.sticky["cube_walk_game_over"] = game_over

# Get saved geometry list and only add new cubes
geo_out = sc.sticky.get("geo_out", [])

# Only add new cubes if path has grown and still running
is_running = not game_over
if is_running and grid is not None and _run:
    cell_size = 1.0
    # Add cube for the current position (newly visited cell)
    base_plane = rg.Plane(rg.Point3d(current_position[1] * cell_size, current_position[0] * cell_size, 0), rg.Vector3d.ZAxis)
    box = rg.Box(base_plane, 
                rg.Interval(0, cell_size),
                rg.Interval(0, cell_size),
                rg.Interval(0, cell_size))
    geo_out.append(box.ToBrep())
    sc.sticky["geo_out"] = geo_out

