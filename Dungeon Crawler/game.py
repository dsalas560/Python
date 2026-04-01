import pygame
from settings import *
from world.dungeon import Dungeon
from entities.player import Player
from entities.enemy import Enemy
from systems.combat import Combat

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
        self.game_over = False      # Tracks whether the player has died

        # Generate the dungeon
        self.dungeon = Dungeon()

        # Spawn the player at the center of the first generated room
        start_col, start_row = self.dungeon.rooms[0].center()
        self.player = Player(start_col, start_row)

        # Spawn one enemy in the center of each room except the first
        self.enemies = []
        for room in self.dungeon.rooms[1:]:
            col, row = room.center()
            self.enemies.append(Enemy(col, row))

        # Initialize the combat system
        self.combat = Combat()

        # Font for rendering the game over screen
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_small = pygame.font.SysFont(None, 36)

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
        Handles:
            - Window close button (QUIT)
            - Escape key to exit
            - R key to restart after game over
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Allow the player to restart after game over by pressing R
                if event.key == pygame.K_r and self.game_over:
                    self.__init__(self.screen, self.clock)   # Reset the entire game

    def update(self):
        """
        Updates all game logic each frame.
        Skips all updates if the game is in a game over state.
        Handles:
            - Player input and movement
            - Enemy AI movement via A* pathfinding
            - Combat resolution between player and enemies
            - Game over detection
        """
        if self.game_over:
            return  # Freeze the game state on game over screen

        # Handle player movement
        self.player.handle_input(self.dungeon)

        # Update every enemy
        for enemy in self.enemies:
            enemy.update(self.player, self.dungeon)

        # Resolve combat — removes dead enemies, damages player on contact
        self.enemies = Combat.check_player_enemy_collision(
            self.player, self.enemies, self.dungeon
        )

        # Check if the player has been reduced to 0 health
        if Combat.is_dead(self.player):
            self.game_over = True

    def _draw_game_over(self):
        """
        Renders the game over screen on top of the frozen game state.
        Shows a 'GAME OVER' message and instructions to restart or quit.
        Uses a semi-transparent dark overlay so the dungeon is still visible.
        """
        # Draw a semi-transparent dark overlay over the dungeon
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))    # Black with ~70% opacity
        self.screen.blit(overlay, (0, 0))

        # Render GAME OVER text centered on screen
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        restart_text   = self.font_small.render("Press R to Restart  |  ESC to Quit", True, WHITE)

        # Center the text horizontally and position vertically
        self.screen.blit(game_over_text, (
            SCREEN_WIDTH  // 2 - game_over_text.get_width()  // 2,
            SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2 - 20
        ))
        self.screen.blit(restart_text, (
            SCREEN_WIDTH  // 2 - restart_text.get_width()  // 2,
            SCREEN_HEIGHT // 2 + restart_text.get_height() // 2 + 10
        ))

    def draw(self):
        """
        Renders the current game state to the screen each frame.
        Drawing order: dungeon tiles → enemies → player → game over overlay (if active)
        """
        self.screen.fill(BLACK)
        self.dungeon.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.player.draw(self.screen)

        # Draw game over screen on top if the player is dead
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()
