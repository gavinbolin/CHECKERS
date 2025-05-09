#Modified 10.3.2023 by Chris Archibald to
#  - run multiple experiments automatically
#  - incorporate MCTS with other code
#  - pass command line param string to each AI
#  - bypass tkinter when it doesn't exist, as that has proven problematic for some users

# TODO
# - ability to cancel selection of piece if it doesnt have any moves
# - track and update queen pieces

import argparse
import multiprocessing as mp
import numpy as np
try:
    import tkinter as tk
    from tkinter import *
    graphics = True
except ImportError as err:
    graphics = False

from Player import HumanPlayer, RandomPlayer, Perceptron, AIPlayer
from Utility import Utility

#https://stackoverflow.com/a/37737985
def turn_worker(board, send_end, p_func):
    send_end.send(p_func(board))

#List of symbols 
symbols = ['.', 'X', 'O']


###############################################################################
###################################  GAME  ####################################
###############################################################################
class Game:
    def __init__(self, player1, player2, time, interactive):
        self.players = [player1, player2]
        self.colors = ['blue', 'red', 'purple', 'orange', 'gray']
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
            graphics = True

        if graphics:  #https://stackoverflow.com/a/38159672
            root = tk.Tk()
            root.title('CHECKERS')
            self.player_string = tk.Label(root, text=player1.player_string)
            self.player_string.pack()
            self.c = tk.Canvas(root, width=400, height=400)
            self.c.pack()
            self.u = Utility(interactive, graphics, self.c, self.gui_board, self.colors)

            for row in range(0, 400, 50):
                column = []
                for col in range(0, 400, 50):
                    column.append(self.c.create_oval(row, col, row+50, col+50, fill=''))
                self.gui_board.append(column)

            # tk.Button(root, text='Next', command=self.make_move).pack() #remove, use only terminal..?
            self.start_state()
            self.make_move()
            root.mainloop()
        else:
            self.u = Utility(interactive, graphics, None, self.gui_board, self.colors)
            if interactive:
                self.u.print_board(self.board)
            self.start_state()
            self.gameloop()


    def start_state(self):
        # create start state of board
        for i in range(0,8,2):
            self.u.update_board(self.board, None, [0,i], 2)
            self.u.update_board(self.board, None, [1,i+1], 2)
            self.u.update_board(self.board, None, [2,i], 2)
            self.u.update_board(self.board, None, [3,i+1],0)
            self.u.update_board(self.board, None, [4,i],0)
            self.u.update_board(self.board, None, [5,i+1], 1)
            self.u.update_board(self.board, None, [6,i], 1)
            self.u.update_board(self.board, None, [7,i+1], 1)


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
                move, piece = current_player.get_move(self.board) # doesnt work for random??  # removed attribute self.g from params
            self.u.execute_move(self.board, move, piece, current_player.player_number)

            if self.game_won(current_player.player_number):   # Determine game state (WIN/LOSS/TIE)
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
            else:
                self.current_turn = int(not self.current_turn)
                if graphics:
                    self.player_string.configure(text=self.players[self.current_turn].name)
                    self.make_move()
                else:
                    print('Current Turn: ', self.players[self.current_turn].name, '  using symbol : ', symbols[self.players[self.current_turn].player_number])

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
        if (player_num in self.board or player_num+2 in self.board) and (other not in self.board and other+2 not in self.board):
            return True
        else:
            return False


def play_game(player1name, player2name, player1, player2, time, params1, params2, interactive, stats):
    """
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
        elif method=='perc':
            return Perceptron(name, method, num, params)

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
    if n == 1 or 'human' in pnames or 'random' in pnames or 'perc' in pnames:
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
    player_types = ['ab', 'random', 'human', 'mcts', 'expmax', 'perc']
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



###############################################################################
###################################  UTIL  ####################################
###############################################################################
