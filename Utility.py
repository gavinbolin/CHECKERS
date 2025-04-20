class Utility:
    def __init__(self, interactive, graphics, tkinter, gui_board, colors):
        self.interactive = interactive
        self.graphics = graphics
        self.c = tkinter
        self.gui_board = gui_board
        self.colors = colors
    
    def execute_move(self, board, move, piece, current_player):
        other_player = 1
        if current_player == 1:
            other_player = 2
        if move is not None: # Remove attacked piece???
            if move == 'se':
                if board[piece[0]+1][piece[1]+1] == other_player and board[piece[0]+2][piece[1]+2] == 0:
                    self.update_board(board, [2,2], piece, current_player)
                    self.update_board(board, [0,0], [piece[0]+1,piece[1]+1], other_player)
                else:
                    self.update_board(board, [1,1], piece, current_player)
            if move == 'sw':
                if board[piece[0]+1][piece[1]-1] == other_player and board[piece[0]+2][piece[1]-2] == 0:
                    self.update_board(board, [2,-2], piece, current_player)
                    self.update_board(board, [0,0], [piece[0]+1,piece[1]-1], other_player)
                else:
                    self.update_board(board, [1,-1], piece, current_player)
            if move == 'ne':
                if board[piece[0]-1][piece[1]+1] == other_player and board[piece[0]-2][piece[1]+2] == 0:
                    self.update_board(board, [-2,2], piece, current_player)
                    self.update_board(board, [0,0], [piece[0]-1,piece[1]+1], other_player)
                else:
                    self.update_board(board, [-1,1], piece, current_player)
            if move == 'nw':
                if board[piece[0]-1][piece[1]-1] == other_player and board[piece[0]-2][piece[1]-2] == 0:
                    self.update_board(board, [-2,-2], piece, current_player)
                    self.update_board(board, [0,0], [piece[0]-1,piece[1]-1], other_player)
                else:
                    self.update_board(board, [-1,-1], piece, current_player)


    def update_board(self, board, move, piece, player_num):
        if move != None:
            # Remove piece
            if move == [0,0]:
                board[piece[0]][piece[1]] = 0
                if self.interactive:
                    if self.graphics:
                        self.c.itemconfig(self.gui_board[piece[1]][piece[0]], fill=self.colors[4])
                    else:
                        self.print_board(board)
            # Move current piece
            else:
                if board[piece[0]][piece[1]] == player_num+2: 
                    board[piece[0] + move[0]][piece[1] + move[1]] = player_num+2  # set piece to queen if so
                    if self.interactive:
                        if self.graphics:
                            self.c.itemconfig(self.gui_board[piece[1] + move[1]][piece[0] + move[0]], fill=self.colors[player_num+1])
                        else:
                            self.print_board(board)
                else:
                    board[piece[0] + move[0]][piece[1] + move[1]] = player_num  # set piece
                    if self.interactive:
                        if self.graphics:
                            self.c.itemconfig(self.gui_board[piece[1] + move[1]][piece[0] + move[0]], fill=self.colors[player_num-1])
                        else:
                            self.print_board(board)
                board[piece[0]][piece[1]] = 0

                # Checks for queens
                if (piece[0] + move[0] == 0) and player_num == 1:  
                    board[piece[0] + move[0]][piece[1] + move[1]] = 3
                    if self.graphics:
                        self.c.itemconfig(self.gui_board[piece[1] + move[1]][piece[0] + move[0]], fill=self.colors[player_num+1])
                    else:
                        self.print_board(board)
                if (piece[0] + move[0] == 7) and player_num == 2: 
                    board[piece[0] + move[0]][piece[1] + move[1]] = 4
                    if self.graphics:
                        self.c.itemconfig(self.gui_board[piece[1] + move[1]][piece[0] + move[0]], fill=self.colors[player_num+1])
                    else:
                        self.print_board(board)

                if self.interactive:
                    if self.graphics:
                        self.c.itemconfig(self.gui_board[piece[1]][piece[0]], fill=self.colors[4])
                    else:
                        self.print_board(board)
        else:
            board[piece[0]][piece[1]] = player_num
            if self.interactive:
                if self.graphics:
                    self.c.itemconfig(self.gui_board[piece[1]][piece[0]], fill=self.colors[player_num-1])
                else:
                    self.print_board(board)


    def print_board(self, board):
        for r in range(0,board.shape[0]):
            for c in range(0, board.shape[1]):
                if board[r,c] == 0:
                    print(' . ', end="")
                elif board[r,c] == 1:
                    print(' x ', end="")
                elif board[r,c] == 2:
                    print(' o ', end="")
                elif board[r,c] == 3:
                    print(' X ', end="")
                elif board[r,c] == 4:
                    print(' O ', end="")
            print(' ')