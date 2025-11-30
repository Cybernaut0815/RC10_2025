import numpy as np
import scriptcontext as rs
import Rhino.Geometry as rg


rs.sticky["cube_walk_grid"] = None
rs.sticky["cube_walk_current_position"] = None
rs.sticky["cube_walk_path_length"] = 0

def get_valid_moves(position, grid):
    """Get valid next moves using cross kernel pattern."""
    kernel = np.array([[0, 1, 0],
                       [1, 0, 1],
                       [0, 1, 0]])
    
    row, col = position
    rows, cols = grid.shape
    valid_moves = []
    
    # Check all 4 directions (up, down, left, right)
    for di in range(-1, 2):
        for dj in range(-1, 2):
            if kernel[di + 1, dj + 1] == 1:
                new_row = row + di
                new_col = col + dj
                
                # Check if in bounds and not visited
                if 0 <= new_row < rows and 0 <= new_col < cols:
                    if grid[new_row, new_col] == 0:
                        valid_moves.append((new_row, new_col))
    
    return valid_moves


def choose_next_position():
    """Choose next random valid position and update grid."""
    current_position = rs.sticky["cube_walk_current_position"]
    path_length = rs.sticky["cube_walk_path_length"]
    grid = rs.sticky["cube_walk_grid"]
    
    valid_moves = get_valid_moves(current_position, grid)
    
    if len(valid_moves) == 0:
        return False  # No valid moves, game over
    
    # Randomly choose next position
    next_position = valid_moves[int(np.random.randint(len(valid_moves)))]
    current_position = next_position
    path_length += 1
    
    # Mark position as visited
    grid[current_position[0], current_position[1]] = 1
    
    rs.sticky["cube_walk_current_position"] = current_position
    rs.sticky["cube_walk_path_length"] = path_length   
    rs.sticky["cube_walk_grid"] = grid
    
    return True


def initialize_cube_walk():
    """Initialize grid with random starting position."""
    current_position = None
    path_length = 0
    grid = np.zeros((50, 50), dtype=int)    
    
    # Random starting position
    start_row = np.random.randint(0, 50)
    start_col = np.random.randint(0, 50)
    current_position = (start_row, start_col)
    path_length = 1

    # Mark starting position
    grid[start_row, start_col] = 1

    rs.sticky["cube_walk_grid"] = grid
    rs.sticky["cube_walk_current_position"] = current_position
    rs.sticky["cube_walk_path_length"] = path_length
    rs.sticky["cube_walk_game_over"] = False


def step_cube_walk():
    """Advance one step in the cube walk. Returns True if step was taken, False if game over."""
    if rs.sticky.get("cube_walk_game_over", False):
        return False
    
    success = choose_next_position()
    
    if not success:
        rs.sticky["cube_walk_game_over"] = True
    
    return success


def get_cube_walk_geometry(cell_size=1.0):
    """Generate Rhino geometry for visualization of the grid."""
    grid = rs.sticky.get("cube_walk_grid")
    current_position = rs.sticky.get("cube_walk_current_position")
    
    if grid is None:
        return [], []
    
    visited_boxes = []
    current_box = None
    
    rows, cols = grid.shape
    
    # Create boxes for visited cells
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] == 1:
                x = j * cell_size
                y = i * cell_size
                z = 0
                
                base_plane = rg.Plane(rg.Point3d(x, y, z), rg.Vector3d.ZAxis)
                box = rg.Box(base_plane, 
                            rg.Interval(0, cell_size),
                            rg.Interval(0, cell_size),
                            rg.Interval(0, cell_size * 0.5))
                
                # Highlight current position differently
                if current_position and (i, j) == current_position:
                    current_box = box.ToBrep()
                else:
                    visited_boxes.append(box.ToBrep())
    
    return visited_boxes, current_box


def get_cube_walk_status():
    """Get current status of the cube walk."""
    path_length = rs.sticky.get("cube_walk_path_length", 0)
    game_over = rs.sticky.get("cube_walk_game_over", False)
    current_position = rs.sticky.get("cube_walk_current_position")
    
    status = "Complete" if game_over else "Running"
    
    return {
        "path_length": path_length,
        "game_over": game_over,
        "status": status,
        "current_position": current_position
    }