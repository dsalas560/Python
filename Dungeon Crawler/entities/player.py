import pygame
from entities.entity import Entity
from settings import *

class Player(Entity):
    """
    The player-controlled character in the dungeon.
    Inherits position, movement, and drawing from Entity.

    Extends Entity with:
        - Keyboard input handling (WASD or arrow keys)
        - Health and attack stats
        - A move cooldown so the player doesn't zip across the dungeon instantly
    """

    def __init__(self, grid_x, grid_y):
        """
        Args:
            grid_x: Starting column in the dungeon grid
            grid_y: Starting row in the dungeon grid
        """
        # Call Entity's __init__ with the player's color (green)
        super().__init__(grid_x, grid_y, GREEN)

        # Player stats
        self.max_health = 100
        self.health = 100
        self.attack = 10

        # Movement cooldown — limits how fast the player can move
        # Without this, holding a key moves the player dozens of tiles per second
        self.move_delay = 150       # Milliseconds between moves
        self.last_move_time = 0     # Timestamp of the last move

    def handle_input(self, dungeon):
        """
        Reads keyboard input and moves the player if the move cooldown has elapsed.
        Supports both WASD and arrow keys.
        Movement is grid-based — one tile per key press.

        Args:
            dungeon: The Dungeon object passed to Entity.move() for collision checking
        """
        # Get the current time in milliseconds
        now = pygame.time.get_ticks()

        # Only allow movement if enough time has passed since the last move
        if now - self.last_move_time < self.move_delay:
            return

        # Read which keys are currently held down
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0   # Direction of movement this frame

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1     # Move up (decrease row)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1      # Move down (increase row)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1     # Move left (decrease column)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1      # Move right (increase column)

        # If a direction was chosen, attempt the move
        if dx != 0 or dy != 0:
            self.move(dx, dy, dungeon)
            self.last_move_time = now   # Reset the cooldown timer

    def draw(self, screen):
        """
        Draws the player on the screen.
        Calls Entity.draw() for the base rectangle, then adds a small
        center dot to make the player visually distinct from enemies.

        Args:
            screen: The pygame surface to draw onto
        """
        # Draw the base entity rectangle (green square)
        super().draw(screen)

        # Draw a small white dot in the center to distinguish the player
        center_x = self.x + TILE_SIZE // 2
        center_y = self.y + TILE_SIZE // 2
        pygame.draw.circle(screen, WHITE, (center_x, center_y), 4)
