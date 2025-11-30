import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Global grid variable
# In rhino needs to be a global sticky Rhino Variable for "looping" the animation
# https://developer.rhino3d.com/guides/rhinopython/ghpython-global-sticky/

grid = None
current_position = None
path_length = 0


def get_valid_moves(position):
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
    global current_position, path_length, grid
    
    valid_moves = get_valid_moves(current_position)
    
    if len(valid_moves) == 0:
        return False  # No valid moves, game over
    
    # Randomly choose next position
    next_position = valid_moves[int(np.random.randint(len(valid_moves)))]
    current_position = next_position
    path_length += 1
    
    # Mark position as visited
    grid[current_position[0], current_position[1]] = 1
    
    return True


def initialize_snake():
    """Initialize grid with random starting position."""
    global grid, current_position, path_length
    grid = np.zeros((50, 50), dtype=int)
    
    # Random starting position
    start_row = np.random.randint(0, 50)
    start_col = np.random.randint(0, 50)
    current_position = (start_row, start_col)
    path_length = 1
    
    # Mark starting position
    grid[start_row, start_col] = 1

# ================================================================
# Everything below needs to be changed for the Rhino animations
# ================================================================

def run_snake(max_steps=2500, interval=50):
    """Run and visualize the snake path."""
    fig, ax = plt.subplots(figsize=(8, 8))
    
    img = ax.imshow(grid, cmap='binary', interpolation='nearest')
    ax.set_title(f'Snake Path - Steps: {path_length}')
    ax.axis('off')
    
    game_over = False
    
    def animate(_frame):
        nonlocal game_over
        
        if not game_over:
            game_over = not choose_next_position()
        
        img.set_data(grid)
        status = "Complete" if game_over else "Running"
        ax.set_title(f'Snake Path - Steps: {path_length} - {status}')
        return [img]
    
    _ = FuncAnimation(fig, animate, frames=max_steps, interval=interval, blit=True)
    plt.show()


if __name__ == '__main__':
    # Initialize grid with random starting position
    initialize_snake()
    
    # Run the simulation
    run_snake(max_steps=2500, interval=50)

