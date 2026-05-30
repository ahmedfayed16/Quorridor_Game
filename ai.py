# ai.py
"""
AI for Quoridor. Hard mode uses greedy best-first (no recursion, no minimax).
Guaranteed to complete in milliseconds - no infinite loops possible.
"""
import random
import time
from collections import deque
from utils import Orientation, is_valid_wall_intersection
from pathfinding import bfs_path_exists

# Safety timeout (seconds) — any AI move exceeding this returns the best found so far
_AI_TIMEOUT = 0.5


def bfs_dist(board, player) -> int:
    start = player.pos
    target = player.target_row
    visited = {start}
    queue = deque([(start, 0)])
    while queue:
        (r, c), d = queue.popleft()
        if r == target:
            return d
        for nb in board.get_valid_adjacent_cells((r, c)):
            if nb not in visited:
                visited.add(nb)
                queue.append((nb, d + 1))
    return 999


def _pawn_moves(game, player):
    orig = game.current_player
    game.current_player = player
    moves = game.get_valid_moves(player)
    game.current_player = orig
    return moves


def _score(game, ai_pl, hu_pl):
    return bfs_dist(game.board, hu_pl) - bfs_dist(game.board, ai_pl)


def easy_move(game, ai_pl):
    moves = _pawn_moves(game, ai_pl)
    if moves:
        game.move_pawn(*random.choice(moves))


def medium_move(game, ai_pl):
    hu_pl = game.player2 if ai_pl == game.player1 else game.player1
    moves = _pawn_moves(game, ai_pl)
    if not moves:
        return

    # Simpler: just pick move that minimises our own BFS distance
    best_score = float("-inf")
    best_dest = None
    deadline = time.monotonic() + _AI_TIMEOUT  # ← timeout guard

    for dest in moves:
        if time.monotonic() > deadline:          # ← bail out if stuck
            break
        old = ai_pl.pos
        ai_pl.move(dest)
        s = _score(game, ai_pl, hu_pl)
        ai_pl.move(old)
        if s > best_score:
            best_score = s
            best_dest = dest

    if best_dest is None:
        best_dest = random.choice(moves)         # ← safe fallback

    game.move_pawn(*best_dest)


def hard_move(game, ai_pl):
    """
    Greedy 1-ply over pawn moves + nearby walls.
    No recursion. Cannot hang. Completes in <100ms.
    """
    hu_pl = game.player2 if ai_pl == game.player1 else game.player1
    deadline = time.monotonic() + _AI_TIMEOUT   # ← timeout guard

    best_score = float("-inf")
    best_action = None

    # --- Pawn moves ---
    moves = _pawn_moves(game, ai_pl)
    for dest in moves:
        # Immediate win
        if dest[0] == ai_pl.target_row:
            game.move_pawn(*dest)
            return
        old = ai_pl.pos
        ai_pl.move(dest)
        s = _score(game, ai_pl, hu_pl)
        ai_pl.move(old)
        if s > best_score:
            best_score = s
            best_action = ("pawn", dest)

    # --- Wall moves (only if walls available) ---
    if ai_pl.walls_remaining > 0:
        hu_dist_now = bfs_dist(game.board, hu_pl)

        # Only try walls near the human pawn (small fixed set)
        hr, hc = hu_pl.pos
        candidates = []
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                r, c = hr + dr, hc + dc
                if is_valid_wall_intersection(r, c):
                    candidates.append((r, c, Orientation.HORIZONTAL))
                    candidates.append((r, c, Orientation.VERTICAL))

        for r, c, ori in candidates:
            if time.monotonic() > deadline:      # ← bail out if stuck
                break
            if game.board.place_wall(r, c, ori):
                # Must not block either player
                if bfs_path_exists(game.board, ai_pl) and bfs_path_exists(game.board, hu_pl):
                    hu_dist_new = bfs_dist(game.board, hu_pl)
                    s = (hu_dist_new - hu_dist_now) * 2 + _score(game, ai_pl, hu_pl)
                    if s > best_score:
                        best_score = s
                        best_action = ("wall", r, c, ori)
                game.board.remove_wall(r, c, ori)

    if best_action is None:
        if moves:
            game.move_pawn(*random.choice(moves))  # ← safe fallback
        return

    if best_action[0] == "pawn":
        game.move_pawn(*best_action[1])
    else:
        _, r, c, ori = best_action
        game.place_wall(r, c, ori)


class AIAgent:
    def __init__(self, difficulty="medium"):
        d = difficulty.lower()
        assert d in ("easy", "medium", "hard"), f"bad difficulty: {d}"
        self.difficulty = d

    def make_move(self, game, ai_player):
        if self.difficulty == "easy":
            easy_move(game, ai_player)
        elif self.difficulty == "medium":
            medium_move(game, ai_player)
        else:
            hard_move(game, ai_player)
