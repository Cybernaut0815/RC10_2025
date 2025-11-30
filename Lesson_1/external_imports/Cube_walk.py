import numpy as np
import Rhino.Geometry as rg

def get_valid_moves(position, grid):
    """Get valid next moves using cross kernel pattern."""
    # 2d kernel
    kernel = np.array([[0, 1, 0],
                        [1, 0, 1],
                        [0, 1, 0]])
    

    # 3d kernel
    # kernel3d = np.array([[[0, 0, 0],[0, 1, 0],[0, 0, 0]],
    #                     [[0, 1, 0],[1, 0, 1],[0, 1, 0]],
    #                     [[0, 0, 0],[0, 1, 0],[0, 0, 0]]])

    row, col = position
    rows, cols = grid.shape
    valid_moves = []
    
    # Check all 4 directions (up, down, left, right)
    for di in range(-1, 2):
        for dj in range(-1, 2):
            # add range for 3d here
            # for dk in range(-1, 2):
            if kernel[di + 1, dj + 1] == 1:
                new_row = row + di
                new_col = col + dj
                
                # Check if in bounds and not visited
                if 0 <= new_row < rows and 0 <= new_col < cols:
                    if grid[new_row, new_col] == 0:
                        valid_moves.append((new_row, new_col))
    
    return valid_moves


def choose_next_position(grid, current_position):
    """Choose next random valid position and update grid.
    
    Returns:
        tuple: (success, updated_grid, updated_position)
        success: True if step was taken, False if game over
    """
    valid_moves = get_valid_moves(current_position, grid)
    
    if len(valid_moves) == 0:
        return False, grid, current_position  # No valid moves, game over
    
    # Randomly choose next position
    next_position = valid_moves[int(np.random.randint(len(valid_moves)))]
    
    # Mark position as visited (create copy to avoid modifying original)
    new_grid = grid.copy()
    new_grid[next_position[0], next_position[1]] = 1
    
    return True, new_grid, next_position


def initialize_cube_walk(y_size, x_size):
    """Initialize grid with random starting position.
    
    Returns:
        tuple: (grid, current_position, game_over)
    """
    grid = np.zeros((y_size, x_size), dtype=int)    
    
    # Random starting position
    start_row = np.random.randint(0, y_size)
    start_col = np.random.randint(0, x_size)
    current_position = (start_row, start_col)

    # Mark starting position
    grid[start_row, start_col] = 1

    return grid, current_position, False


def step_cube_walk(grid, current_position, game_over):
    """Advance one step in the cube walk.
    
    Args:
        grid: numpy array representing the grid
        current_position: tuple (row, col) of current position
        game_over: boolean indicating if game is over
    
    Returns:
        tuple: (updated_grid, updated_position, updated_game_over)
    """
    if game_over:
        return grid, current_position, True
    
    if grid is None or current_position is None:
        return grid, current_position, game_over
    
    success, new_grid, new_position = choose_next_position(grid, current_position)
    
    if not success:
        return new_grid, new_position, True
    
    return new_grid, new_position, False

