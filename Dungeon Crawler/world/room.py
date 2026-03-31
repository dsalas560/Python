from settings import *

class Room:
    """
    Represents a rectangular room in the dungeon.
    
    Rooms are carved out of the dungeon grid during procedural generation.
    Each room stores its position and size in grid coordinates, and provides
    helper methods used during dungeon generation and entity spawning.
    """

    def __init__(self, col, row, width, height):
        """
        Args:
            col:    Left edge column of the room in the grid
            row:    Top edge row of the room in the grid
            width:  How many tiles wide the room is
            height: How many tiles tall the room is
        """
        self.col = col          # Left edge
        self.row = row          # Top edge
        self.width = width
        self.height = height

        # Precompute edges for easy access during collision and generation
        self.left   = col
        self.right  = col + width
        self.top    = row
        self.bottom = row + height

    def center(self):
        """
        Returns the (col, row) grid coordinate of the room's center tile.
        Used to connect rooms with corridors and to spawn entities inside rooms.

        Returns:
            Tuple (center_col, center_row)
        """
        center_col = self.col + self.width // 2
        center_row = self.row + self.height // 2
        return (center_col, center_row)

    def intersects(self, other):
        """
        Checks if this room overlaps with another room.
        Used during generation to avoid placing rooms on top of each other.

        Args:
            other: Another Room object to check against

        Returns:
            True if the rooms overlap, False if they are separate
        """
        return (
            self.left   < other.right  and
            self.right  > other.left   and
            self.top    < other.bottom and
            self.bottom > other.top
        )
