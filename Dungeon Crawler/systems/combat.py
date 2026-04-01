from settings import *

class Combat:
    """
    Handles all combat interactions between entities in the dungeon.
    
    Combat is tile-based — it triggers when two entities attempt to
    occupy the same tile. Instead of passing through each other,
    the attacker deals damage to the defender.

    This class is intentionally stateless (no __init__ needed) —
    it acts as a collection of combat utility functions that are
    called by the Game object each frame.
    """

    @staticmethod
    def attack(attacker, defender):
        """
        Resolves a single attack from one entity to another.
        Subtracts the attacker's attack stat from the defender's health.
        Health is clamped to 0 as a minimum (no negative health).

        Args:
            attacker: The entity dealing damage (Player or Enemy)
            defender: The entity receiving damage (Player or Enemy)
        """
        defender.health -= attacker.attack
        defender.health = max(0, defender.health)   # Clamp health to 0 minimum

    @staticmethod
    def is_dead(entity):
        """
        Checks if an entity has been reduced to zero health.

        Args:
            entity: The entity to check

        Returns:
            True if the entity's health is 0 or below, False otherwise
        """
        return entity.health <= 0

    @staticmethod
    def check_player_enemy_collision(player, enemies, dungeon):
        """
        Checks if the player is on the same tile as any enemy.
        
        If the player and an enemy share a tile:
            - The player attacks the enemy
            - The enemy attacks the player back
        
        Dead enemies are removed from the list after all collisions are resolved.

        Args:
            player:  The Player object
            enemies: List of Enemy objects currently in the dungeon
            dungeon: The Dungeon object (reserved for future use e.g. traps)

        Returns:
            The updated list of enemies with dead enemies removed
        """
        for enemy in enemies:
            # Check if the player and enemy are on the same tile
            if player.grid_x == enemy.grid_x and player.grid_y == enemy.grid_y:
                Combat.attack(player, enemy)    # Player hits enemy
                Combat.attack(enemy, player)    # Enemy hits player back

        # Remove any enemies that have been reduced to 0 health
        enemies = [e for e in enemies if not Combat.is_dead(e)]

        return enemies
