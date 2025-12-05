import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import json
import random


class Tile:
    def __init__(self, tile_name, tile_definition, tile_index):     
        self.tile_name = tile_name
        self.index = tile_index  # For fast lookup
        self.connections = tile_definition['connections']
        self.top = self.connections['top']
        self.right = self.connections['right']
        self.bottom = self.connections['bottom']
        self.left = self.connections['left']
        self.image = plt.imread(os.path.join(os.path.dirname(__file__), 'tiles', '2d', f'{tile_name}.png'))


class AdjacencyRules:
    """Pre-computed adjacency rules for fast constraint propagation."""
    def __init__(self, tiles: list, connections: dict) -> None:
        self.tiles = tiles
        self.num_tiles = len(tiles)
        # For each direction, store which tiles can be neighbors
        # adjacency[direction][tile_index] = set of valid neighbor tile indices
        self.adjacency = {
            'top': [set() for _ in range(self.num_tiles)],
            'right': [set() for _ in range(self.num_tiles)],
            'bottom': [set() for _ in range(self.num_tiles)],
            'left': [set() for _ in range(self.num_tiles)],
        }
        self._build_rules(connections)
    
    def _build_rules(self, connections: dict):
        """Pre-compute all valid adjacencies."""
        opposite = {'top': 'bottom', 'bottom': 'top', 'left': 'right', 'right': 'left'}
        
        for direction in ['top', 'right', 'bottom', 'left']:
            opp_dir = opposite[direction]
            for tile in self.tiles:
                edge = getattr(tile, direction)
                valid_edges = connections.get(edge, [])
                for other_tile in self.tiles:
                    other_edge = getattr(other_tile, opp_dir)
                    if other_edge in valid_edges:
                        self.adjacency[direction][tile.index].add(other_tile.index)
    
    def get_valid_neighbors(self, tile_indices: set, direction: str) -> set:
        """Get all tiles that can be neighbors in the given direction."""
        valid = set()
        for idx in tile_indices:
            valid.update(self.adjacency[direction][idx])
        return valid


class Cell:
    __slots__ = ['position', 'possible_tiles', 'collapsed', 'tile']
    
    def __init__(self, position: tuple, all_tile_indices: set) -> None:
        self.position = position
        self.possible_tiles = all_tile_indices.copy()  # Set of tile indices
        self.collapsed = False
        self.tile = None
    
    @property
    def entropy(self) -> int:
        return len(self.possible_tiles) if not self.collapsed else float('inf')
    
    def collapse(self, tiles: list) -> bool:
        """Collapse the cell to a single random tile."""
        if self.possible_tiles:
            tile_idx = random.choice(list(self.possible_tiles))
            self.tile = tiles[tile_idx]
            self.possible_tiles = {tile_idx}
            self.collapsed = True
            return True
        return False
    
    def constrain(self, valid_indices: set) -> bool:
        """Reduce possible tiles. Returns True if changed."""
        if self.collapsed:
            return False
        new_possible = self.possible_tiles & valid_indices
        if new_possible != self.possible_tiles:
            self.possible_tiles = new_possible
            return True
        return False


class Grid:
    def __init__(self, size: tuple, tiles: list, rules: AdjacencyRules) -> None:
        self.size = size
        self.tiles = tiles
        self.rules = rules
        self.all_tile_indices = set(range(len(tiles)))
        self.cells = self.create_grid()
        # Cache for image generation
        self.tile_size = tiles[0].image.shape[0] if tiles else 32
        self.channels = tiles[0].image.shape[2] if tiles and len(tiles[0].image.shape) > 2 else 3
        self.collapsed_count = 0
        
    def create_grid(self) -> list:
        """Create a 2D grid of cells."""
        return [[Cell((i, j), self.all_tile_indices) 
                 for j in range(self.size[1])] 
                for i in range(self.size[0])]
    
    def get_min_entropy_cell(self):
        """Find the uncollapsed cell with minimum entropy."""
        min_entropy = float('inf')
        min_cells = []
        
        for row in self.cells:
            for cell in row:
                if not cell.collapsed:
                    entropy = len(cell.possible_tiles)
                    if entropy < min_entropy:
                        min_entropy = entropy
                        min_cells = [cell]
                    elif entropy == min_entropy:
                        min_cells.append(cell)
        
        return random.choice(min_cells) if min_cells else None
    
    def propagate(self, cell: Cell) -> bool:
        """Propagate constraints using a stack."""
        stack = [cell]
        
        # Direction info: (row_offset, col_offset, direction, opposite_direction)
        directions = [
            (-1, 0, 'top', 'bottom'),
            (1, 0, 'bottom', 'top'),
            (0, -1, 'left', 'right'),
            (0, 1, 'right', 'left'),
        ]
        
        while stack:
            current = stack.pop()
            row, col = current.position
            
            for dr, dc, direction, _ in directions:
                n_row, n_col = row + dr, col + dc
                if not (0 <= n_row < self.size[0] and 0 <= n_col < self.size[1]):
                    continue
                    
                neighbor = self.cells[n_row][n_col]
                if neighbor.collapsed:
                    continue
                
                # Get valid tiles for neighbor based on current cell's possibilities
                valid_indices = self.rules.get_valid_neighbors(current.possible_tiles, direction)
                
                if neighbor.constrain(valid_indices):
                    if len(neighbor.possible_tiles) == 0:
                        return False  # Contradiction
                    stack.append(neighbor)
        
        return True
    
    def is_fully_collapsed(self) -> bool:
        return self.collapsed_count >= self.size[0] * self.size[1]
    
    def step(self) -> bool:
        """Perform one step of WFC."""
        cell = self.get_min_entropy_cell()
        if cell is None:
            return False
        
        if not cell.collapse(self.tiles):
            return False
        
        self.collapsed_count += 1
        
        if not self.propagate(cell):
            return False
        
        return True
    
    def run_steps(self, n: int) -> bool:
        """Run multiple steps. Returns False if contradiction."""
        for _ in range(n):
            if self.is_fully_collapsed():
                return True
            if not self.step():
                return False
        return True
    
    def get_image(self) -> np.ndarray:
        """Generate the current state as an image."""
        img = np.ones((self.size[0] * self.tile_size, 
                       self.size[1] * self.tile_size, 
                       self.channels), dtype=np.float32) * 0.7
        
        for i, row in enumerate(self.cells):
            y_start = i * self.tile_size
            y_end = y_start + self.tile_size
            for j, cell in enumerate(row):
                x_start = j * self.tile_size
                x_end = x_start + self.tile_size
                
                if cell.collapsed and cell.tile:
                    img[y_start:y_end, x_start:x_end] = cell.tile.image[:, :, :self.channels]
                else:
                    entropy_ratio = len(cell.possible_tiles) / len(self.tiles)
                    img[y_start:y_end, x_start:x_end] = entropy_ratio * 0.5 + 0.25
        
        return img


def run_wfc(grid_size=(10, 10), steps_per_frame=50):
    """Run and visualize the Wave Function Collapse algorithm."""
    tile_definitions_path = os.path.join(os.path.dirname(__file__), 'tiles', '2d', 'Tiles_small_1.json')
    
    with open(tile_definitions_path, 'r', encoding='utf-8') as file:
        tile_definitions = json.load(file)
    
    # Load all tiles with indices
    tiles = []
    for idx, tile_name in enumerate(tile_definitions['Tiles']):
        tiles.append(Tile(tile_name, tile_definitions['Tiles'][tile_name], idx))
    
    # Pre-compute adjacency rules
    rules = AdjacencyRules(tiles, tile_definitions['Connections'])
    grid = Grid(grid_size, tiles, rules)
    
    # Setup visualization
    fig, ax = plt.subplots(figsize=(8, 8))
    img_display = ax.imshow(grid.get_image())
    ax.set_title('Wave Function Collapse')
    ax.axis('off')
    
    def animate(_frame):
        if not grid.is_fully_collapsed():
            success = grid.run_steps(steps_per_frame)
            if not success and not grid.is_fully_collapsed():
                ax.set_title('Wave Function Collapse - Contradiction!')
        
        img_display.set_data(grid.get_image())
        total = grid.size[0] * grid.size[1]
        ax.set_title(f'Wave Function Collapse - {grid.collapsed_count}/{total} cells collapsed')
        return [img_display]
    
    total_cells = grid_size[0] * grid_size[1]
    num_frames = (total_cells // steps_per_frame) + 10
    _ = FuncAnimation(fig, animate, frames=num_frames, interval=1, blit=True)
    plt.show()


if __name__ == "__main__":
    run_wfc(grid_size=(64, 64), steps_per_frame=100)
