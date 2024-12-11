import tkinter as tk


class TicTacToeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tic Tac Toe")
        self.root.configure(bg="black")  # Set background color to black

        self.controller = None  # Will be set later

        # Control buttons frame (top-right)
        self.control_frame = tk.Frame(self.root, bg="black")
        self.control_frame.pack(anchor="ne", pady=10)

        self.reset_button = tk.Button(
            self.control_frame,
            text="Reset",
            font=("Arial", 14),
            bg="black",
            fg="white",
            activebackground="gray",
            activeforeground="white",
            command=self.reset_game,
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)

        self.quit_button = tk.Button(
            self.control_frame,
            text="Quit",
            font=("Arial", 14),
            bg="black",
            fg="white",
            activebackground="gray",
            activeforeground="white",
            command=self.quit_game,
        )
        self.quit_button.pack(side=tk.LEFT, padx=10)

        # Status message
        self.status_message = "Player 1's Turn"
        self.status_label = tk.Label(self.root, text=self.status_message, font=("Arial", 14), bg="black", fg="white")
        self.status_label.pack(pady=10)

        # Create a frame for the game grid
        self.grid_frame = tk.Frame(self.root, bg="black")
        self.grid_frame.pack()

        # Initialize grid buttons
        self.grid_buttons = []
        for row in range(3):
            button_row = []
            for col in range(3):
                btn = tk.Button(
                    self.grid_frame,
                    text=" ",
                    width=5,
                    height=2,
                    font=("Arial", 24),
                    bg="black",
                    fg="white",
                    activebackground="gray",
                    activeforeground="white",
                    command=lambda r=row, c=col: self.handle_grid_click(r, c),
                )
                btn.grid(row=row, column=col, padx=5, pady=5)
                button_row.append(btn)
            self.grid_buttons.append(button_row)

        # Player info frame (below grid)
        self.info_frame = tk.Frame(self.root, bg="black")
        self.info_frame.pack(pady=10)

        self.player1_label = tk.Label(self.info_frame, text="Player 1: X (Wins: 0, Ties: 0)", font=("Arial", 12), bg="black", fg="white")
        self.player1_label.grid(row=0, column=0, padx=20)

        self.player2_label = tk.Label(self.info_frame, text="Player 2: O (Wins: 0, Ties: 0)", font=("Arial", 12), bg="black", fg="white")
        self.player2_label.grid(row=0, column=1, padx=20)

        # Continue button (initially hidden)
        self.continue_button = tk.Button(
            self.root,
            text="Continue",
            font=("Arial", 14),
            bg="yellow",
            fg="black",
            activebackground="gray",
            activeforeground="black",
            command=self.continue_game,
        )
        self.continue_button.pack(pady=10)
        self.continue_button.pack_forget()  # Hide the button initially

    def set_controller(self, controller):
        """Sets the controller to handle events."""
        self.controller = controller

    def handle_grid_click(self, row, col):
        """Handles grid button clicks."""
        if self.controller:
            self.controller.handle_move(row, col)

    def update_board(self, row, col, symbol):
        """Updates the UI for the given move."""
        self.grid_buttons[row][col].config(text=symbol, state=tk.DISABLED)

    def display_invalid_move(self):
        """Displays a message for an invalid move."""
        self.status_label.config(text="Invalid move! Cell already occupied.")

    def update_turn(self, current_player):
        """Updates the turn message and highlights the current player's name."""
        # Change the turn text in the label to show Player 1 or Player 2
        self.status_message = f"Player {1 if current_player == self.controller.player1 else 2}'s Turn"
        self.status_label.config(text=self.status_message)

        # Highlight the current player’s name in yellow
        p1_color = "yellow" if current_player == self.controller.player1 else "white"
        p2_color = "yellow" if current_player == self.controller.player2 else "white"

        # Update player labels with highlighted color for the current player
        self.player1_label.config(fg=p1_color)
        self.player2_label.config(fg=p2_color)

    def update_player_info(self, player1, player2, current_player):
        """Updates the player info section and highlights the current player's name."""
        p1_color = "yellow" if current_player == player1 else "white"
        p2_color = "yellow" if current_player == player2 else "white"

        self.player1_label.config(text=f"Player 1: X (Wins: {player1.getScore()['wins']}, Ties: {player1.getScore()['ties']})", fg=p1_color)
        self.player2_label.config(text=f"Player 2: O (Wins: {player2.getScore()['wins']}, Ties: {player2.getScore()['ties']})", fg=p2_color)


    def display_winner(self, winner):
        """Displays the winner message and disables the board."""
        self.status_message = f"{winner.getMark()} wins!"
        self.status_label.config(text=self.status_message)
        self.disable_board()
        self.show_continue_button()

    def display_tie(self):
        """Displays a tie message."""
        self.status_message = "It's a draw!"
        self.status_label.config(text=self.status_message)
        self.show_continue_button()

    def disable_board(self):
        """Disables all grid buttons."""
        for row in self.grid_buttons:
            for btn in row:
                btn.config(state=tk.DISABLED)

    def show_continue_button(self):
        """Displays the continue button."""
        self.continue_button.pack()

    def hide_continue_button(self):
        """Hides the continue button."""
        self.continue_button.pack_forget()

    def continue_game(self):
        """Handles the continuation of the game."""
        # Continue with the existing score, reset the board, and start a new game round.
        for row in self.grid_buttons:
            for btn in row:
                btn.config(text=" ", state=tk.NORMAL)  # Clear text and re-enable buttons
        self.status_label.config(text="Player 1's Turn")  # Reset status to Player 1's turn
        self.hide_continue_button()  # Ensure the continue button is hidden
        if self.controller:
            self.controller.continueGame()
        self.hide_continue_button()
        self.update_player_info()

    def reset_game(self):
        """Resets the UI for a new game."""
        for row in self.grid_buttons:
            for btn in row:
                btn.config(text=" ", state=tk.NORMAL)  # Clear text and re-enable buttons
        self.status_label.config(text="Player 1's Turn")  # Reset status to Player 1's turn
        self.hide_continue_button()  # Ensure the continue button is hidden
        self.controller.resetGame()



    def quit_game(self):
        """Quits the application."""
        self.root.destroy()

    def run(self):
        """Starts the GUI main loop."""
        self.root.mainloop()