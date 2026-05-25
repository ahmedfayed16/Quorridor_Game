# game.py
from board import Board
from player import Player
from utils import START_POSITIONS, WALLS_PER_PLAYER, Orientation, BOARD_SIZE
from pathfinding import bfs_path_exists


class Game:
    def __init__(self):
        self.board = Board()
        # Initialize players using START_POSITIONS and WALLS_PER_PLAYER
        self.player1 = Player("P1")
        self.player2 = Player("P2")

        self.current_player = self.player1
        self.winner = None

    def get_opponent(self):
        return self.player2 if self.current_player == self.player1 else self.player1

    def switch_turn(self):
        self.current_player = self.get_opponent()

    def move_pawn(self, row: int, col: int) -> bool:
        """Attempts to move the current player's pawn to the specified cell."""
        if self.winner:
            return False

        opponent = self.get_opponent()
        valid_moves = self.board.get_valid_adjacent_cells(self.current_player.pos)

        # Normal adjacency move
        if (row, col) in valid_moves and (row, col) != opponent.pos:
            self.current_player.move((row, col))
            if self.current_player.has_won():
                self.winner = self.current_player
            else:
                self.switch_turn()
            return True

        # Jumping logic: opponent directly adjacent
        if opponent.pos in valid_moves:
            # Try direct jump first
            behind_opponent = (
                opponent.pos[0] + (opponent.pos[0] - self.current_player.pos[0]),
                opponent.pos[1] + (opponent.pos[1] - self.current_player.pos[1])
            )

            if behind_opponent in self.board.get_valid_adjacent_cells(opponent.pos):
                if (row, col) == behind_opponent:
                    self.current_player.move((row, col))
                    if self.current_player.has_won():
                        self.winner = self.current_player
                    else:
                        self.switch_turn()
                    return True
            else:
                # Direct jump blocked → allow diagonal moves
                for jm in self.board.get_valid_adjacent_cells(opponent.pos):
                    if (row, col) == jm:
                        self.current_player.move((row, col))
                        if self.current_player.has_won():
                            self.winner = self.current_player
                        else:
                            self.switch_turn()
                        return True

        return False

    def place_wall(self, row: int, col: int, orientation: Orientation) -> bool:
        """Attempts to place a wall for the current player."""
        if self.winner:
            return False

        if self.current_player.walls_remaining > 0:
            # Temporarily place wall and validate paths
            if self.board.place_wall(row, col, orientation):
                # Check if both players still have a path
                if bfs_path_exists(self.board, self.player1) and bfs_path_exists(self.board, self.player2):
                    self.current_player.place_wall()  # Deduct wall count
                    self.switch_turn()
                    return True
                else:
                    # Rollback if invalid
                    self.board.remove_wall(row, col, orientation)
        return False

    def get_valid_moves(self, player):
        moves = self.board.get_valid_adjacent_cells(player.pos)
        opponent = self.get_opponent()

        pr, pc = player.pos
        or_, oc = opponent.pos

        # If opponent is adjacent
        if abs(pr - or_) + abs(pc - oc) == 1:
            # Direct jump cell
            jump_r = or_ + (or_ - pr)
            jump_c = oc + (oc - pc)

            # Check if direct jump is possible (no wall blocking)
            if (jump_r, jump_c) in self.board.get_valid_adjacent_cells(opponent.pos):
                if self.is_cell_free(jump_r, jump_c):
                    moves.append((jump_r, jump_c))
            else:
                # Direct jump blocked → allow diagonals
                for diag_r, diag_c in self.board.get_valid_adjacent_cells(opponent.pos):
                    if self.is_cell_free(diag_r, diag_c):
                        moves.append((diag_r, diag_c))

        return moves

    def is_cell_free(self, r, c):
        """Return True if cell is inside board and not occupied by a pawn."""
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            return False
        if (r, c) == self.player1.pos or (r, c) == self.player2.pos:
            return False
        return True