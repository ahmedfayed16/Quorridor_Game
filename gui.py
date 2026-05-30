# gui.py
import tkinter as tk
from tkinter import messagebox
import threading
from utils import (
    BOARD_SIZE, CELL_SIZE, WALL_THICKNESS, MARGIN,
    Orientation, grid_to_pixel, COLORS
)
from game import Game
from ai import AIAgent


class QuoridorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quoridor")
        self.root.resizable(False, False)

        self.game = None
        self.ai_agent = None
        self.ai_plays_as = None
        self.ai_thinking = False   # True while background thread is running

        self.canvas_size = (MARGIN * 2) + (BOARD_SIZE * CELL_SIZE) + ((BOARD_SIZE - 1) * WALL_THICKNESS)

        # ── Left sidebar ─────────────────────────────────────────────
        sidebar = tk.Frame(root, width=180, bg="#2b2b2b", padx=12, pady=14)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="QUORIDOR", bg="#2b2b2b", fg="white",
                 font=("Arial", 15, "bold")).pack(pady=(0, 18))

        tk.Label(sidebar, text="Mode", bg="#2b2b2b", fg="#aaaaaa",
                 font=("Arial", 9, "bold")).pack(anchor=tk.W)

        self.mode_var = tk.StringVar(value="pvp")
        for text, val in [("Human vs Human", "pvp"), ("vs Computer", "pvc")]:
            tk.Radiobutton(sidebar, text=text, variable=self.mode_var, value=val,
                           bg="#2b2b2b", fg="white", selectcolor="#444444",
                           activebackground="#2b2b2b", activeforeground="white",
                           font=("Arial", 10), anchor=tk.W).pack(fill=tk.X, pady=1)

        tk.Label(sidebar, text="", bg="#2b2b2b").pack(pady=4)
        tk.Label(sidebar, text="AI Difficulty", bg="#2b2b2b", fg="#aaaaaa",
                 font=("Arial", 9, "bold")).pack(anchor=tk.W)

        self.diff_var = tk.StringVar(value="medium")
        for text, val in [("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")]:
            tk.Radiobutton(sidebar, text=text, variable=self.diff_var, value=val,
                           bg="#2b2b2b", fg="white", selectcolor="#444444",
                           activebackground="#2b2b2b", activeforeground="white",
                           font=("Arial", 10), anchor=tk.W).pack(fill=tk.X, pady=1)

        tk.Label(sidebar, text="", bg="#2b2b2b").pack(pady=4)

        tk.Button(sidebar, text="▶  New Game", command=self._start_game,
                  bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                  relief=tk.FLAT, padx=8, pady=6, cursor="hand2").pack(fill=tk.X, pady=(0, 6))

        tk.Button(sidebar, text="✕  Quit", command=root.quit,
                  bg="#c0392b", fg="white", font=("Arial", 10),
                  relief=tk.FLAT, padx=8, pady=4, cursor="hand2").pack(fill=tk.X)

        tk.Label(sidebar, text="", bg="#2b2b2b").pack(expand=True)

        self.wall_p1_var = tk.StringVar(value="")
        self.wall_p2_var = tk.StringVar(value="")
        tk.Label(sidebar, textvariable=self.wall_p1_var, bg="#2b2b2b",
                 fg=COLORS["p1"], font=("Arial", 10, "bold")).pack(anchor=tk.W)
        tk.Label(sidebar, textvariable=self.wall_p2_var, bg="#2b2b2b",
                 fg=COLORS["p2"], font=("Arial", 10, "bold")).pack(anchor=tk.W)

        # ── Right: info + canvas ──────────────────────────────────────
        right = tk.Frame(root, bg="white")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.info_var = tk.StringVar(value="Press ▶ New Game to start")
        tk.Label(right, textvariable=self.info_var, font=("Arial", 13),
                 bg="white", pady=6).pack()

        self.canvas = tk.Canvas(right, width=self.canvas_size,
                                height=self.canvas_size, bg="white",
                                highlightthickness=0)
        self.canvas.pack(padx=10, pady=(0, 10))

        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Motion>", self.handle_hover)

        self._draw_empty_board()

    # ── Empty board ───────────────────────────────────────────────────

    def _draw_empty_board(self):
        self.canvas.delete("all")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1, y1 = grid_to_pixel(r, c)
                self.canvas.create_rectangle(
                    x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                    fill=COLORS["board"], outline=COLORS["grid"])

    # ── Start / reset ─────────────────────────────────────────────────

    def _start_game(self):
        # If AI thread is running, just flag a new game and return
        if self.ai_thinking:
            return

        self.game = Game()
        mode = self.mode_var.get()
        diff = self.diff_var.get()

        if mode == "pvc":
            self.ai_agent = AIAgent(difficulty=diff)
            self.ai_plays_as = "P2"
            self.root.title(f"Quoridor — vs Computer ({diff.capitalize()})")
        else:
            self.ai_agent = None
            self.ai_plays_as = None
            self.root.title("Quoridor — Human vs Human")

        self.ai_thinking = False
        self.update_ui()

    # ── Drawing ───────────────────────────────────────────────────────

    def draw_board(self):
        if self.game is None:
            return
        self.canvas.delete("all")

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1, y1 = grid_to_pixel(r, c)
                self.canvas.create_rectangle(
                    x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                    fill=COLORS["board"], outline=COLORS["grid"])

        for r, c in self.game.board.horizontal_walls:
            x, y = grid_to_pixel(r, c)
            self.canvas.create_rectangle(
                x, y + CELL_SIZE,
                x + (CELL_SIZE * 2) + WALL_THICKNESS, y + CELL_SIZE + WALL_THICKNESS,
                fill=COLORS["wall"])

        for r, c in self.game.board.vertical_walls:
            x, y = grid_to_pixel(r, c)
            self.canvas.create_rectangle(
                x + CELL_SIZE, y,
                x + CELL_SIZE + WALL_THICKNESS, y + (CELL_SIZE * 2) + WALL_THICKNESS,
                fill=COLORS["wall"])

        self._draw_pawn(self.game.player1.pos, COLORS["p1"])
        self._draw_pawn(self.game.player2.pos, COLORS["p2"])

        human_turn = (
            self.ai_agent is None or
            self.game.current_player.player_id != self.ai_plays_as
        )
        if human_turn and not self.game.winner and not self.ai_thinking:
            for r, c in self.game.get_valid_moves(self.game.current_player):
                if (r, c) != self.game.get_opponent().pos:
                    x1, y1 = grid_to_pixel(r, c)
                    self.canvas.create_rectangle(
                        x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                        outline="green", width=3, dash=(4, 2), tags="highlight")

    def _draw_pawn(self, pos, color):
        r, c = pos
        x1, y1 = grid_to_pixel(r, c)
        p = 10
        self.canvas.create_oval(
            x1 + p, y1 + p, x1 + CELL_SIZE - p, y1 + CELL_SIZE - p,
            fill=color)

    # ── Input ─────────────────────────────────────────────────────────

    def handle_click(self, event):
        if self.game is None or self.game.winner or self.ai_thinking:
            return
        if self.ai_agent and self.game.current_player.player_id == self.ai_plays_as:
            return

        x, y = event.x, event.y

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                px, py = grid_to_pixel(r, c)
                if px <= x <= px + CELL_SIZE and py <= y <= py + CELL_SIZE:
                    self.game.move_pawn(r, c)
                    self.update_ui()
                    return

        for r in range(BOARD_SIZE - 1):
            for c in range(BOARD_SIZE - 1):
                px, py = grid_to_pixel(r, c)
                if px <= x <= px + (CELL_SIZE * 2) and py + CELL_SIZE <= y <= py + CELL_SIZE + WALL_THICKNESS:
                    self.game.place_wall(r, c, Orientation.HORIZONTAL)
                    self.update_ui()
                    return
                if px + CELL_SIZE <= x <= px + CELL_SIZE + WALL_THICKNESS and py <= y <= py + (CELL_SIZE * 2):
                    self.game.place_wall(r, c, Orientation.VERTICAL)
                    self.update_ui()
                    return

    def handle_hover(self, event):
        if self.game is None or self.game.winner or self.ai_thinking:
            return
        if self.ai_agent and self.game.current_player.player_id == self.ai_plays_as:
            return

        x, y = event.x, event.y
        self.canvas.delete("preview")

        for r in range(BOARD_SIZE - 1):
            for c in range(BOARD_SIZE - 1):
                px, py = grid_to_pixel(r, c)
                if px <= x <= px + (CELL_SIZE * 2) and py + CELL_SIZE <= y <= py + CELL_SIZE + WALL_THICKNESS:
                    self.canvas.create_rectangle(
                        px, py + CELL_SIZE,
                        px + (CELL_SIZE * 2) + WALL_THICKNESS, py + CELL_SIZE + WALL_THICKNESS,
                        fill=COLORS["wall"], stipple="gray50", tags="preview")
                    return
                if px + CELL_SIZE <= x <= px + CELL_SIZE + WALL_THICKNESS and py <= y <= py + (CELL_SIZE * 2):
                    self.canvas.create_rectangle(
                        px + CELL_SIZE, py,
                        px + CELL_SIZE + WALL_THICKNESS, py + (CELL_SIZE * 2) + WALL_THICKNESS,
                        fill=COLORS["wall"], stipple="gray50", tags="preview")
                    return

    # ── AI — runs in background thread ────────────────────────────────

    def _trigger_ai(self):
        """Called after a human move when it's now the AI's turn."""
        self.ai_thinking = True
        self.info_var.set("🤖  Computer is thinking…")
        self.draw_board()   # refresh board immediately so human sees their move
        self.root.update()  # flush the UI before the thread starts

        thread = threading.Thread(target=self._ai_worker, daemon=True)
        thread.start()

    def _ai_worker(self):
        """Runs on a background thread — does NOT touch Tkinter widgets."""
        try:
            ai_pl = self.game.player2 if self.ai_plays_as == "P2" else self.game.player1
            self.ai_agent.make_move(self.game, ai_pl)
        except Exception as e:
            print(f"AI error: {e}")
        finally:
            # Schedule UI update back on the main thread
            self.root.after(0, self._ai_done)

    def _ai_done(self):
        """Called on the main thread once the AI thread finishes."""
        self.ai_thinking = False
        self.update_ui()

    # ── UI update ─────────────────────────────────────────────────────

    def update_ui(self):
        if self.game is None:
            return

        self.draw_board()

        self.wall_p1_var.set(f"● P1 walls: {self.game.player1.walls_remaining}")
        self.wall_p2_var.set(f"● P2 walls: {self.game.player2.walls_remaining}")

        if self.game.winner:
            wid = self.game.winner.player_id
            if self.ai_agent and wid == self.ai_plays_as:
                headline, msg = "Computer Wins!", "Computer wins! Better luck next time."
            elif self.ai_agent:
                headline, msg = "You Win! 🎉", "You beat the computer!"
            else:
                headline, msg = f"Player {wid} Wins! 🎉", f"Player {wid} wins!"
            self.info_var.set(headline)
            again = messagebox.askyesno("Game Over", f"{msg}\n\nPlay again?")
            if again:
                self._start_game()
            return

        cur = self.game.current_player
        is_ai_turn = self.ai_agent and cur.player_id == self.ai_plays_as

        if is_ai_turn and not self.ai_thinking:
            self._trigger_ai()
        elif not self.ai_thinking:
            if self.ai_agent:
                whose = "Your Turn" if cur.player_id != self.ai_plays_as else "Computer's Turn"
            else:
                whose = f"Player {cur.player_id}'s Turn"
            self.info_var.set(whose)
