from typing import Tuple
from utils import START_POSITIONS, WALLS_PER_PLAYER, BOARD_SIZE

class Player:
    def __init__(self, player_id: str):
        """
        Initializes a player.
        player_id: "P1" or "P2"
        """
        self.player_id = player_id
        self.pos: Tuple[int, int] = START_POSITIONS[player_id]
        # Target row: bottom for P1, top for P2
        self.target_row = BOARD_SIZE - 1 if player_id == "P1" else 0
        self.walls_remaining = WALLS_PER_PLAYER

    def move(self, new_pos: Tuple[int, int]):
        """Updates the player's position."""
        self.pos = new_pos

    def place_wall(self) -> bool:
        """
        Decrements the wall count if walls are available.
        Returns True if successful, False if out of walls.
        """
        if self.walls_remaining > 0:
            self.walls_remaining -= 1
            return True
        return False

    def has_won(self) -> bool:
        """Checks if the player has reached their target row."""
        return self.pos[0] == self.target_row
