import numpy as np
import random
import time
import json
from collections import namedtuple
from Utility import Utility

###############################################################################
##################################  HUMAN  ####################################
###############################################################################
class HumanPlayer:
    def __init__(self, player_number):
        self.player_number = player_number
        self.type = 'human'
        self.name = 'human'
        self.player_string = 'Player {}: human'.format(player_number)

    def get_move(self, board):
        print('Available pieces::')
        pieces = get_pieces(board, self.player_number)
        print(pieces)
        r = -1
        c = -1 
        while (r < 0 or r > 7):
            r = int(input("Choose piece row:: "))
        while (c < 0 or c > 7):
            c = int(input("Choose piece column:: "))
        valid = None
        while (board[r,c] != self.player_number) and (board[r,c] != self.player_number+2):
            r = int(input('Incorrect Input, choose, piece row::'))
            c = int(input('Choose, piece col::'))
        valid = get_available_moves(board, [r,c])
        val_move = ""
        if valid != None:   
            print("Moves:: ", valid) 
            val_move = input("Choose available move:: " )
        else: 
            print("No valid moves for piece, please select another piece.")

        while val_move not in valid:
            val_move = input('Incorrect input, choose available move::')
        return val_move, [r,c]
    

###############################################################################
##################################  RANDOM  ###################################
###############################################################################
class RandomPlayer:
    def __init__(self, player_number):
        self.player_number = player_number
        self.type = 'random'
        self.name = 'random'
        self.player_string = 'Player {}: random'.format(player_number)

    def get_move(self, board):
        count = 0
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


###############################################################################
################################  PERCEPTRON  #################################
###############################################################################
class Perceptron:
    def __init__(self, ptype, name, player_number, param):
        self.player_number = player_number
        self.enum = 1 if player_number == 2 else 2
        self.name = name
        self.type = ptype
        self.player_string = 'Player {}: '.format(player_number) + self.name
        self.u = Utility(None, None, None, None, None)

        self.weights = np.random.randn(64) * 0.01
        self.bias = 0.0
        self.learning_rate = 0.01

    def get_move(self, board):
        pieces = get_pieces(board, self.player_number)
        move = None 
        piece = None
        best = -float('inf')
        for p in pieces: 
            temp_board = np.zeros([8,8]).astype(np.uint8)
            temp_board = board.copy()
            valid = get_available_moves(board, p)
            for m in valid:
                self.u.execute_move(temp_board, m, p, self.player_number)
                features = self.extract_features(board)
                print(self.weights)
                score = self.predict(features)
                if score > best:
                    best = score
                    piece = p
                    move = m
        return move, piece
    
    def predict(self, x): 
        return np.dot(x, self.weights) + self.bias
    
    def train(self, x, target):
        pred = self.predict(x)
        error = target - pred
        self.weights += self.learning_rate * error * x
        self.bias += self.learning_rate * error 

    def extract_features(self, board):
        if not isinstance(board, np.ndarray) or board.shape != (8, 8):
            raise ValueError(f"Expected 2D board with shape (8, 8), got {type(board)} with shape {getattr(board, 'shape', None)}")
        features = np.zeros(64, dtype=float)
        board_flat = board.flatten()
        features[board_flat == self.player_number] = 1
        features[board_flat == self.player_number+2] = 2  
        features[board_flat == self.enum] = -0.5
        features[board_flat == self.enum+2] = -1
        return features
    
# def save_weights(self, filename="perceptron_weights.json"):
#     with open(filename, 'w') as f:
#         json.dump({'weights': self.weights.tolist(), 'bias': float(self.bias)}, f)
#         print(f"Weights saved to {filename}")

# def load_weights(self, filename="perceptron_weights.json"):
#     try:
#         with open(filename, 'r') as f:
#             data = json.load(f)
#             self.weights = np.array(data['weights'])
#             self.bias = data['bias']
#         print(f"Weights loaded from {filename}")
#     except FileNotFoundError:
#         print(f"File {filename} not found.")
#     except Exception as e:
#         print(f"Error loading weights: {e}")
        

###############################################################################
###################################  MCTS  ####################################
###############################################################################
class AIPlayer:
    def func(): 
        return

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



###############################################################################
##############################  UTIL FUNCTIONS  ###############################
###############################################################################

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