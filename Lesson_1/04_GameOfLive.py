import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Global grid variable
# In rhino needs to be a global sticky Rhino Variable for "looping" the animation
# https://developer.rhino3d.com/guides/rhinopython/ghpython-global-sticky/
grid = None


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


def update_grid():
    """Apply Game of Life rules to update the grid."""
    global grid
    neighbor_count = count_neighbors(grid)
    
    # Rule 1: Any live cell with 2 or 3 neighbors survives
    # Rule 2: Any dead cell with exactly 3 neighbors becomes alive
    # Rule 3: All other cells die or stay dead
    grid = ((grid == 1) & ((neighbor_count == 2) | (neighbor_count == 3))) | \
           ((grid == 0) & (neighbor_count == 3))
    
    grid = grid.astype(int)


def initialize_glider():
    """Create a grid with a glider pattern."""
    global grid
    grid = np.zeros((50, 50), dtype=int)
    
    # Glider pattern
    glider = np.array([[0, 1, 0],
                       [0, 0, 1],
                       [1, 1, 1]])
        
    grid[10:13, 10:13] = glider
    

def initilize_random_pattern():
    """Create a grid with a random pattern."""
    global grid
    grid = np.random.randint(0, 2, (50, 50), dtype=int)


# ================================================================
# Everything below needs to be changed for the Rhino animations
# ================================================================

def run_game_of_life(generations=100, interval=20):
    """Run and visualize the Game of Life."""
    fig, ax = plt.subplots(figsize=(8, 8))
    
    img = ax.imshow(grid, cmap='binary', interpolation='nearest')
    ax.set_title('Conway\'s Game of Life')
    ax.axis('off')
    
    def animate(frame):
        update_grid()
        img.set_data(grid)
        ax.set_title(f'Conway\'s Game of Life - Generation {frame + 1}')
        return [img]
    
    _ = FuncAnimation(fig, animate, frames=generations, interval=interval, blit=True)
    plt.show()


if __name__ == '__main__':
    # Initialize grid with a glider pattern
    # initialize_glider()
    initilize_random_pattern()
    
    # Run the simulation
    run_game_of_life(generations=100, interval=20)

