import pygame
from settings import *
from world.dungeon import Dungeon
from entities.player import Player

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
        Will later handle:
            - Enemy AI and pathfinding
            - Combat resolution
            - Game state changes (next floor, game over, etc.)
        """
        self.player.handle_input(self.dungeon)

    def draw(self):
        """
        Renders the current game state to the screen each frame.
        Drawing order matters — things drawn later appear on top.
        Currently draws the dungeon tiles then the player on top.
        Will later draw: enemies, HUD, etc.
        """
        self.screen.fill(BLACK)
        self.dungeon.draw(self.screen)
        self.player.draw(self.screen)
        pygame.display.flip()
