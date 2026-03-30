import pygame
from settings import *
from world.dungeon import Dungeon

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
        self.running = True  # Controls the game loop — set to False to quit

        # Initialize the dungeon map
        self.dungeon = Dungeon()

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
            self.clock.tick(FPS)        # Cap the loop to FPS (defined in settings.py)
            self.handle_events()         # Step 1: Process keyboard/mouse input
            self.update()                # Step 2: Update positions, logic, AI
            self.draw()                  # Step 3: Render everything to the screen

    def handle_events(self):
        """
        Processes all pygame events in the event queue each frame.
        Currently handles:
            - Window close button (QUIT)
            - Escape key to exit the game
        More input handling (player movement, etc.) will be added here later.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:           # User clicked the X button
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:    # Escape key exits cleanly
                    self.running = False

    def update(self):
        """
        Updates all game logic each frame.
        Currently empty — will later handle:
            - Player movement and collision
            - Enemy AI and pathfinding
            - Combat resolution
            - Game state changes (next floor, game over, etc.)
        """
        pass

    def draw(self):
        """
        Renders the current game state to the screen each frame.
        Drawing order matters — things drawn later appear on top.
        Currently draws the dungeon tile grid.
        Will later draw: player, enemies, HUD, etc.
        """
        self.screen.fill(BLACK)         # Clear last frame
        self.dungeon.draw(self.screen)  # Draw all dungeon tiles
        pygame.display.flip()           # Push the finished frame to the display
