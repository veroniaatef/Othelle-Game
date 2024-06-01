import copy
import tkinter as tk

class OthelloGame:
    def __init__(self):
        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 'W'
        self.board[3][4] = self.board[4][3] = 'B'
        self.current_player = 'B'

    def is_valid_move(self, row, col):
        if not (0 <= row < 8 and 0 <= col < 8) or self.board[row][col] != ' ':
            return False
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == self.opponent():
                while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == self.opponent():
                    r, c = r + dr, c + dc
                if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == self.current_player:
                    return True
        return False

    def opponent(self):
        return 'W' if self.current_player == 'B' else 'B'

    def make_move(self, row, col):
        if self.is_valid_move(row, col):
            self.board[row][col] = self.current_player
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            for dr, dc in directions:
                r, c = row + dr, col + dc
                to_flip = []
                while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == self.opponent():
                    to_flip.append((r, c))
                    r, c = r + dr, c + dc
                if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == self.current_player:
                    for r, c in to_flip:
                        self.board[r][c] = self.current_player
            self.current_player = self.opponent()

    def get_valid_moves(self):
        return [(row, col) for row in range(8) for col in range(8) if self.is_valid_move(row, col)]

    def game_over(self):
        return len(self.get_valid_moves()) == 0 and len(self.get_valid_moves_for_player(self.opponent())) == 0

    def get_valid_moves_for_player(self, player):
        original_player = self.current_player
        self.current_player = player
        valid_moves = [(row, col) for row in range(8) for col in range(8) if self.is_valid_move(row, col)]
        self.current_player = original_player
        return valid_moves

    def count_pieces(self):
        black_count = sum(row.count('B') for row in self.board)
        white_count = sum(row.count('W') for row in self.board)
        return black_count, white_count

    def utility(self):
        black_count, white_count = self.count_pieces()
        return black_count - white_count if self.current_player == 'B' else white_count - black_count


import copy
import time


class AIPlayer:
    DIFFICULTY_MAP = {"Easy": 1, "Medium": 3, "Hard": 5}

    def __init__(self, difficulty):
        self.depth = self.DIFFICULTY_MAP.get(difficulty, 1)
        self.difficulty = difficulty

    def make_move(self, game):
        start_time = time.time()
        depth = self.depth

        # Iterative deepening loop
        best_move = None
        for current_depth in range(1, depth + 1):
            _, move = self.minimax(game, current_depth, float('-inf'), float('inf'), maximizing_player=True)
            if move:
                best_move = move

            # Check if we have exceeded time limit (3 seconds for example)
            if time.time() - start_time > 3:  # Adjust time limit as needed
                break

        if best_move:
            game.make_move(*best_move)

    def minimax(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.game_over():
            return game.utility(), None
        best_utility = float('-inf') if maximizing_player else float('inf')
        best_move = None
        valid_moves = game.get_valid_moves()

        # Move ordering can improve performance by trying more promising moves first
        # For example, sort valid_moves based on some heuristic before processing

        for move in valid_moves:
            new_game = copy.deepcopy(game)
            new_game.make_move(*move)
            utility, _ = self.minimax(new_game, depth - 1, alpha, beta, not maximizing_player)

            if maximizing_player:
                if utility > best_utility:
                    best_utility = utility
                    best_move = move
                alpha = max(alpha, best_utility)
            else:
                if utility < best_utility:
                    best_utility = utility
                    best_move = move
                beta = min(beta, best_utility)

            if alpha >= beta:
                break

        return best_utility, best_move


class OthelloGUI:
    SQUARE_SIZE = 50

    def __init__(self, game, player1, player2=None):
        self.game = game
        self.player1 = player1
        self.player2 = player2

        self.root = tk.Tk()
        self.root.title("Othello")
        self.root.geometry("400x450")

        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()

        self.draw_board()

        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Motion>", self.handle_motion)

        self.current_player_label = tk.Label(self.root, text="Current Player: " + self.game.current_player)
        self.current_player_label.pack()

        self.game_over_label = tk.Label(self.root, text="")
        self.game_over_label.pack()

    def draw_board(self, highlight_move=None):
        self.canvas.delete("square")
        for row in range(8):
            for col in range(8):
                x0 = col * self.SQUARE_SIZE
                y0 = row * self.SQUARE_SIZE
                x1 = x0 + self.SQUARE_SIZE
                y1 = y0 + self.SQUARE_SIZE
                color = "green" if (row + col) % 2 == 0 else "dark green"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, tags="square")

        if highlight_move:
            row, col = highlight_move
            x0 = col * self.SQUARE_SIZE
            y0 = row * self.SQUARE_SIZE
            x1 = x0 + self.SQUARE_SIZE
            y1 = y0 + self.SQUARE_SIZE
            self.canvas.create_rectangle(x0, y0, x1, y1, fill="yellow", outline="", tags="highlight")

        for row in range(8):
            for col in range(8):
                x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                if self.game.board[row][col] == 'B':
                    self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill='black', tags="piece")
                elif self.game.board[row][col] == 'W':
                    self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill='white', tags="piece")

    def handle_click(self, event):
        if self.game.game_over():
            return

        col = event.x // self.SQUARE_SIZE
        row = event.y // self.SQUARE_SIZE
        if self.game.is_valid_move(row, col):
            self.game.make_move(row, col)
            self.draw_board()
            self.current_player_label.config(text="Current Player: " + self.game.current_player)
            self.check_game_over()
            if not self.game.game_over():
                self.make_ai_move()

    def handle_motion(self, event):
        if not self.game.game_over():
            col = event.x // self.SQUARE_SIZE
            row = event.y // self.SQUARE_SIZE
            if self.game.current_player == 'B':
                if self.game.is_valid_move(row, col):
                    self.draw_board(highlight_move=(row, col))
                else:
                    self.draw_board()
            else:
                valid_moves = self.game.get_valid_moves()
                if (row, col) in valid_moves:
                    self.draw_board(highlight_move=(row, col))
                else:
                    self.draw_board()

    def make_ai_move(self):
        while self.game.current_player == 'W' and self.player2:
            if len(self.game.get_valid_moves()) > 0:
                self.player2.make_move(self.game)
                self.draw_board()
                self.current_player_label.config(text="Current Player: " + self.game.current_player)
                self.check_game_over()
            else:
                self.game.current_player = self.game.opponent()

    def check_game_over(self):
        if self.game.game_over():
            black_count, white_count = self.game.count_pieces()
            if black_count > white_count:
                self.game_over_label.config(text="Black wins!")
            elif black_count < white_count:
                self.game_over_label.config(text="White wins!")
            else:
                self.game_over_label.config(text="It's a tie!")
        else:
            if len(self.game.get_valid_moves()) == 0:
                self.game.current_player = self.game.opponent()
                if len(self.game.get_valid_moves()) == 0:
                    self.check_game_over()
                else:
                    self.current_player_label.config(text="Current Player: " + self.game.current_player)
                    self.make_ai_move()

    def start(self):
        self.root.mainloop()


def main():
    root = tk.Tk()
    root.title("Othello")
    root.geometry("200x200")

    def start_game(difficulty):
        root.destroy()
        game = OthelloGame()
        ai_player = AIPlayer(difficulty)
        gui = OthelloGUI(game, None, ai_player)
        gui.start()

    difficulty_label = tk.Label(root, text="Choose difficulty:")
    difficulty_label.pack()

    difficulty_var = tk.StringVar(root)
    difficulty_var.set("Easy")

    difficulty_menu = tk.OptionMenu(root, difficulty_var, "Easy", "Medium", "Hard")
    difficulty_menu.pack()

    start_button = tk.Button(root, text="Start Game", command=lambda: start_game(difficulty_var.get()))
    start_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
