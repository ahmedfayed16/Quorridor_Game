import tkinter as tk
from pathfinding import validate_wall
from tkinter import messagebox
from utils import (
    BOARD_SIZE, CELL_SIZE, WALL_THICKNESS, MARGIN,
    Orientation, grid_to_pixel, COLORS
)
from game import Game


class QuoridorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quoridor - PvP")
        self.game = Game()

        # Calculate canvas dimensions based on 9x9 cells + 8 walls + margins
        self.canvas_size = (MARGIN * 2) + (BOARD_SIZE * CELL_SIZE) + ((BOARD_SIZE - 1) * WALL_THICKNESS)

        self.info_var = tk.StringVar()
        self.info_label = tk.Label(root, textvariable=self.info_var, font=("Arial", 14))
        self.info_label.pack(pady=10)



        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack()


        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Motion>", self.handle_hover)  # NEW: hover preview
        self.update_ui()

    def draw_board(self):
        self.canvas.delete("all")

        # Draw 9x9 Grid Cells
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1, y1 = grid_to_pixel(r, c)
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=COLORS["board"], outline=COLORS["grid"]
                )

        # Draw Placed Walls
        for r, c in self.game.board.horizontal_walls:
            x, y = grid_to_pixel(r, c)
            self.canvas.create_rectangle(
                x, y + CELL_SIZE,
                   x + (CELL_SIZE * 2) + WALL_THICKNESS, y + CELL_SIZE + WALL_THICKNESS,
                fill=COLORS["wall"]
            )

        for r, c in self.game.board.vertical_walls:
            x, y = grid_to_pixel(r, c)
            self.canvas.create_rectangle(
                x + CELL_SIZE, y,
                x + CELL_SIZE + WALL_THICKNESS, y + (CELL_SIZE * 2) + WALL_THICKNESS,
                fill=COLORS["wall"]
            )

        # Draw Pawns
        self.draw_pawn(self.game.player1.pos, COLORS["p1"])  # Player 1
        self.draw_pawn(self.game.player2.pos, COLORS["p2"])  # Player 2

        # Highlight valid moves for current player
        valid_moves = self.game.get_valid_moves(self.game.current_player)
        opponent_pos = self.game.get_opponent().pos

        for r, c in valid_moves:
            if (r, c) != opponent_pos:
                x1, y1 = grid_to_pixel(r, c)
                self.canvas.create_rectangle(
                    x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                    outline="green", width=3, dash=(4, 2), tags="highlight"
                )

    def draw_pawn(self, pos, color):
        r, c = pos
        x1, y1 = grid_to_pixel(r, c)
        padding = 10
        self.canvas.create_oval(
            x1 + padding, y1 + padding,
            x1 + CELL_SIZE - padding, y1 + CELL_SIZE - padding,
            fill=color
        )

    def handle_click(self, event):
        if self.game.winner:
            return

        x, y = event.x, event.y

        # Check if a cell was clicked (Pawn Move)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                px, py = grid_to_pixel(r, c)
                if px <= x <= px + CELL_SIZE and py <= y <= py + CELL_SIZE:
                    self.game.move_pawn(r, c)
                    self.update_ui()
                    return

        # Check if a wall gap was clicked (Wall Placement)
        for r in range(BOARD_SIZE - 1):
            for c in range(BOARD_SIZE - 1):
                px, py = grid_to_pixel(r, c)

                # Horizontal wall zone
                if px <= x <= px + (CELL_SIZE * 2) and py + CELL_SIZE <= y <= py + CELL_SIZE + WALL_THICKNESS:
                    self.game.place_wall(r, c, Orientation.HORIZONTAL)
                    self.update_ui()
                    return

                # Vertical wall zone
                if px + CELL_SIZE <= x <= px + CELL_SIZE + WALL_THICKNESS and py <= y <= py + (CELL_SIZE * 2):
                    self.game.place_wall(r, c, Orientation.VERTICAL)
                    self.update_ui()
                    return

    def handle_hover(self, event):
        if self.game.winner:
            return

        x, y = event.x, event.y
        self.canvas.delete("preview")  # clear old preview

        for r in range(BOARD_SIZE - 1):
            for c in range(BOARD_SIZE - 1):
                px, py = grid_to_pixel(r, c)

                # Horizontal preview zone
                if px <= x <= px + (CELL_SIZE * 2) and py + CELL_SIZE <= y <= py + CELL_SIZE + WALL_THICKNESS:
                    self.canvas.create_rectangle(
                        px, py + CELL_SIZE,
                            px + (CELL_SIZE * 2) + WALL_THICKNESS, py + CELL_SIZE + WALL_THICKNESS,
                        fill=COLORS["wall"], stipple="gray50", tags="preview"
                    )
                    return

                # Vertical preview zone
                if px + CELL_SIZE <= x <= px + CELL_SIZE + WALL_THICKNESS and py <= y <= py + (CELL_SIZE * 2):
                    self.canvas.create_rectangle(
                        px + CELL_SIZE, py,
                        px + CELL_SIZE + WALL_THICKNESS, py + (CELL_SIZE * 2) + WALL_THICKNESS,
                        fill=COLORS["wall"], stipple="gray50", tags="preview"
                    )
                    return

    def reset_game(self):
        """Reset the game to start a new match."""
        self.game = Game()  # create a fresh Game instance
        self.update_ui()

    def update_ui(self):
        self.draw_board()
        if self.game.winner:
            self.info_var.set(f"Player {self.game.winner.player_id} Wins!")
            again = messagebox.askyesno("Game Over", f"Player {self.game.winner.player_id} wins! Play again?")
            if again:
                self.reset_game()
        else:
            current = self.game.current_player
            self.info_var.set(f"Player {current.player_id}'s Turn | Walls: {current.walls_remaining}")
