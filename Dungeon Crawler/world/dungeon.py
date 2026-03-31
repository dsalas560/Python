import random
from world.tile import Tile
from world.room import Room
from settings import *

class Dungeon:
    """
    Manages the entire dungeon map as a 2D grid of Tile objects.

    Uses procedural generation to create a new dungeon layout every run.
    Generation algorithm:
        1. Fill the entire grid with WALL tiles
        2. Randomly place rectangular rooms, rejecting any that overlap
        3. Connect every room to the next with L-shaped corridors
        4. Store the list of rooms for use by the game (spawning, stairs, etc.)
    """

    COLS = SCREEN_WIDTH  // TILE_SIZE   # Total columns in the grid
    ROWS = SCREEN_HEIGHT // TILE_SIZE   # Total rows in the grid

    # Room generation settings
    MAX_ROOMS   = 15
    MIN_ROOM_SIZE = 4   # Minimum width/height of a room in tiles
    MAX_ROOM_SIZE = 10  # Maximum width/height of a room in tiles

    def __init__(self):
        """
        Initializes the dungeon by procedurally generating a new layout.
        """
        # Start with a completely solid grid of walls
        self.grid = self._fill_walls()

        # Generate rooms and corridors, store the room list
        self.rooms = self._generate()

    def _fill_walls(self):
        """
        Creates the initial grid filled entirely with WALL tiles.
        Rooms and corridors will be carved into this grid during generation.

        Returns:
            A 2D list (ROWS x COLS) of WALL Tile objects
        """
        grid = []
        for row in range(self.ROWS):
            tile_row = []
            for col in range(self.COLS):
                tile_row.append(Tile(col, row, WALL))
            grid.append(tile_row)
        return grid

    def _carve_room(self, room):
        """
        Carves a rectangular room into the grid by setting tiles to FLOOR.
        Leaves a 1-tile wall border around the room edges untouched.

        Args:
            room: A Room object defining the area to carve
        """
        for row in range(room.top + 1, room.bottom):
            for col in range(room.left + 1, room.right):
                self.grid[row][col].tile_type = FLOOR
                self.grid[row][col].color = GRAY

    def _carve_corridor(self, start, end):
        """
        Carves an L-shaped corridor between two (col, row) points.
        First moves horizontally then vertically (or vice versa, chosen randomly).
        This ensures every room is reachable from every other room.

        Args:
            start: (col, row) tuple — starting point (usually a room center)
            end:   (col, row) tuple — ending point (usually the next room's center)
        """
        col1, row1 = start
        col2, row2 = end

        # Randomly decide whether to go horizontal-first or vertical-first
        if random.random() < 0.5:
            self._carve_h_corridor(col1, col2, row1)   # Move horizontally
            self._carve_v_corridor(row1, row2, col2)   # Then vertically
        else:
            self._carve_v_corridor(row1, row2, col1)   # Move vertically
            self._carve_h_corridor(col1, col2, row2)   # Then horizontally

    def _carve_h_corridor(self, col1, col2, row):
        """
        Carves a horizontal corridor along a single row between two columns.

        Args:
            col1: Starting column
            col2: Ending column
            row:  The row to carve along
        """
        for col in range(min(col1, col2), max(col1, col2) + 1):
            self.grid[row][col].tile_type = FLOOR
            self.grid[row][col].color = GRAY

    def _carve_v_corridor(self, row1, row2, col):
        """
        Carves a vertical corridor along a single column between two rows.

        Args:
            row1: Starting row
            row2: Ending row
            col:  The column to carve along
        """
        for row in range(min(row1, row2), max(row1, row2) + 1):
            self.grid[row][col].tile_type = FLOOR
            self.grid[row][col].color = GRAY

    def _generate(self):
        """
        Main generation method. Attempts to place rooms randomly,
        rejecting any that overlap with existing rooms.
        After placing rooms, connects them all with corridors.

        Returns:
            A list of successfully placed Room objects
        """
        rooms = []

        for _ in range(self.MAX_ROOMS):
            # Pick a random size for this room
            width  = random.randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
            height = random.randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)

            # Pick a random position, keeping the room fully inside the grid
            col = random.randint(1, self.COLS - width  - 1)
            row = random.randint(1, self.ROWS - height - 1)

            new_room = Room(col, row, width, height)

            # Reject this room if it overlaps any existing room
            if any(new_room.intersects(existing) for existing in rooms):
                continue

            # Carve the room into the grid
            self._carve_room(new_room)

            # Connect to the previous room with a corridor
            if rooms:
                self._carve_corridor(rooms[-1].center(), new_room.center())

            rooms.append(new_room)

        return rooms

    def draw(self, screen):
        """
        Draws all tiles in the grid to the screen.
        Called every frame from Game.draw().

        Args:
            screen: The pygame surface to draw onto
        """
        for row in self.grid:
            for tile in row:
                tile.draw(screen)
