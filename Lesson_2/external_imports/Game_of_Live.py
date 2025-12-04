import numpy as np


def count_neighbors(input_grid):
    """Count live neighbors for each cell using convolution."""
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])
    
    # Pad the grid with zeros to handle edges
    padded_grid = np.pad(input_grid, pad_width=1, mode='constant', constant_values=0)
    
    # Count neighbors for each cell
    rows, cols = input_grid.shape
    neighbor_count = np.zeros_like(input_grid)
    
    for i in range(rows):
        for j in range(cols):
            neighbor_count[i, j] = np.sum(padded_grid[i:i+3, j:j+3] * kernel)
    
    return neighbor_count


def update_grid(grid):
    """Apply Game of Life rules to update the grid.
    
    Args:
        grid: numpy array representing the current state
    
    Returns:
        numpy array: updated grid
    """
    neighbor_count = count_neighbors(grid)
    
    # Rule 1: Any live cell with 2 or 3 neighbors survives
    # Rule 2: Any dead cell with exactly 3 neighbors becomes alive
    # Rule 3: All other cells die or stay dead
    new_grid = ((grid == 1) & ((neighbor_count == 2) | (neighbor_count == 3))) | \
               ((grid == 0) & (neighbor_count == 3))
    
    return new_grid.astype(int)


def initialize_glider(grid_size=50):
    """Create a grid with a glider pattern.
    
    Args:
        grid_size: size of the grid (default 50x50)
    
    Returns:
        numpy array: initialized grid with glider pattern
    """
    grid = np.zeros((grid_size, grid_size), dtype=int)
    
    # Glider pattern
    glider = np.array([[0, 1, 0],
                       [0, 0, 1],
                       [1, 1, 1]])
    
    grid[10:13, 10:13] = glider
    
    return grid


def initialize_random_pattern(grid_size=50):
    """Create a grid with a random pattern.
    
    Args:
        grid_size: size of the grid (default 50x50)
    
    Returns:
        numpy array: initialized grid with random pattern
    """
    return np.random.randint(0, 2, (grid_size, grid_size), dtype=int)


def initialize_game_of_life(grid_size=50, pattern='random'):
    """Initialize grid for Game of Life.
    
    Args:
        grid_size: size of the grid (default 50x50)
        pattern: 'random' or 'glider' (default 'random')
    
    Returns:
        tuple: (grid, generation)
        grid: numpy array representing the grid
        generation: current generation number (starts at 0)
    """
    if pattern == 'glider':
        grid = initialize_glider(grid_size)
    else:
        grid = initialize_random_pattern(grid_size)
    
    return grid, 0


def step_game_of_life(grid, generation):
    """Advance one generation in the Game of Life.
    
    Args:
        grid: numpy array representing the current state
        generation: current generation number
    
    Returns:
        tuple: (updated_grid, updated_generation)
    """
    if grid is None:
        return grid, generation
    
    new_grid = update_grid(grid)
    new_generation = generation + 1
    
    return new_grid, new_generation

