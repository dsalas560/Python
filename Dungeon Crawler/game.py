import pygame
from settings import *
from world.dungeon import Dungeon
from entities.player import Player
from entities.enemy import Enemy

class Game:
    def __init__(self, screen, clock):
        """
        The main game object that controls the core game loop.
        All major systems (rendering, input, updating) flow through here.

        Args:
            screen: The pygame display surface we draw everything onto
            clock:  The pygame clock used to control FPS and delta time
        """
        self.screen = screen
        self.clock = clock
        self.running = True

        # Generate the dungeon
        self.dungeon = Dungeon()

        # Spawn the player at the center of the first generated room
        start_col, start_row = self.dungeon.rooms[0].center()
        self.player = Player(start_col, start_row)

        # Spawn one enemy in the center of each room except the first (player's room)
        self.enemies = []
        for room in self.dungeon.rooms[1:]:
            col, row = room.center()
            self.enemies.append(Enemy(col, row))

    def run(self):
        """
        The core game loop. Runs continuously until self.running is False.
        Each iteration represents one frame and follows the standard loop order:
            1. Cap the framerate
            2. Handle input events
            3. Update game state
            4. Draw everything to the screen
        """
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        """
        Processes all pygame events in the event queue each frame.
        Currently handles:
            - Window close button (QUIT)
            - Escape key to exit the game
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """
        Updates all game logic each frame.
        Currently handles:
            - Player input and movement
            - Enemy AI movement via A* pathfinding
        Will later handle:
            - Combat resolution
            - Game state changes (next floor, game over, etc.)
        """
        self.player.handle_input(self.dungeon)

        # Update every enemy — each one will chase the player if in range
        for enemy in self.enemies:
            enemy.update(self.player, self.dungeon)

    def draw(self):
        """
        Renders the current game state to the screen each frame.
        Drawing order matters — things drawn later appear on top.
        Order: dungeon tiles → enemies → player (player always on top)
        """
        self.screen.fill(BLACK)
        self.dungeon.draw(self.screen)

        # Draw all enemies before the player so player renders on top
        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.player.draw(self.screen)
        pygame.display.flip()
