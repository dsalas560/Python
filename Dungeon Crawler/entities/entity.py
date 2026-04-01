import pygame
from settings import *

class Entity:
    """
    Base class for all living things in the dungeon (player, enemies, etc.)
    
    Contains the shared attributes and behavior that every entity has:
        - A position in the dungeon grid
        - A pixel position on screen (derived from grid position)
        - A color for rendering
        - A rectangle for drawing and collision detection
        - Health and attack stats (set by subclasses)
    """

    def __init__(self, grid_x, grid_y, color):
        """
        Args:
            grid_x: Starting column in the dungeon grid
            grid_y: Starting row in the dungeon grid
            color:  RGB tuple used to draw this entity
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.color = color

        # Pixel position on screen — derived from grid position
        self.x = grid_x * TILE_SIZE
        self.y = grid_y * TILE_SIZE

        # Rectangle used for drawing and collision detection
        # Slightly smaller than a full tile (4px padding) so movement feels clean
        self.rect = pygame.Rect(self.x + 4, self.y + 4, TILE_SIZE - 8, TILE_SIZE - 8)

        # Stats — default values, overridden by Player and Enemy subclasses
        self.max_health = 100
        self.health = 100
        self.attack = 0

    def move(self, dx, dy, dungeon):
        """
        Attempts to move the entity by (dx, dy) grid steps.
        Movement is grid-based — entities snap from tile to tile.

        Checks for wall collisions before moving:
            - If the destination tile is a WALL, movement is blocked
            - If the destination tile is a FLOOR, movement is allowed

        Args:
            dx:      Change in column (-1 left, +1 right, 0 no horizontal move)
            dy:      Change in row (-1 up, +1 down, 0 no vertical move)
            dungeon: The Dungeon object used to check tile types at destination
        """
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        # Look up the tile at the destination position
        destination_tile = dungeon.grid[new_y][new_x]

        # Only move if the destination is a floor tile (not a wall)
        if destination_tile.tile_type == FLOOR:
            self.grid_x = new_x
            self.grid_y = new_y

            # Update pixel position to match new grid position
            self.x = self.grid_x * TILE_SIZE
            self.y = self.grid_y * TILE_SIZE

            # Update the rect so drawing and collision stay in sync
            self.rect.topleft = (self.x + 4, self.y + 4)

    def draw(self, screen):
        """
        Draws the entity as a filled rectangle on the screen.

        Args:
            screen: The pygame surface to draw onto
        """
        pygame.draw.rect(screen, self.color, self.rect)
