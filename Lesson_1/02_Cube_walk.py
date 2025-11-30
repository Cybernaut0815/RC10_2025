#! python3
# r: numpy

import numpy as np
import pathlib
import importlib
import sys

sys.path.append(r'%USERPROFILE%\\Documents\\RC10\\2025_2026\\Lesson_1\\external_imports')
import Cube_walk
importlib.reload(Cube_walk)


# Initialize on reset
if reset:
    Cube_walk.initialize_cube_walk()

# Step forward when ticker runs
if run:
    Cube_walk.step_cube_walk()

# Get visualization geometry
visited, current = Cube_walk.get_cube_walk_geometry(cell_size=cell_size)

# Get status information
status_info = Cube_walk.get_cube_walk_status()
path_length = status_info["path_length"]
game_over = status_info["game_over"]
status = status_info["status"]