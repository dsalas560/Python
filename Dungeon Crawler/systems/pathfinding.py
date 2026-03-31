import heapq
from settings import *

class AStar:
    """
    Implementation of the A* pathfinding algorithm.
    
    A* finds the shortest path between two points on a grid by combining:
        - g_cost: The actual distance traveled from the start node
        - h_cost: A heuristic estimate of the distance to the goal (Manhattan distance)
        - f_cost: g_cost + h_cost — the value used to prioritize which node to explore next
    
    The algorithm always explores the node with the lowest f_cost first,
    guaranteeing the shortest path is found efficiently.
    
    Used by enemies to navigate toward the player each turn.
    """

    def __init__(self, dungeon):
        """
        Args:
            dungeon: The Dungeon object containing the grid of tiles
        """
        self.dungeon = dungeon

    def heuristic(self, a, b):
        """
        Estimates the distance between two grid points using Manhattan distance.
        Manhattan distance counts steps horizontally + vertically (no diagonals).
        This is the standard heuristic for grid-based pathfinding.

        Args:
            a: (col, row) tuple — current node
            b: (col, row) tuple — goal node

        Returns:
            Integer estimate of the distance between a and b
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, node):
        """
        Returns all valid neighboring tiles of a given node.
        Only returns FLOOR tiles — enemies cannot walk through walls.
        Only checks the 4 cardinal directions (up, down, left, right).

        Args:
            node: (col, row) tuple of the current tile

        Returns:
            List of (col, row) tuples representing walkable neighbors
        """
        col, row = node
        neighbors = []

        # Check all 4 cardinal directions
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, Down, Left, Right

        for dc, dr in directions:
            new_col = col + dc
            new_row = row + dr

            # Make sure the neighbor is inside the grid bounds
            if 0 <= new_row < len(self.dungeon.grid) and 0 <= new_col < len(self.dungeon.grid[0]):
                # Only include walkable (FLOOR) tiles
                if self.dungeon.grid[new_row][new_col].tile_type == FLOOR:
                    neighbors.append((new_col, new_row))

        return neighbors

    def find_path(self, start, goal):
        """
        Finds the shortest path from start to goal using A*.
        
        Algorithm steps:
            1. Add the start node to the open set (nodes to explore)
            2. Pop the node with the lowest f_cost from the open set
            3. If it's the goal, reconstruct and return the path
            4. Otherwise add its neighbors to the open set with updated costs
            5. Repeat until the goal is found or no path exists

        Args:
            start: (col, row) tuple — starting position (enemy location)
            goal:  (col, row) tuple — target position (player location)

        Returns:
            A list of (col, row) tuples representing the path from start to goal,
            not including the start position. Returns empty list if no path found.
        """
        # Open set implemented as a min-heap for efficient lowest f_cost lookup
        # Each entry: (f_cost, node)
        open_set = []
        heapq.heappush(open_set, (0, start))

        # Tracks which node each node was reached from (for path reconstruction)
        came_from = {}

        # g_cost[node] = actual cost to reach this node from start
        g_cost = {start: 0}

        # f_cost[node] = g_cost + heuristic estimate to goal
        f_cost = {start: self.heuristic(start, goal)}

        while open_set:
            # Get the node with the lowest f_cost
            _, current = heapq.heappop(open_set)

            # If we reached the goal, reconstruct the path and return it
            if current == goal:
                return self._reconstruct_path(came_from, current)

            # Explore each walkable neighbor
            for neighbor in self.get_neighbors(current):
                # Moving one tile always costs 1
                tentative_g = g_cost[current] + 1

                # If this path to neighbor is cheaper than any previously found
                if tentative_g < g_cost.get(neighbor, float('inf')):
                    # Record this as the best path to neighbor
                    came_from[neighbor] = current
                    g_cost[neighbor] = tentative_g
                    f_cost[neighbor] = tentative_g + self.heuristic(neighbor, goal)

                    # Add neighbor to open set for future exploration
                    heapq.heappush(open_set, (f_cost[neighbor], neighbor))

        # No path found (enemy is completely blocked)
        return []

    def _reconstruct_path(self, came_from, current):
        """
        Traces back through the came_from map to build the full path
        from start to goal once the goal node has been reached.

        Args:
            came_from: Dictionary mapping each node to the node it was reached from
            current:   The goal node to trace back from

        Returns:
            List of (col, row) tuples from start to goal (excluding start)
        """
        path = []

        # Walk backwards from goal to start using came_from
        while current in came_from:
            path.append(current)
            current = came_from[current]

        # Reverse so the path goes from start to goal
        path.reverse()
        return path
