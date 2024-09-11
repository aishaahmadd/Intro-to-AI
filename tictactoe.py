import numpy as np
import pickle

BOARD_ROWS = 3
BOARD_COLS = 3

class State:
    def __init__(self, p1, p2): # p1 = minmax or alphabeta player, p2 = human player
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        # init p1 plays first
        self.playerSymbol = 1
    
    # get unique hash of current board state
    def getHash(self):
        self.boardHash = str(self.board.reshape(BOARD_COLS*BOARD_ROWS))
        return self.boardHash
    
    # returns -1 is p2 wins, 1 if p1 wins and 0 for tie and sets isEnd to True
    def winner(self):
        # row
        for i in range(BOARD_ROWS):
            if sum(self.board[i, :]) == 3:
                self.isEnd = True
                return 1
            if sum(self.board[i, :]) == -3:
                self.isEnd = True
                return -1
        # col
        for i in range(BOARD_COLS):
            if sum(self.board[:, i]) == 3:
                self.isEnd = True
                return 1
            if sum(self.board[:, i]) == -3:
                self.isEnd = True
                return -1
        # diagonal
        diag_sum1 = sum([self.board[i, i] for i in range(BOARD_COLS)])
        diag_sum2 = sum([self.board[i, BOARD_COLS-i-1] for i in range(BOARD_COLS)])
        if (diag_sum1 == 3 or diag_sum2 == 3):
            self.isEnd  = True
            return 1
        elif (diag_sum1 == -3 or diag_sum2 == -3):
            self.isEnd  = True
            return -1
        
        # tie
        # no available positions
        if len(self.availablePositions()) == 0:
            self.isEnd = True
            return 0
        # not end
        self.isEnd = False
        return None
    
    def availablePositions(self):
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if self.board[i, j] == 0:
                    positions.append((i, j))  # need to be tuple
        return positions
    
    def updateState(self, position):
        self.board[position] = self.playerSymbol
        # switch to another player
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1
    
    # only when game ends
    def giveReward(self):
        result = self.winner()
        # backpropagate reward
        if result == 1:
            self.p1.feedReward(1)
            self.p2.feedReward(-1)  # was -1
        elif result == -1:
            self.p1.feedReward(-1)  # was -1
            self.p2.feedReward(1)
        else:
            self.p1.feedReward(0.1)  # was 0.1
            self.p2.feedReward(0.5) # was 0.5
    
    # board reset
    def reset(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 1
    

    # minmax play player1 = minmax/alphabeta, player = human
    def play_against_human(self):
        while not self.isEnd:
                # Player 1
                p1_action = self.p1.chooseAction(self.board, self.playerSymbol)
                # take action and upate board state
                self.updateState(p1_action)
                # check board status if it is end
                self.showBoard()

                win = self.winner()
                if win is not None:     
                    if win == 1:
                        print("Minmax/alphabeta wins")
                    elif win == -1:
                        print("Human wins")
                    else:
                        print("Tie")
                    self.reset() # starts a new game
                
                # player 2 = human
                positions = self.availablePositions()
                p2_action = self.p2.chooseAction(positions)
                self.updateState(p2_action)
                self.showBoard()

                win = self.winner()
                if win is not None:     
                    if win == 1:
                        print("Minmax wins")
                    elif win == -1:
                        print("Human wins")
                    else:
                        print("Tie")
                    self.reset()


    # plays against another RL agent
    def play(self, rounds=100):
        p1_results = {'wins':0, 'ties':0, 'losses':0}   
        p2_results =  {'wins':0, 'ties':0, 'losses':0}
        for i in range(rounds):
            if i%1000 == 0 or rounds <= 10:
                print("Rounds {}".format(i))
                print("Player 1 ", p1_results)
                print("Player 2 ", p2_results)
                p1_results = {'wins':0, 'ties':0, 'losses':0} #  
                p2_results =  {'wins':0, 'ties':0, 'losses':0}
            while not self.isEnd:
                # Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
                # take action and upate board state
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                # check board status if it is end

                win = self.winner()
                if win is not None:     
                    if win == 1:
                        p1_results['wins'] += 1
                        p2_results['losses'] +=1
                    elif win == -1:
                        p1_results['losses'] +=1
                        p2_results['wins'] += 1
                    else:
                        p1_results['ties'] +=1
                        p2_results['ties'] +=1
                    # self.showBoard()
                    # ended with p1 either win or draw
                    self.giveReward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break

                else:
                    # Player 2
                    positions = self.availablePositions()
                    p2_action = self.p2.chooseAction(positions, self.board, self.playerSymbol)
                    self.updateState(p2_action)
                    board_hash = self.getHash()
                    self.p2.addState(board_hash)
                    
                    win = self.winner()
                    if win is not None:
                        if win == 1:
                            p1_results['wins'] += 1
                            p2_results['losses'] +=1
                        elif win == -1:
                            p1_results['losses'] +=1
                            p2_results['wins'] += 1
                        else:
                            p1_results['ties'] +=1
                            p2_results['ties'] +=1
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break
    
    # play one play 
    def play2(self):
        while not self.isEnd:
            # Player 1
            positions = self.availablePositions()
            p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
            # take action and upate board state
            self.updateState(p1_action)
            self.showBoard()
            # check board status if it is end
            win = self.winner()
            if win is not None:
                if win == 1:
                    print(self.p1.name, "wins!")
                else:
                    print("tie!")
                self.reset()
                break

            else:
                # Player 2
                positions = self.availablePositions()
                p2_action = self.p2.chooseAction(positions)

                self.updateState(p2_action)
                self.showBoard()
                win = self.winner()
                if win is not None:
                    if win == -1:
                        print(self.p2.name, "wins!")
                    else:
                        print("tie!")
                    self.reset()
                    break

    def showBoard(self):
        # p1: x  p2: o
        for i in range(0, BOARD_ROWS):
            print('-------------')
            out = '| '
            for j in range(0, BOARD_COLS):
                if self.board[i, j] == 1:
                    token = 'x'
                if self.board[i, j] == -1:
                    token = 'o'
                if self.board[i, j] == 0:
                    token = ' '
                out += token + ' | '
            print(out)
        print('-------------')

from copy import deepcopy


class MinMaxPlayer:
    def __init__(self, name):
        self.name = name
        self.states = []
    
    def chooseAction(self, current_board, playerSymbol):
        # chose an action using minmax
        copy_board  = deepcopy(current_board)
        chosen_position = self.minmax(copy_board, playerSymbol)
        
    def minmax(self, current_board, playerSymbol):
        value = self.max_value(current_board)
    
    def max_value(self, current_board, playerSymbol):
        val_current = self.winner(current_board)
        if val_current != None: # val_current is a terminal state
            return val_current 
        
        # current_board is not a terminal state
        valid_positions = self.available_positions(current_board)
        value = -100
        copy_current = deepcopy(current_board)

        for pos in valid_positions:
            # update current board
            current_board[pos[0]][pos[1]] = playerSymbol
            # update player symbol 
            new_playerSymbol = (-1) * playerSymbol

            # get new valid_positions
            value = max.self(value, self.min_value(current_board,new_playerSymbol)) # current_board is passed by reference
            current_board = deepcopy(copy_current) 
        
        return value
    
    def min_value(self, current_board, playerSymbol): # model it after max_value
        val_current = self.winner(current_board)
        if val_current != None: # val_current is a terminal state
            return val_current 
        
        # current_board is not a terminal state
        valid_positions = self.available_positions(current_board)
        value = 100
        copy_current = deepcopy(current_board)

        for pos in valid_positions:
            # update current board
            current_board[pos[0]][pos[1]] = playerSymbol
            # update player symbol 
            new_playerSymbol = (-1) * playerSymbol

            # get new valid_positions
            value = min.self(value, self.min_value(current_board,new_playerSymbol)) # current_board is passed by reference
            current_board = deepcopy(copy_current) 
    def winner(board): # copy the code from State class
        # returns -1 if p2 wins, 1 if p1 wins and 0 for tie and sets isEnd to True
        # row
        for i in range(BOARD_ROWS):
            if sum(board[i, :]) == 3:
                board.isEnd = True
                return 1
            if sum(board[i, :]) == -3:
                board.isEnd = True
                return -1
        # col
        for i in range(BOARD_COLS):
            if sum(board[:, i]) == 3:
                board.isEnd = True
                return 1
            if sum(board[:, i]) == -3:
                board.isEnd = True
                return -1
        # diagonal
        diag_sum1 = sum([board[i, i] for i in range(BOARD_COLS)])
        diag_sum2 = sum([board[i, BOARD_COLS-i-1] for i in range(BOARD_COLS)])
        if (diag_sum1 == 3 or diag_sum2 == 3):
            board.isEnd  = True
            return 1
        elif (diag_sum1 == -3 or diag_sum2 == -3):
            board.isEnd  = True
            return -1
        
        # tie
        # no available positions
        if len(board.availablePositions()) == 0:
            board.isEnd = True
            return 0
        # not end
        board.isEnd = False
        return None
    def available_positions(board): # copy code from State class
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if board[i, j] == 0:
                    positions.append((i, j))  # need to be tuple
        return positions
 
class AlphaBetaPlayer:
    def __init__(self, name):
        self.name = name
        self.states = []

    
    def chooseAction(self, positions, current_board, playerSymbol):
        # chose an action using minmax
        copy_board  = deepcopy(current_board)
        chosen_position = self.minmax(copy_board, playerSymbol, -100000, 100000)
        return chosen_position
        
    def minmax(self, current_board, playerSymbol, alpha, beta):
        if playerSymbol == 1: #Max agent
            value = self.max_value(current_board, playerSymbol, alpha, beta)
        else:
            value = self.min_value(current_board, playerSymbol, alpha, beta)
        return value
    
    def max_value(self, current_board, playerSymbol, alpha, beta):
        val_current = self.winner(current_board)
        if val_current != None: # val_current is a terminal state
            return val_current 
        
        # current_board is not a terminal state
        valid_positions = self.available_positions(current_board)
        value = -100000
        copy_current = deepcopy(current_board)

        for pos in valid_positions:
            # update current board
            current_board[pos[0]][pos[1]] = playerSymbol
            # update player symbol 
            new_playerSymbol = (-1) * playerSymbol

            # get new valid_positions
            value = max.self(value, self.min_value(current_board,new_playerSymbol)) # current_board is passed by reference
            alpha = max(alpha, value)
            current_board = deepcopy(copy_current)
            if alpha >= beta: #pruning
                break
        
        return value
    
    def min_value(self, current_board, playerSymbol, alpha, beta): # model it after max_value
        val_current = self.winner(current_board)
        if val_current != None: # val_current is a terminal state
            return val_current 
        
        # current_board is not a terminal state
        valid_positions = self.available_positions(current_board)
        value = 100000
        copy_current = deepcopy(current_board)

        for pos in valid_positions:
            # update current board
            current_board[pos[0]][pos[1]] = playerSymbol
            # update player symbol 
            new_playerSymbol = (-1) * playerSymbol

            # get new valid_positions
            value = min.self(value, self.min_value(current_board,new_playerSymbol)) # current_board is passed by reference
            beta = min(beta, value)
            current_board = deepcopy(copy_current)
            if alpha >= beta:
                break
    def winner(board): # copy the code from State class
        # returns -1 if p2 wins, 1 if p1 wins and 0 for tie and sets isEnd to True
        # row
        for i in range(BOARD_ROWS):
            if sum(board[i, :]) == 3:
                board.isEnd = True
                return 1
            if sum(board[i, :]) == -3:
                board.isEnd = True
                return -1
        # col
        for i in range(BOARD_COLS):
            if sum(board[:, i]) == 3:
                board.isEnd = True
                return 1
            if sum(board[:, i]) == -3:
                board.isEnd = True
                return -1
        # diagonal
        diag_sum1 = sum([board[i, i] for i in range(BOARD_COLS)])
        diag_sum2 = sum([board[i, BOARD_COLS-i-1] for i in range(BOARD_COLS)])
        if (diag_sum1 == 3 or diag_sum2 == 3):
            board.isEnd  = True
            return 1
        elif (diag_sum1 == -3 or diag_sum2 == -3):
            board.isEnd  = True
            return -1
        
        # tie
        # no available positions
        if len(board.availablePositions()) == 0:
            board.isEnd = True
            return 0
        # not end
        board.isEnd = False
        return None
    def available_positions(board): # copy code from State class
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if board[i, j] == 0:
                    positions.append((i, j))  # need to be tuple
        return positions

class Player: # RL player
    def __init__(self, name, exp_rate=0.3):
        self.name = name
        self.states = []  # record all positions taken
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {}  # state -> value function 
    
    def getHash(self, board):
        boardHash = str(board.reshape(BOARD_COLS*BOARD_ROWS))
        return boardHash
    
    # choose action randomly with exp_rate or the optimal one given the value function in states_value
    # 
    def chooseAction(self, positions, current_board, symbol):
        if np.random.uniform(0, 1) <= self.exp_rate:
            # take random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else:
            value_max = -999
            for p in positions:
                next_board = current_board.copy()
                next_board[p] = symbol
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
                # print("value", value)
                if value >= value_max:
                    value_max = value
                    action = p
        # print("{} takes action {}".format(self.name, action))
        return action
    
    # append a hash state
    def addState(self, state):
        self.states.append(state)
    
    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        next_state = None
        for st in reversed(self.states[:-1]): # from last state to first state 
            if self.states_value.get(st) is None: 
                self.states_value[st] = 0

            if next_state == None: # last state
                delta = reward - self.states_value[st]
            else: # not the terminal state
                delta = self.decay_gamma * self.states_value[next_state] - self.states_value[st]  
            
            self.states_value[st] += self.lr* delta # (self.decay_gamma*reward - self.states_value[st])
            next_state = st
            # reward = self.states_value[st]
            
    def reset(self):
        self.states = []

    def savePolicy(self):
        SAVEPOLICY(self.name, self.states_value)

    def loadPolicy(self, file):
        self.states_value = LOADPOLICY(file)

        
class HumanPlayer:
    def __init__(self, name):
        self.name = name
        self.states = [] 
    
    def chooseAction(self, positions):
        while True:
            row = int(input("Input your action row:"))
            col = int(input("Input your action col:"))
            action = (row, col)
            if action in positions:
                return action
    
    # append a hash state
    def addState(self, state):
        self.states.append(state)
    
    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        next_state = None
        for st in reversed(self.states[:-1]): # from last state to first state 
            if self.states_value.get(st) is None: 
                self.states_value[st] = 0

            if next_state == None: # last state
                delta = reward - self.states_value[st]
            else: # not the terminal state
                delta = self.decay_gamma * self.states_value[next_state] - self.states_value[st]  
            
            self.states_value[st] += self.lr* delta # (self.decay_gamma*reward - self.states_value[st])
            next_state = st
            # reward = self.states_value[st]
            
    def reset(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 1

def SAVEPOLICY(name, states_value): 
    fw = open('policy_' + str(name), 'wb') 
    pickle.dump(states_value, fw)
    fw.close()

def LOADPOLICY(file):

    fr = open(file, 'rb')
    states_value = pickle.load(fr)
    fr.close()
    return states_value


#training

# changed reward to 1 for player 1, -1 for player
p1 = Player("p1") # , exp_rate = )
p2 = Player("p2", 1) # , exp_rate = )

st = State(p1, p2)
print("training...")
st.play(50000)

p1.exp_rate = 0
p2.exp_rate = 0
print("Check...")
st = State(p1, p2)
st.play(10)

p1.savePolicy()
p2.savePolicy()
p1.loadPolicy("policy_p1")

#RL vs MinMax
p1 = Player("RL", exp_rate=0)
p1.loadPolicy("policy_p1")
pm = MinMaxPlayer("minmax")

st= State(p1, pm)


#Human vs Computer
p1 = Player("computer", exp_rate=0)
p1.loadPolicy("policy_p1")

ph = HumanPlayer("human")

st = State(p1, ph)
st.play2()
