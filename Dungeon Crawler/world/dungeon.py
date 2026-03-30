from world.tile import Tile
from settings import *

class Dungeon:
    """
    Manages the entire dungeon map as a 2D grid of Tile objects.
    
    The dungeon is represented as a 2D list (grid) where each cell
    is a Tile that is either a FLOOR or a WALL.
    
    Currently uses a hardcoded test map — procedural generation will
    replace this in a later step.
    """

    # Number of tiles that fit on screen horizontally and vertically
    COLS = SCREEN_WIDTH // TILE_SIZE    # e.g. 800 / 32 = 25 columns
    ROWS = SCREEN_HEIGHT // TILE_SIZE   # e.g. 600 / 32 = 18 rows

    def __init__(self):
        """
        Initializes the dungeon by building the tile grid.
        """
        self.grid = self._build_map()

    def _build_map(self):
        """
        Builds a 2D grid of Tile objects from a hardcoded map layout.
        
        The map is defined as a 2D list of integers:
            1 = WALL
            0 = FLOOR
        
        Returns:
            A 2D list (rows x cols) of Tile objects
        """
        # Hardcoded test map — 1 is wall, 0 is floor
        # Outer ring is all walls, interior has open floor space
        layout = []
        for row in range(self.ROWS):
            layout_row = []
            for col in range(self.COLS):
                # Make the border walls, everything inside is floor
                if row == 0 or row == self.ROWS - 1 or col == 0 or col == self.COLS - 1:
                    layout_row.append(WALL)
                else:
                    layout_row.append(FLOOR)
            layout.append(layout_row)

        # Build the actual Tile objects from the layout
        grid = []
        for row in range(self.ROWS):
            tile_row = []
            for col in range(self.COLS):
                tile = Tile(col, row, layout[row][col])
                tile_row.append(tile)
            grid.append(tile_row)

        return grid

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
