import pygame
from settings import *

class Tile:
    """
    Represents a single tile in the dungeon grid.
    Every cell in the dungeon map is a Tile object — either a floor or a wall.
    
    Tiles are the building blocks of the dungeon. They store:
        - Their position in the grid (grid_x, grid_y)
        - Their pixel position on screen (derived from grid position * TILE_SIZE)
        - Their type (FLOOR or WALL, defined in settings.py)
        - Their color for rendering
    """

    def __init__(self, grid_x, grid_y, tile_type):
        """
        Args:
            grid_x:     Column index in the dungeon grid
            grid_y:     Row index in the dungeon grid
            tile_type:  FLOOR or WALL (constants from settings.py)
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.tile_type = tile_type

        # Convert grid coordinates to pixel coordinates for drawing
        self.x = grid_x * TILE_SIZE
        self.y = grid_y * TILE_SIZE

        # Create a rectangle representing this tile's position and size on screen
        self.rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)

        # Assign color based on tile type
        self.color = GRAY if tile_type == FLOOR else BLACK

    def draw(self, screen):
        """
        Draws the tile onto the screen as a filled rectangle.
        Walls are drawn with a dark border to visually separate them.

        Args:
            screen: The pygame surface to draw onto
        """
        pygame.draw.rect(screen, self.color, self.rect)

        # Draw a subtle border on wall tiles to give depth
        if self.tile_type == WALL:
            pygame.draw.rect(screen, BROWN, self.rect, 2)  # 2px border
