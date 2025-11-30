#! python3
# r: numpy

import scriptcontext as sc
import Rhino.Geometry as rg
import sys
import os

sys.path.append(os.path.expandvars(r'%USERPROFILE%\Documents\RC10\2025_2026\RC10_2025\Lesson_2\external_imports'))
import Game_of_Live

# inputs
# grid size defines the size of the grid
# pattern defines the initial pattern of the grid (random or glider)

# Get state from sticky variables
grid = sc.sticky.get("game_of_life_grid")
generation = sc.sticky.get("game_of_life_generation", 0)

# Initialize on reset or if not yet initialized
if _reset or grid is None:
    grid, generation = Game_of_Live.initialize_game_of_life(_gridSize, _pattern)
    sc.sticky["game_of_life_grid"] = grid
    sc.sticky["game_of_life_generation"] = generation
    # Reset geometry list on initialization
    sc.sticky["geo_out"] = []

# Step forward when ticker runs
if _run:
    grid, generation = Game_of_Live.step_game_of_life(grid, generation)
    sc.sticky["game_of_life_grid"] = grid
    sc.sticky["game_of_life_generation"] = generation

    print(f"Generation: {generation}")

# Get saved geometry list
geo_out = sc.sticky.get("geo_out", [])

# Generate geometry for live cells
if grid is not None and _run:
    cell_size = 1.0
    rows, cols = grid.shape
    
    # Clear previous geometry and rebuild from current grid state
    geo_out = []
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] == 1:
                base_plane = rg.Plane(rg.Point3d(j * cell_size, i * cell_size, 0), rg.Vector3d.ZAxis)
                box = rg.Box(base_plane, 
                            rg.Interval(0, cell_size),
                            rg.Interval(0, cell_size),
                            rg.Interval(0, cell_size))
                geo_out.append(box.ToBrep())
    
    sc.sticky["geo_out"] = geo_out

