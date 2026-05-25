# utils.py
"""
Utility constants and helper functions for Quoridor game.
Imported by board.py, player.py, gui.py, and game.py.
"""

from enum import Enum
from typing import Tuple

# --- Core Constants ---
BOARD_SIZE = 9              # logical pawn grid (9x9)
PHYSICAL_SIZE = 17          # expanded grid for GUI (walls + pawns)
WALLS_PER_PLAYER = 10       # number of walls per player (2-player version)

# --- GUI Constants ---
CELL_SIZE = 60              # pixel size of each cell
WALL_THICKNESS = 10         # pixel thickness of walls
MARGIN = 40                 # margin around the board

# --- Starting Positions ---
START_POSITIONS = {
    "P1": (0, BOARD_SIZE // 2),              # Player 1 starts at top center
    "P2": (BOARD_SIZE - 1, BOARD_SIZE // 2)  # Player 2 starts at bottom center
}

# --- Enums ---
class Orientation(Enum):
    HORIZONTAL = "H"
    VERTICAL = "V"

class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

# --- Colors (for GUI rendering) ---
COLORS = {
    "board": "#EEE8AA",      # light khaki background
    "grid": "#000000",       # black grid lines
    "p1": "#1E90FF",         # blue pawn
    "p2": "#FF4500",         # orange pawn
    "wall": "#8B4513",       # brown walls
    "highlight": "#90EE90"   # light green for valid moves
}

# --- Helper Functions ---
def grid_to_pixel(row: int, col: int) -> Tuple[int, int]:
    """
    Converts board grid coordinates to pixel coordinates for the GUI.
    Returns the top-left pixel (x, y) of a given cell.
    """
    x = MARGIN + col * (CELL_SIZE + WALL_THICKNESS)
    y = MARGIN + row * (CELL_SIZE + WALL_THICKNESS)
    return x, y

def in_bounds(row: int, col: int) -> bool:
    """Checks if a given coordinate is within the logical 9x9 board."""
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

def in_physical_bounds(x: int, y: int) -> bool:
    """Checks if coordinates are inside the physical 17x17 board."""
    return 0 <= x < PHYSICAL_SIZE and 0 <= y < PHYSICAL_SIZE

def is_valid_wall_intersection(row: int, col: int) -> bool:
    """Checks if a given coordinate is a valid wall intersection (8x8 grid)."""
    return 0 <= row < BOARD_SIZE - 1 and 0 <= col < BOARD_SIZE - 1

def opposite_side(player: str, position: Tuple[int, int]) -> bool:
    """
    Check if a player has reached the opposite side (win condition).
    position is a tuple (row, col) on the logical 9x9 board.
    """
    if player == "P1":
        return position[0] == BOARD_SIZE - 1
    elif player == "P2":
        return position[0] == 0
    return False

def logical_to_physical(x: int, y: int) -> Tuple[int, int]:
    """
    Convert logical 9x9 coordinates to physical 17x17 coordinates.
    Pawns occupy odd cells in the physical grid.
    """
    return (x * 2, y * 2)

def physical_to_logical(x: int, y: int) -> Tuple[int, int]:
    """
    Convert physical 17x17 coordinates back to logical 9x9.
    Only valid for pawn positions (odd cells).
    """
    return (x // 2, y // 2)
