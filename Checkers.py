#Modified 10.3.2023 by Chris Archibald to
#  - run multiple experiments automatically
#  - incorporate MCTS with other code
#  - pass command line param string to each AI
#  - bypass tkinter when it doesn't exist, as that has proven problematic for some users

# system libs
import argparse
import multiprocessing as mp
import sys

#See if they have tkinter 
try:
    import tkinter as tk
    from tkinter import *
    graphics = True
except ImportError as err:
    graphics = False

# 3rd party libs
import numpy as np

# Local libs
from Player import AIPlayer, RandomPlayer, HumanPlayer

#https://stackoverflow.com/a/37737985
def turn_worker(board, send_end, p_func):
    send_end.send(p_func(board))

#List of symbols 
symbols = ['.', 'X', 'O']

#This is the main game class that will store the information 
#necessary for the game to play and also run the game
class Game:
    def __init__(self, player1, player2, time, interactive):
        self.players = [player1, player2]
        self.colors = ['blue', 'purple']
        self.current_turn = 0
        self.board = np.zeros([8,8]).astype(np.uint8)
        self.gui_board = []
        self.game_over = False
        self.winner = None
        self.ai_turn_limit = time
        self.interactive = interactive
        self.count = 0

        global graphics
        if not interactive:
            graphics = False

        if graphics:
            #https://stackoverflow.com/a/38159672
            root = tk.Tk()
            root.title('CHECKERS')
            self.player_string = tk.Label(root, text=player1.player_string)
            self.player_string.pack()
            self.c = tk.Canvas(root, width=400, height=400)
            self.c.pack()

            for row in range(0, 400, 50):
                column = []
                for col in range(0, 400, 50):
                    column.append(self.c.create_oval(row, col, row+50, col+50, fill=''))
                    # column.append(self.c.create_rectangle(row, col, row+50, col+50, fill=''))
                self.gui_board.append(column)

            # tk.Button(root, text='Next', command=self.make_move).pack() #remove, use only terminal..?
            self.start_state()
            self.make_move()
            root.mainloop()
        else:
            if interactive:
                self.print_board()
            self.gameloop()

    def start_state(self):
        # create start state of board
        for i in range(0,8,2):
            self.update_board(None, [0,i], 2)
            self.update_board(None, [1,i+1], 2)
            self.update_board(None, [2,i], 2)
            self.update_board(None, [5,i+1], 1)
            self.update_board(None, [6,i], 1)
            self.update_board(None, [7,i+1], 1)

    def gameloop(self):
        while True:
            print(self.board)
            if self.interactive:
                command = input("Press enter to continue game, Type x to end game: ")
                if command == 'x':
                    break
            self.make_move()
            if self.game_over:
                break

        if self.interactive:
            print('Game is over.  Thanks for playing')

    def make_move(self):
        self.count += 1
        if not self.game_over:
            current_player = self.players[self.current_turn]
            if current_player.type == 'mcts':
                p_func = current_player.get_mcts_move
                try:
                    recv_end, send_end = mp.Pipe(False)
                    p = mp.Process(target=turn_worker, args=(self.board, send_end, p_func))
                    p.start()
                    if p.join(self.ai_turn_limit) is None and p.is_alive():
                        p.terminate()
                        raise Exception('Player Exceeded time limit')
                except Exception as e:
                    uh_oh = 'Uh oh.... something is wrong with Player {}'
                    print(uh_oh.format(current_player.player_number))
                    print(e)
                    raise Exception('Game Over')

                move, piece = recv_end.recv()
            else:
                move, piece = current_player.get_move(self.board) # doesnt work for random??

            other_player = 1
            if current_player.player_number == 1:
                other_player = 2
            if move is not None: # Remove attacked piece???
                if move == 'se':
                    if self.board[piece[0]+1][piece[1]+1] == other_player and self.board[piece[0]+2][piece[1]+2] == 0:
                        self.update_board([2,2], piece, current_player.player_number)
                        self.update_board([0,0], [piece[0]+1,piece[1]+1], other_player)
                    else:
                        self.update_board([1,1], piece, current_player.player_number)
                if move == 'sw':
                    if self.board[piece[0]+1][piece[1]-1] == other_player and self.board[piece[0]+2][piece[1]-2] == 0:
                        self.update_board([2,-2], piece, current_player.player_number)
                        self.update_board([0,0], [piece[0]+1,piece[1]-1], other_player)
                    else:
                        self.update_board([1,-1], piece, current_player.player_number)
                if move == 'ne':
                    if self.board[piece[0]-1][piece[1]+1] == other_player and self.board[piece[0]-2][piece[1]+2] == 0:
                        self.update_board([-2,2], piece, current_player.player_number)
                        self.update_board([0,0], [piece[0]-1,piece[1]+1], other_player)
                    else:
                        self.update_board([-1,1], piece, current_player.player_number)
                if move == 'nw':
                    if self.board[piece[0]-1][piece[1]-1] == other_player and self.board[piece[0]-2][piece[1]-2] == 0:
                        self.update_board([-2,-2], piece, current_player.player_number)
                        self.update_board([0,0], [piece[0]-1,piece[1]-1], other_player)
                    else:
                        self.update_board([-1,-1], piece, current_player.player_number)


            # Determine game state (WIN/LOSS/TIE)
            if self.game_won(current_player.player_number):
                #Set the winner and losers
                self.winner = current_player.name
                self.loser = self.players[int(not self.current_turn)].name
                #Mark the game as over
                self.game_over = True
                if graphics:
                    self.player_string.configure(text=self.players[self.current_turn].player_string + ' wins!')
                else:
                    print(self.players[self.current_turn].player_string + ' wins!')
                print('Game over!')
            # IF GAME TIED ???
            # elif self.game_tied():
            #     #Mark the game as over
            #     self.game_over = True
            #     if graphics:
            #         self.player_string.configure(text='Game ends in a tie!')
            #     else:
            #         print('Game ends in a tie!')
            else:
                self.current_turn = int(not self.current_turn)
                if graphics:
                    self.player_string.configure(text=self.players[self.current_turn].name)
                    self.make_move()
                else:
                    print('Current Turn: ', self.players[self.current_turn].name, '  using symbol : ', symbols[self.players[self.current_turn].player_number])

    def update_board(self, move, piece, player_num):
        if move:
        # Remove piece
            if move == [0,0]:
                self.board[piece[0]][piece[1]] = 0
                if self.interactive:
                    if graphics:
                        self.c.itemconfig(self.gui_board[piece[1]][piece[0]], fill='white')
                    else:
                        self.print_board()
        # Move current piece
            else:
                self.board[piece[0] + move[0]][piece[1] + move[1]] = player_num
                if self.interactive:
                    if graphics:
                        self.c.itemconfig(self.gui_board[piece[1] + move[1]][piece[0] + move[0]], fill=self.colors[player_num-1])
                    else:
                        self.print_board()
                self.board[piece[0]][piece[1]] = 0
                if self.interactive:
                    if graphics:
                        self.c.itemconfig(self.gui_board[piece[1]][piece[0]], fill='white')
                    else:
                        self.print_board()
        # Create piece
        else:
            self.board[piece[0]][piece[1]] = player_num
            if self.interactive:
                if graphics:
                    self.c.itemconfig(self.gui_board[piece[1]][piece[0]], fill=self.colors[player_num-1])
                else:
                    self.print_board()


    def print_board(self):
        for r in range(0,self.board.shape[0]):
            for c in range(0, self.board.shape[1]):
                if self.board[r,c] == 0:
                    print(' . ', end="")
                elif self.board[r,c] == 1:
                    print(' X ', end="")
                elif self.board[r,c] == 2:
                    print(' O ', end="")
            print(' ')

        #Display the column names as well
        print('---------------------')            

        for c in range(0, self.board.shape[1]):
            print(f" {c} ", end="")
        print(' ')


    def game_tied(self): #track to see if pieces havnt been removed for 20 pieces or passed 100 moves
        if not 0 in self.board:
            return True
        return False

    def game_won(self, player_num):
        other = 2
        if player_num == 2:
            other = 1
        if (player_num in self.board) and other not in self.board:
            return True
        else:
            return False


def play_game(player1name, player2name, player1, player2, time, params1, params2, interactive, stats):
    """
    Creates player objects based on the string parameters that are passed
    to it and creates game, which then plays

    INPUTS:
    player1 - a string ['ab', 'random', 'human', 'mcts', 'expmax']
    player2 - a string ['ab', 'random', 'human', 'mcts', 'expmax']
    """
    def make_player(name, method, num, params):
        if method=='ab' or method=='expmax' or method == 'mcts':
            return AIPlayer(num, name, method, params)
        elif method=='random':
            return RandomPlayer(num)
        elif method=='human':
            return HumanPlayer(num)

    g = Game(make_player(player1name, player1, 1, params1), make_player(player2name, player2, 2, params2), time, interactive)

    #Update stats with winner, loser, or ties
    if g.winner:
        stats[g.winner]['wins'] += 1
        stats[g.loser]['losses'] += 1
    else:
        stats[player1name]['ties'] += 1
        stats[player2name]['ties'] += 1

#This function sets up everything for the experiments, and repeatedly calls play_game to run the games
def main(player1, player2, time, n, params1, params2):
    #Set up this run of the program

    #Create player names
    p1name = player1 
    if params1: 
        p1name += params1
    p2name = player2
    if params2:
        p2name += params2

    # if p1name == p2name:
    #     print('Error: players must be different or have different parameters!')
    #     sys.exit()

    #Get list of player names
    pnames = [p1name, p2name]

    #Access to player and paramstrings
    pstring = {p1name: player1, p2name: player2}
    params = {p1name: params1, p2name: params2}

    #Store what happened in each game
    stats = {p1name: {'wins': 0, 'ties': 0, 'losses': 0}, p2name: {'wins': 0, 'ties': 0, 'losses': 0}}

    #Are we running in interactive mode?
    interactive = False
    if n == 1 or 'human' in pnames or 'random' in pnames:
        interactive = True

    # #Play 2n games (Each player goes first n times)
    N = n
    # Unless n = 1, then we only play one game
    if n == 1:
        N = 1

    print(f"Playing {N} games between {p1name} and {p2name}")

    for i in range(N):
        #Play game with current player list
        play_game(pnames[0], pnames[1], pstring[pnames[0]], pstring[pnames[1]], time, params[pnames[0]], params[pnames[1]], interactive, stats)

        #Reverse the order of the players
        pnames.reverse()


    #Display the results of the games
    print('Experiment results: ')
    print(stats)

if __name__=='__main__':
    player_types = ['ab', 'random', 'human', 'mcts', 'expmax']
    parser = argparse.ArgumentParser()
    parser.add_argument('player1', choices=player_types)
    parser.add_argument('player2', choices=player_types)
    parser.add_argument('-p1', '--params1', help='Parameter string for agent 1', default=None)
    parser.add_argument('-p2', '--params2', help='Parameter string for agent 2', default=None)
    parser.add_argument('-n', '--number', 
                        help='Number of games each player goes first in match. If this number is 1, game will be interactive.',
                        type=int,
                        default=1)
    parser.add_argument('-t', '--time',
                        type=int,
                        default=60,
                        help='Time to wait for a move in seconds (int)')
    args = parser.parse_args()

    main(args.player1, args.player2, args.time, args.number, args.params1, args.params2)