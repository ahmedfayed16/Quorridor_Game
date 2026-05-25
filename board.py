from typing import Tuple, List, Set
from utils import Orientation, Direction, in_bounds, is_valid_wall_intersection


class Board:
    def __init__(self):
        # Walls are stored as tuples of (row, col) representing the top-left cell of the intersection.
        self.horizontal_walls: Set[Tuple[int, int]] = set()
        self.vertical_walls: Set[Tuple[int, int]] = set()

    def place_wall(self, row: int, col: int, orientation: Orientation) -> bool:
        """
        Attempts to place a wall. Validates bounds and collisions.
        Note: Pathfinding validation (ensuring a path exists) should be
        called from game.py before finalizing this placement.
        """
        if not is_valid_wall_intersection(row, col):
            return False

        # Check for overlaps
        if orientation == Orientation.HORIZONTAL:
            # Cannot overlap exactly, cross a vertical wall at the same intersection,
            # or overlap with a horizontal wall shifted by 1.
            if ((row, col) in self.horizontal_walls or
                    (row, col) in self.vertical_walls or
                    (row, col - 1) in self.horizontal_walls or
                    (row, col + 1) in self.horizontal_walls):
                return False
            self.horizontal_walls.add((row, col))

        elif orientation == Orientation.VERTICAL:
            if ((row, col) in self.vertical_walls or
                    (row, col) in self.horizontal_walls or
                    (row - 1, col) in self.vertical_walls or
                    (row + 1, col) in self.vertical_walls):
                return False
            self.vertical_walls.add((row, col))

        return True

    def remove_wall(self, row: int, col: int, orientation: Orientation):
        """Removes a wall. Useful for backtracking during pathfinding validation."""
        if orientation == Orientation.HORIZONTAL:
            self.horizontal_walls.discard((row, col))
        else:
            self.vertical_walls.discard((row, col))

    def is_step_blocked_by_wall(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """
        Checks if a direct orthogonal step between pos1 and pos2 is blocked by a wall.
        Assumes pos1 and pos2 are adjacent.
        """
        r1, c1 = pos1
        r2, c2 = pos2

        # Moving Vertically
        if c1 == c2:
            min_r = min(r1, r2)
            # A horizontal wall at (min_r, c1) or (min_r, c1-1) blocks this vertical move.
            if (min_r, c1) in self.horizontal_walls or (min_r, c1 - 1) in self.horizontal_walls:
                return True

        # Moving Horizontally
        elif r1 == r2:
            min_c = min(c1, c2)
            # A vertical wall at (r1, min_c) or (r1-1, min_c) blocks this horizontal move.
            if (r1, min_c) in self.vertical_walls or (r1 - 1, min_c) in self.vertical_walls:
                return True

        return False

    def get_valid_adjacent_cells(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Returns all directly adjacent cells that are not blocked by a wall.
        (Does not account for other players / jumping rules - game.py handles that).
        """
        r, c = pos
        valid_cells = []

        for direction in Direction:
            dr, dc = direction.value
            new_r, new_c = r + dr, c + dc

            if in_bounds(new_r, new_c):
                if not self.is_step_blocked_by_wall(pos, (new_r, new_c)):
                    valid_cells.append((new_r, new_c))

        return valid_cells

