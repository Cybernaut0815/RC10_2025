"""
Wave Function Collapse (WFC) Algorithm - A constraint-based procedural generation technique.

How WFC works:
1. Start with a grid where each cell can be ANY tile (maximum entropy/uncertainty)
2. Pick the cell with the LEAST possibilities (lowest entropy) - this is the most constrained
3. COLLAPSE that cell: randomly pick one of its possible tiles
4. PROPAGATE: update neighbors - remove tiles that can't connect to the collapsed cell
5. Repeat until all cells are collapsed OR a contradiction occurs (no valid tiles left)

The algorithm is inspired by quantum mechanics - cells exist in superposition of all possible
states until "observed" (collapsed), at which point they influence their neighbors.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os, json, random



class Tile:
    """A single tile with connection rules on each edge."""
    def __init__(self, name, definition, index):
        self.name, self.index = name, index
        # Each edge has a "socket" type that determines what can connect to it
        c = definition['connections']
        self.edges = {'top': c['top'], 'right': c['right'], 'bottom': c['bottom'], 'left': c['left']}
        self.image = plt.imread(os.path.join(os.path.dirname(__file__), 'tiles', '2d', f'{name}.png'))



def build_adjacency_rules(tiles, connections):
    """
    Pre-compute which tiles can be neighbors in each direction.
    
    Returns a dict: adjacency[direction][tile_index] = set of valid neighbor indices
    
    Two tiles can be adjacent if their touching edges have compatible "sockets".
    The connections dict defines which socket types can connect to each other.
    """
    opposite = {'top': 'bottom', 'bottom': 'top', 'left': 'right', 'right': 'left'}
    adjacency = {d: [set() for _ in tiles] for d in opposite}
    
    for direction in adjacency:
        for tile in tiles:
            # Find all tiles whose opposite edge is compatible with this tile's edge
            valid_sockets = connections.get(tile.edges[direction], [])
            for other in tiles:
                if other.edges[opposite[direction]] in valid_sockets:
                    adjacency[direction][tile.index].add(other.index)
    return adjacency



class Grid:
    """
    The WFC grid - each cell tracks which tiles are still possible.
    
    Attributes:
        possible: 2D list of sets - each set contains indices of tiles still valid for that cell
        collapsed: 2D list tracking which cells have been finalized
    """
    # Neighbor offsets: (row_delta, col_delta, direction_to_neighbor)
    DIRECTIONS = [(-1, 0, 'top'), (1, 0, 'bottom'), (0, -1, 'left'), (0, 1, 'right')]



    def __init__(self, size, tiles, adjacency):
        self.rows, self.cols = size
        self.tiles, self.adjacency = tiles, adjacency
        self.tile_by_name = {t.name: t for t in tiles}  # Lookup table for predefined tiles
        all_indices = set(range(len(tiles)))
        # Every cell starts with ALL tiles possible (maximum entropy)
        self.possible = [[all_indices.copy() for _ in range(self.cols)] for _ in range(self.rows)]
        self.collapsed = [[False] * self.cols for _ in range(self.rows)]
        self.result = [[None] * self.cols for _ in range(self.rows)]  # Final tile assignments


    def set_tile(self, r, c, tile_name):
        """
        Pre-place a specific tile at position (r, c) before running WFC.
        
        This "seeds" the grid with fixed tiles that won't change. Useful for:
        - Placing specific features (doors, windows, landmarks)
        - Creating boundaries or borders
        - Guiding the generation toward desired patterns
        
        Returns False if the tile doesn't exist or position is invalid.
        """
        if tile_name not in self.tile_by_name:
            print(f"Warning: Tile '{tile_name}' not found, skipping.")
            return False
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            print(f"Warning: Position ({r}, {c}) out of bounds, skipping.")
            return False
        
        tile = self.tile_by_name[tile_name]
        self.possible[r][c] = {tile.index}
        self.collapsed[r][c] = True
        self.result[r][c] = tile
        return True


    def set_tiles(self, predefined):
        """
        Place multiple predefined tiles and propagate all constraints.
        
        Args:
            predefined: List of (row, col, tile_name) tuples specifying fixed tiles
        
        Returns False if propagation fails (contradiction from incompatible seeds).
        """
        # First, place all tiles without propagating
        placed = []
        for r, c, tile_name in predefined:
            if self.set_tile(r, c, tile_name):
                placed.append((r, c))
        
        # Then propagate constraints from all placed tiles
        for r, c in placed:
            if not self.propagate(r, c):
                print(f"Warning: Contradiction when propagating from ({r}, {c})")
                return False
        return True


    # Core logic
    def get_min_entropy_cell(self):
        """Find uncollapsed cell with fewest possibilities (most constrained)."""
        best, best_entropy = [], float('inf')
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.collapsed[r][c]:
                    entropy = len(self.possible[r][c])
                    if entropy < best_entropy:
                        best, best_entropy = [(r, c)], entropy
                    elif entropy == best_entropy:
                        best.append((r, c))
        return random.choice(best) if best else None



    def collapse(self, r, c):
        """Collapse a cell: pick one random tile from its possibilities."""
        if not self.possible[r][c]:
            return False  # Contradiction - no valid tiles!
        choice = random.choice(list(self.possible[r][c]))
        self.possible[r][c] = {choice}
        self.collapsed[r][c] = True
        self.result[r][c] = self.tiles[choice]
        return True



    def propagate(self, start_r, start_c):
        """
        Propagate constraints outward from a collapsed cell using a stack.
        
        When a cell's possibilities change, its neighbors might need updating too.
        This continues until no more changes occur or a contradiction is found.
        """
        stack = [(start_r, start_c)]
        
        while stack:
            r, c = stack.pop()
            for dr, dc, direction in self.DIRECTIONS:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < self.rows and 0 <= nc < self.cols) or self.collapsed[nr][nc]:
                    continue
                
                # Compute valid tiles for neighbor based on current cell's possibilities
                valid = set()
                for idx in self.possible[r][c]:
                    valid.update(self.adjacency[direction][idx])
                
                # Constrain neighbor to only tiles compatible with current cell
                old_count = len(self.possible[nr][nc])
                self.possible[nr][nc] &= valid
                
                if not self.possible[nr][nc]:
                    return False  # Contradiction!
                if len(self.possible[nr][nc]) < old_count:
                    stack.append((nr, nc))  # Changed, so propagate further
        return True



    def step(self):
        """One WFC iteration: find lowest entropy cell, collapse it, propagate."""
        cell = self.get_min_entropy_cell()
        if cell is None:
            return False
        r, c = cell
        return self.collapse(r, c) and self.propagate(r, c)


    
    def is_complete(self):
        return all(self.collapsed[r][c] for r in range(self.rows) for c in range(self.cols))


    
    def get_image(self):
        """Render current state: collapsed cells show tiles, others show entropy as grayscale."""
        tile_size = self.tiles[0].image.shape[0]
        channels = self.tiles[0].image.shape[2] if len(self.tiles[0].image.shape) > 2 else 3
        img = np.ones((self.rows * tile_size, self.cols * tile_size, channels), dtype=np.float32) * 0.5
        
        for r in range(self.rows):
            for c in range(self.cols):
                y, x = r * tile_size, c * tile_size
                if self.collapsed[r][c] and self.result[r][c]:
                    img[y:y+tile_size, x:x+tile_size] = self.result[r][c].image[:, :, :channels]
                else:
                    # Darker = fewer possibilities (lower entropy) = more constrained
                    brightness = len(self.possible[r][c]) / len(self.tiles) * 0.5 + 0.25
                    img[y:y+tile_size, x:x+tile_size] = brightness
        return img



def run_wfc(grid_size=(10, 10), steps_per_frame=50, tiles_file='Tiles.json', predefined=None):
    """
    Run and visualize Wave Function Collapse.
    
    Args:
        grid_size: (rows, cols) tuple for grid dimensions
        steps_per_frame: How many cells to collapse per animation frame
        tiles_file: JSON file with tile definitions and connection rules
        predefined: List of (row, col, tile_name) tuples for pre-placed tiles
                   These tiles are fixed before WFC runs and guide the generation.
                   Example: [(0, 0, 'Tile1_A'), (5, 5, 'Tile2_B')]
    """
    # Load tile definitions
    path = os.path.join(os.path.dirname(__file__), 'tiles', '2d', tiles_file)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tiles = [Tile(name, data['Tiles'][name], i) for i, name in enumerate(data['Tiles'])]
    adjacency = build_adjacency_rules(tiles, data['Connections'])
    grid = Grid(grid_size, tiles, adjacency)
    
    # Place predefined tiles before running WFC
    if predefined:
        if not grid.set_tiles(predefined):
            print("Warning: Some predefined tiles caused contradictions!")
    
    # Setup visualization
    fig, ax = plt.subplots(figsize=(8, 8))
    img_display = ax.imshow(grid.get_image())
    ax.axis('off')
    
    def animate(_):
        for _ in range(steps_per_frame):
            if grid.is_complete():
                break
            if not grid.step():
                ax.set_title('WFC - Contradiction! (unsolvable state)')
                break
        img_display.set_data(grid.get_image())
        collapsed = sum(sum(row) for row in grid.collapsed)
        ax.set_title(f'Wave Function Collapse - {collapsed}/{grid.rows * grid.cols} cells')
        return [img_display]
    
    _ = FuncAnimation(fig, animate, frames=grid.rows * grid.cols // steps_per_frame + 10, interval=1, blit=True)
    plt.show()
    
    return grid



if __name__ == "__main__":
    
    seeds = []
    
    size = 32
    use_boundary = True
    
    if use_boundary:
        for i in range(size):
            seeds.append((i, 0, 'Tile0_O'))
            seeds.append((i, size - 1, 'Tile0_O'))
            seeds.append((0, i, 'Tile0_O'))
            seeds.append((size - 1, i, 'Tile0_O'))
    
        run_wfc(grid_size=(size, size), steps_per_frame=100, tiles_file='Tiles_restraint_2.json', predefined=seeds)
    else:
        run_wfc(grid_size=(size, size), steps_per_frame=100, tiles_file='Tiles.json', predefined=seeds)
