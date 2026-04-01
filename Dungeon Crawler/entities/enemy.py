import pygame
from entities.entity import Entity
from systems.pathfinding import AStar
from settings import *

class Enemy(Entity):
    """
    An enemy that chases the player using A* pathfinding.
    Inherits position, movement, and drawing from Entity.

    Extends Entity with:
        - A* pathfinding to navigate toward the player each turn
        - Health and attack stats
        - A move cooldown so enemies don't move too fast
        - Detection range — enemies only chase the player if close enough
    """

    def __init__(self, grid_x, grid_y):
        """
        Args:
            grid_x: Starting column in the dungeon grid
            grid_y: Starting row in the dungeon grid
        """
        # Call Entity's __init__ with the enemy's color (red)
        super().__init__(grid_x, grid_y, RED)

        # Enemy stats
        self.max_health = 40
        self.health = 40
        self.attack = 8

        # Movement cooldown — enemies move slower than the player
        self.move_delay = 500       # Milliseconds between moves (0.5 seconds)
        self.last_move_time = 0

        # Detection range in tiles — enemy only chases if player is within this range
        self.detection_range = 8

    def update(self, player, dungeon):
        """
        Updates the enemy each frame.
        If the player is within detection range, uses A* to find a path
        toward the player and moves one step along it.
        Does nothing if the player is out of range or the cooldown hasn't elapsed.

        Args:
            player:  The Player object to chase
            dungeon: The Dungeon object used for pathfinding and collision
        """
        now = pygame.time.get_ticks()

        # Only move if the cooldown has elapsed
        if now - self.last_move_time < self.move_delay:
            return

        # Calculate the distance to the player in tiles (Manhattan distance)
        distance = abs(self.grid_x - player.grid_x) + abs(self.grid_y - player.grid_y)

        # Only chase if the player is within detection range
        if distance > self.detection_range:
            return

        # Use A* to find the path from this enemy to the player
        pathfinder = AStar(dungeon)
        path = pathfinder.find_path(
            (self.grid_x, self.grid_y),     # Enemy's current position
            (player.grid_x, player.grid_y)  # Player's current position
        )

        # If a path exists, move one step along it
        if path:
            next_col, next_row = path[0]    # First step in the path
            dx = next_col - self.grid_x
            dy = next_row - self.grid_y
            self.move(dx, dy, dungeon)
            self.last_move_time = now

    def draw(self, screen):
        """
        Draws the enemy on the screen.
        Calls Entity.draw() for the base rectangle, then adds a small
        center dot to make enemies visually distinct from floor tiles.

        Args:
            screen: The pygame surface to draw onto
        """
        # Draw the base entity rectangle (red square)
        super().draw(screen)

        # Draw a small dark dot in the center
        center_x = self.x + TILE_SIZE // 2
        center_y = self.y + TILE_SIZE // 2
        pygame.draw.circle(screen, BLACK, (center_x, center_y), 4)
