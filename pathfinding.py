# pathfinding.py
"""
Pathfinding utilities for Quoridor.
Used to validate wall placements and check if players can reach their goal.
"""

from typing import Tuple, Set, List
from collections import deque
from utils import in_bounds
from board import Board
from player import Player

def bfs_path_exists(board: Board, player: Player) -> bool:
    """
    Runs BFS from the player's current position to check if a path exists
    to their target row. Returns True if reachable, False otherwise.
    """
    start = player.pos
    visited: Set[Tuple[int, int]] = set()
    queue = deque([start])

    while queue:
        r, c = queue.popleft()

        # Check win condition
        if r == player.target_row:
            return True

        if (r, c) in visited:
            continue
        visited.add((r, c))

        # Explore neighbors
        for neighbor in board.get_valid_adjacent_cells((r, c)):
            if neighbor not in visited and in_bounds(*neighbor):
                queue.append(neighbor)

    return False


def validate_wall(board: Board, row: int, col: int, orientation) -> bool:
    """
    Temporarily places a wall and checks if both players still have a path.
    Removes the wall afterward. Returns True if valid, False otherwise.
    """
    # Place wall
    success = board.place_wall(row, col, orientation)
    if not success:
        return False

    # Check both players
    valid = bfs_path_exists(board, board.game.players["P1"]) and bfs_path_exists(board, board.game.players["P2"])

    # Rollback wall placement
    board.remove_wall(row, col, orientation)

    return valid
