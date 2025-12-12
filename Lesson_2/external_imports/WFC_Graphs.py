import matplotlib.pyplot as plt
import networkx as nx

def create_connectivity_graph(grid, exclude_connections=None, exclude_tiles=None, search_connections=None):
    """
    Create connectivity graphs for tiles in a WFC grid.
    
    Args:
        grid: Grid object from WFC algorithm with collapsed tiles in grid.result
        exclude_connections: List of connection types to exclude (e.g., ['D'])
        exclude_tiles: List of tile names to exclude (e.g., ['Tile0_O'])
        search_connections: List of connection types to use for island connections
    
    Returns:
        tuple: (tile_graph, island_graph) where:
            - tile_graph: Graph with tiles as nodes, connected via non-excluded connections
            - island_graph: Graph with connected components (islands) as nodes, 
                          connected via search_connections (None if only one island)
    """
    exclude_connections = exclude_connections or []
    exclude_tiles = exclude_tiles or []
    search_connections = search_connections or []
    
    exclude_connections_set = set(exclude_connections)
    exclude_tiles_set = set(exclude_tiles)
    opposite = {'top': 'bottom', 'bottom': 'top', 'left': 'right', 'right': 'left'}
    directions = [(-1, 0, 'top'), (1, 0, 'bottom'), (0, -1, 'left'), (0, 1, 'right')]
    
    # Create tile graph
    tile_graph = nx.Graph()
    for r in range(grid.rows):
        for c in range(grid.cols):
            tile = grid.result[r][c]
            if tile and tile.name not in exclude_tiles_set:
                tile_graph.add_node((r, c), tile_name=tile.name)
    
    # Add edges between neighboring tiles
    for r in range(grid.rows):
        for c in range(grid.cols):
            tile1 = grid.result[r][c]
            if not tile1 or tile1.name in exclude_tiles_set:
                continue
            
            for dr, dc, direction in directions:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < grid.rows and 0 <= nc < grid.cols):
                    continue
                
                tile2 = grid.result[nr][nc]
                if not tile2 or tile2.name in exclude_tiles_set:
                    continue
                
                conn_type = tile1.edges[direction]
                if conn_type in exclude_connections_set:
                    continue
                
                opp_direction = opposite[direction]
                if (tile2.index in grid.adjacency[direction][tile1.index] and
                    tile2.edges[opp_direction] not in exclude_connections_set):
                    tile_graph.add_edge((r, c), (nr, nc), connection_type=conn_type)
    
    # Find islands and create island graph if needed
    islands = list(nx.connected_components(tile_graph))
    island_graph = None
    
    if len(islands) > 1 and search_connections:
        island_graph = nx.Graph()
        search_connections_set = set(search_connections)
        
        for i, island in enumerate(islands):
            island_graph.add_node(i, tiles=list(island))
        
        for i in range(len(islands)):
            for j in range(i + 1, len(islands)):
                for r1, c1 in islands[i]:
                    tile1 = grid.result[r1][c1]
                    if not tile1:
                        continue
                    
                    for dr, dc, direction in directions:
                        r2, c2 = r1 + dr, c1 + dc
                        if (r2, c2) not in islands[j]:
                            continue
                        
                        tile2 = grid.result[r2][c2]
                        if (tile2 and
                            tile1.edges[direction] in search_connections_set and
                            tile2.edges[opposite[direction]] in search_connections_set and
                            tile2.index in grid.adjacency[direction][tile1.index]):
                            island_graph.add_edge(i, j)
                            break
                    else:
                        continue
                    break
    
    return tile_graph, island_graph


def visualize_connectivity_graphs(tile_graph, island_graph=None, grid=None, figsize=(12, 12)):
    """
    Visualize the WFC grid with tile connectivity graph and island graph overlaid.
    
    Args:
        tile_graph: Graph with tiles as nodes
        island_graph: Optional graph with islands as nodes
        grid: Grid object for displaying WFC tiles
        figsize: Figure size tuple
    """
    if grid is None:
        raise ValueError("grid parameter is required for visualization")
    
    _, ax = plt.subplots(figsize=figsize)
    img = grid.get_image()
    ax.imshow(img, aspect='equal', origin='upper')
    
    tile_size = img.shape[0] // grid.rows if grid.rows > 0 else img.shape[1] // grid.cols if grid.cols > 0 else 1
    
    def get_coords(r, c):
        return c * tile_size + tile_size / 2, r * tile_size + tile_size / 2
    
    # Draw tile graph
    for (r1, c1), (r2, c2) in tile_graph.edges():
        x1, y1 = get_coords(r1, c1)
        x2, y2 = get_coords(r2, c2)
        ax.plot([x1, x2], [y1, y2], 'b-', alpha=0.5, linewidth=2, zorder=1)
    
    for r, c in tile_graph.nodes():
        x, y = get_coords(r, c)
        ax.plot(x, y, 'bo', markersize=6, alpha=0.8, zorder=2,
               markeredgecolor='darkblue', markeredgewidth=1)
    
    # Draw island graph
    if island_graph and island_graph.nodes():
        island_pos = {}
        for island_id in island_graph.nodes():
            tiles = island_graph.nodes[island_id]['tiles']
            if tiles:
                avg_r = sum(r for r, c in tiles) / len(tiles)
                avg_c = sum(c for r, c in tiles) / len(tiles)
                island_pos[island_id] = get_coords(avg_r, avg_c)
        
        for island1_id, island2_id in island_graph.edges():
            if island1_id in island_pos and island2_id in island_pos:
                ax.plot([island_pos[island1_id][0], island_pos[island2_id][0]],
                        [island_pos[island1_id][1], island_pos[island2_id][1]],
                        'r-', alpha=0.9, linewidth=5, zorder=3)
        
        for island_id, (x, y) in island_pos.items():
            ax.plot(x, y, 'ro', markersize=25, alpha=0.9, zorder=4,
                   markeredgecolor='darkred', markeredgewidth=2)
            ax.text(x, y, str(island_id), ha='center', va='center',
                   fontsize=14, fontweight='bold', color='white', zorder=5)
    
    ax.set_xlim(0, img.shape[1])
    ax.set_ylim(img.shape[0], 0)
    ax.set_aspect('equal')
    ax.axis('off')
    
    title = 'WFC Grid with Connectivity Graphs'
    if island_graph:
        title += f' ({len(island_graph.nodes())} islands, {len(island_graph.edges())} connections)'
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()
