#Modified 10.3.2023 by Chris Archibald to
#  - incorporate MCTS with other code
#  - pass command line param string to each AI
import random

import numpy as np
import time
from collections import namedtuple


class RandomPlayer:
    def __init__(self, player_number):
        self.player_number = player_number
        self.type = 'random'
        self.name = 'random'
        self.player_string = 'Player {}: random'.format(player_number)

    def get_move(self, board):
        """
        Given the current board state select a random column from the available
        valid moves.

        INPUTS:
        board - a numpy array containing the state of the board using the
                following encoding:
                - the board maintains its same two dimensions
                    - row 0 is the top of the board and so is
                      the last row filled
                - spaces that are unoccupied are marked as 0
                - spaces that are occupied by player 1 have a 1 in them
                - spaces that are occupied by player 2 have a 2 in them

        RETURNS:
        The 0 based index of the column that represents the next move
        """

        count = 1
        while count > 0:
            time.sleep(.1)
            count -=1

        pieces = get_pieces(board, self.player_number)
        while True:
            rand = random.choice(pieces)
            r = int(rand[0])
            c = int(rand[1])
            valid = get_available_moves(board, [r,c])
            print('HERE::: r:', r, 'c:', c, 'VAL::', valid)
            if valid:
                break
        val_move = random.choice(valid)
        print('MOVE::', val_move)
        return val_move, [r,c]

class HumanPlayer:
    def __init__(self, player_number):
        self.player_number = player_number
        self.type = 'human'
        self.name = 'human'
        self.player_string = 'Player {}: human'.format(player_number)

    def get_move(self, board):
        """
        Given the current board state returns the human input for next move

        INPUTS:
        board - a numpy array containing the state of the board using the
                following encoding:
                - the board maintains its same two dimensions
                    - row 0 is the top of the board and so is
                      the last row filled
                - spaces that are unoccupied are marked as 0
                - spaces that are occupied by player 1 have a 1 in them
                - spaces that are occupied by player 2 have a 2 in them

        RETURNS:
        The 0 based index of the column that represents the next move
        """

        print('Available pieces::')
        pieces = get_pieces(board, self.player_number)
        print(pieces)
        r = int(input('Choose piece row:: '))
        c = int(input('Choose piece colum:: '))
        while board[r,c] != self.player_number:
            r = int(input('Incorrect Input, choose, piece row::'))
            c = int(input('Choose, piece col::'))

        print('Available moves::')
        valid = get_available_moves(board, [r,c])
        print(valid)
        val_move = input('Choose available move::')
        while val_move not in valid:
            val_move = input('Incorrect input, choose available move::')
        return val_move, [r,c]


class AIPlayer:
    def __init__(self, player_number, name, ptype, param):
        self.player_number = player_number
        self.name = name
        self.type = ptype
        self.player_string = 'Player {}: '.format(player_number) + self.name
        self.other_player_number = 1 if player_number == 2 else 2

        # MCTS
        self.max_iterations = 1000  # Default max-iterations for MCTS - change if you desire
        # Example of using command line param to overwrite max-iterations for MCTS
        if self.type == 'mcts' and param:
            self.max_iterations = int(param)

    def get_mcts_move(self, board):
        """
        Use MCTS to get the next move
        """
        # How many iterations of MCTS will we do?
        max_iterations = 10

        # Make the MCTS root node from the current board state
        root = MCTSNode(board, self.player_number, None, None)

        # Run our MCTS iterations
        for i in range(max_iterations):
            # Select + Expand
            cur_node = root.select()
            # Simulate + backpropate
            cur_node.simulate()
            print(cur_node.board)

        # Print out the info from the root node
        root.print_node()
        print('MCTS chooses action', root.max_child())
        return root.max_child()


#CODE FOR MCTS 
class MCTSNode:
    def __init__(self, board, player_number, parent, piece):
        self.board = board
        self.player_number = player_number
        self.other_player_number = 1 if player_number == 2 else 2
        self.parent = parent
        self.piece = piece
        self.pieces = get_pieces(board, self.player_number)
        self.o_pieces = get_pieces(board, self.other_player_number)
        self.terminal = (len(self.pieces) == 0 or len(self.o_pieces) == 0)
        self.moves = get_available_moves(board, piece)
        # for i in self.pieces:
        #     i_moves = get_available_moves(board,i)
        #     for j in i_moves:
        #         self.moves.append([i, i_moves[j]])
        # self.o_moves = []
        # for i in self.o_pieces:
        #     i_moves = get_available_moves(board, i)
        #     for j in i_moves:
        #         self.moves.append([i, i_moves[j]])
        self.children = dict()
        if self.piece:
            for m in self.moves:
                m = digitize(m)
                self.children[m] = None
        else:
            for m in range(4):
                self.children[m] = None

        #Set up stats for MCTS
        #Number of visits to this node
        self.n = 0 

        #Total number of wins from this node (win = +1, loss = -1, tie = +0)
        # Note: these wins are from the perspective of the PARENT node of this node
        #       So, if self.player_number wins, that is -1, while if self.other_player_number wins
        #       that is a +1.  (Since parent will be using our UCB value to make choice)
        self.w = 0 

        #c value to be used in the UCB calculation
        self.c = .01
    

    def print_tree(self):
        #Debugging utility that will print the whole subtree starting at this node
        print("****")
        self.print_node()
        for m in self.moves:
            if self.children[m]:
                self.children[m].print_tree()
        print("****")

    def print_node(self):
        #Debugging utility that will print this node's information
        print('Total Node visits and wins: ', self.n, self.w)
        print('Children: ')
        for m in self.moves:
            if self.children[m] is None:
                print('   ', m, ' is None')
            else:
                print('   ', m, ':', self.children[m].n, self.children[m].w, 'UB: ', self.children[m].upper_bound(self.n))

    def max_child(self):
        #Return the most visited child
        #This is used at the root node to make a final decision
        max_n = 0
        max_m = None
        # print("TREE::",self.print_tree())
        # print("SAMPLING::", self.n, self.w)
        for m in self.moves:
            if self.children[m].n > max_n:
                max_n = self.children[m].n
                max_m = m
        return max_m

    def upper_bound(self, N):
        #This function returns the UCB for this node
        #N is the number of samples for the parent node, to be used in UCB calculation
        # print("N::", self.n, ", W::", self.w)
        # self.print_node()
        ucb = (self.w / self.n) + (self.c * (np.sqrt(np.log(N) / self.n)))
        #To do: return the UCB for this node (look in __init__ to see the values you can use)
        return ucb

    def select(self):
        #This recursive function combines the selection and expansion steps of the MCTS algorithm
        #It will return either: 
        # A terminal node, if this is the node selected
        # The new node added to the tree, if a leaf node is selected

        max_ub = -np.inf  #Track the best upper bound found so far
        max_child = None  #Track the best child found so far
        max_move = None

        if self.terminal:
            #If this is a terminal node, then return it (the game is over)
            # print("HERE:::")
            return self

        # For all of the children of this node
        for p in get_pieces(self.board, self.player_number):
            for m in get_available_moves(self.board, p):
                m = digitize(m)
                if self.children[m] is None:

                    # If this child doesn't exist, then create it and return it
                    new_board = ai_move(np.copy(self.board),p,m,self.player_number) # Make the move in the state
                    self.children[m] = MCTSNode(new_board, self.other_player_number, self, p) #Create the child node
                    return self.children[m] # Return it

                # Child already exists, get it's UCB value
                # print("TERMINAL?::", self.terminal)
                current_ub = self.children[m].upper_bound(self.n)
                # Compare to previous best UCB
                if current_ub > max_ub:
                    max_ub = current_ub
                    max_child = p
                    max_move = m

        #Recursively return the select result for the best child 
        return self.children[max_move].select()


    def simulate(self):
        #This function will simulate a random game from this node's state and then call back on its 
        #parent with the result
        if len(self.o_pieces) == 0:
            self.terminal = True
            return 1
        elif len(self.pieces) == 0:
            self.terminal = True
            return -1
        result = self.rollout(self.board, self.player_number)
        if result != 0:
            self.terminal = True
        self.parent.back(result)
        return result

        # Pseudocode in comments:
        #################################
        # If this state is terminal (meaning the game is over) AND it is a winning state for self.other_player_number
        #   Then we are done and the result is 1 (since this is from parent's perspective)
        #
        # Else-if this state is terminal AND is a winning state for self.player_number
        #   Then we are done and the result is -1 (since this is from parent's perspective)
        #
        # Else-if this is not a terminal state (if it is terminal and a tie (no-one won, then result is 0))
        #   Then we need to perform the random rollout
        #      1. Make a copy of the board to modify
        #      2. Keep track of which player's turn it is (first turn is current nodes self.player_number)
        #      3. Until the game is over: 
        #            3.1  Make a random move for the player who's turn it is
        #            3.2  Check to see if someone won or the game ended in a tie 
        #                 (Hint: you can check for a tie if there are no more valid moves)
        #            3.3  If the game is over, store the result
        #            3.4  If game is not over, change the player and continue the loop
        #
        # Update this node's total reward (self.w) and visit count (self.n) values to reflect this visit and result


        # Back-propagate this result
        # You do this by calling back on the parent of this node with the result of this simulation
        #    This should look like: self.parent.back(result)
        # Tip: you need to negate the result to account for the fact that the other player
        #    is the actor in the parent node, and so the scores will be from the opposite perspective

    def rollout(self, board, player):
        p = player
        temp = np.copy(board)
        result = 0
        while True:
            pieces = get_pieces(board, self.player_number)
            o_pieces = get_pieces(board, self.other_player_number)
            piece = []
            move = []
            if p == self.player_number:
                while move is None:
                    piece = random.choice(pieces)
                    move = random.choice(get_available_moves(temp, piece))
                temp = ai_move(temp, piece, move, p)
            else:
                while move is None:
                    piece = random.choice(o_pieces)
                    move = random.choice(get_available_moves(temp, piece))
                temp = ai_move(temp, piece, move, p)

            if len(pieces) == 0 or len(o_pieces) == 0:
                print('HERE::YEEHAW')
                if len(self.o_pieces) == 0: result = 1
                elif len(self.pieces) == 0: result = -1
                self.terminal = True
                break
            else:
                p = self.player_number if p == self.other_player_number else self.other_player_number
                continue
        self.n += 1
        self.w += result
        return result

    def back(self, score):
        #This updates the stats for this node, then backpropagates things 
        #to the parent (note the inverted score)
        self.n += 1
        self.w += score
        if self.parent is not None:
            self.parent.back(-score) #Score inverted before passing along


#UTILITY FUNCTIONS

def digitize(move):
    if move == 'ne':
        return 0
    if move == 'nw':
        return 1
    if move == 'se':
        return 2
    if move == 'sw':
        return 3

def get_pieces(board, p):
    pieces = []
    # print(board)
    for r in range(board.shape[0]):
        for c in range(board.shape[1]):
            if (board[r,c] == p) or (board[r,c] == p+2):
                pieces.append([r,c])
    return pieces

def get_available_moves(board, piece):
    valid = []
    # print(board)
    if not piece:
        return None

    # SE (+,+)
    if (piece[0]+1 <= 7 and piece[1]+1 <= 7) and (board[piece[0]][piece[1]] != 1): 
        if board[piece[0]+1][piece[1]+1] == 0:
            valid.append('se')
        elif piece[0]+2 <= 7 and piece[1]+2 <= 7 and board[piece[0]+1][piece[1]+1] != board[piece[0]][piece[1]]:
            if board[piece[0]+2][piece[1]+2] == 0:
                valid.append('se')

    # SW (+,-)
    if (piece[0]+1 <= 7 and piece[1]-1 >= 0) and (board[piece[0]][piece[1]] != 1):
        if board[piece[0]+1][piece[1]-1] == 0:
            valid.append('sw')
        elif piece[0]+2 <= 7 and piece[1]-2 >= 0  and board[piece[0]+1][piece[1]-1] != board[piece[0]][piece[1]]:
            if board[piece[0]+2][piece[1]-2] == 0:
                valid.append('sw')

    # NE (-,+)
    if (piece[0]-1 >= 0 and piece[1]+1 <= 7) and (board[piece[0]][piece[1]] != 2):
        if board[piece[0]-1][piece[1]+1] == 0:
            valid.append('ne')
        elif piece[0] - 2 <= 7 and piece[1] + 2 <= 7  and board[piece[0]-1][piece[1]+1] != board[piece[0]][piece[1]]:
            if board[piece[0]-2][piece[1]+2] == 0:
                valid.append('ne')

    # NW (-,-)
    if (piece[0]-1 >= 0 and piece[1]-1 >= 0) and (board[piece[0]][piece[1]] != 2):
        if board[piece[0]-1][piece[1]-1] == 0:
            valid.append('nw')
        elif piece[0]-2 <= 7 and piece[1]-2 <= 7  and board[piece[0]-1][piece[1]-1] != board[piece[0]][piece[1]]:
            if board[piece[0]-2][piece[1]-2] == 0:
                valid.append('nw')

    # NONE?
    if valid is None:
        print("No valid moves, choose a different piece.")
    return valid

#This function will modify the board according to 
#player_number moving into move column
def ai_move(board, piece, move, player_number):
    # piece = mv[0]
    # move = mv[1]
    other_player = 2 if player_number == 1 else 1
    if move is not None:  # Remove attacked piece???
        if move == 'se':
            if board[piece[0] + 1][piece[1] + 1] == other_player and board[piece[0] + 2][piece[1] + 2] == 0:
                board = update(board, [2, 2], piece, player_number)
                board = update(board, [0, 0], [piece[0] + 1, piece[1] + 1], other_player)
            else:
                board = update(board, [1, 1], piece, player_number)
        if move == 'sw':
            if board[piece[0] + 1][piece[1] - 1] == other_player and board[piece[0] + 2][piece[1] - 2] == 0:
                board = update(board, [2, -2], piece, player_number)
                board = update(board, [0, 0], [piece[0] + 1, piece[1] - 1], other_player)
            else:
                board = update(board, [1, -1], piece, player_number)
        if move == 'ne':
            if board[piece[0] - 1][piece[1] + 1] == other_player and board[piece[0] - 2][piece[1] + 2] == 0:
                board = update(board, [-2, 2], piece, player_number)
                board = update(board, [0, 0], [piece[0] - 1, piece[1] + 1], other_player)
            else:
                board = update(board, [-1, 1], piece, player_number)
        if move == 'nw':
            if board[piece[0] - 1][piece[1] - 1] == other_player and board[piece[0] - 2][piece[1] - 2] == 0:
                board = update(board, [-2, -2], piece, player_number)
                board = update(board, [0, 0], [piece[0] - 1, piece[1] - 1], other_player)
            else:
                board = update(board, [-1, -1], piece, player_number)
        return board


def update(board, move, piece, p):
    if move:
        if move == [0,0]:
            board[piece[0]][piece[1]] = 0
        else:
            board[piece[0]+move[0]][piece[1]+move[1]] = p
            board[piece[0]][piece[1]] = 0
    else:
        board[piece[0]][piece[1]] = p
    return board



#This function will return a list of valid moves for the given board
# def get_valid_moves(board):
#     valid_moves = []
#     for c in range(7):
#         if 0 in board[:,c]:
#             valid_moves.append(c)
#     return valid_moves

#This function returns true if player_num is winning on board
# def is_winning_state(board, player_num):
#     # player_win_str = '{0}{0}{0}{0}'.format(player_num)
#     # to_str = lambda a: ''.join(a.astype(str))
#     #
#     # def check_horizontal(b):
#     #     for row in b:
#     #         if player_win_str in to_str(row):
#     #             return True
#     #     return False
#     #
#     # def check_verticle(b):
#     #     return check_horizontal(b.T)
#     #
#     # def check_diagonal(b):
#     #     for op in [None, np.fliplr]:
#     #         op_board = op(b) if op else b
#     #
#     #         root_diag = np.diagonal(op_board, offset=0).astype(int)
#     #         if player_win_str in to_str(root_diag):
#     #             return True
#     #
#     #         for i in range(1, b.shape[1]-3):
#     #             for offset in [i, -i]:
#     #                 diag = np.diagonal(op_board, offset=offset)
#     #                 diag = to_str(diag.astype(int))
#     #                 if player_win_str in diag:
#     #                     return True
#     #
#     #     return False
#     #
#     # return (check_horizontal(board) or
#     #         check_verticle(board) or
#     #         check_diagonal(board))

