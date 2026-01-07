"""
Tic Tac Toe Player
"""

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    total_X = 0
    total_O = 0
    
    for i in range(3):
        for j in range(3):
            value = board[i][j]
            if value == X:
                total_X += 1
            elif value == O:
                total_O += 1
    
    if total_X <= total_O:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    all_actions = set()
    
    for i in range(3):
        for j in range(3):
            value = board[i][j]
            if value == EMPTY:
                all_actions.add((i, j))
                
    return all_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = []
    for row in board:
        new_board.append(row.copy())
    try:
        i = action[0]
        j = action[1]
        new_board[i][j] = player(board)
    except Exception:
        print(i, j)
    
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """    
    
    for i in range(3):
        # Line Win
        if board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
        
        # Column Win
        if board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]
        
    # Diagonal win
    diagonal_1 = (board[0][0] == board[1][1] == board[2][2])
    diagonal_2 = (board[0][2] == board[1][1] == board[2][0])
    if diagonal_1 or diagonal_2:
        return board[1][1]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    
    for row in board:
        if EMPTY in row:
            return False
    
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winner_value = winner(board)
    if winner_value == X:
        return 1
    elif winner_value == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if player(board) == X:
        player_func = max_value
    else:
        player_func = min_value
    
    _, best_action = player_func(board)
    return best_action

def max_value(board):
    if terminal(board):
        return utility(board), None
    
    best_value = float("-inf")
    best_action = None
    for action in actions(board):
        new_value, _ = min_value(result(board, action))
        if new_value > best_value:
            best_value = new_value
            best_action = action
    
    return best_value, best_action
 
def min_value(board):
    if terminal(board):
        return utility(board), None
    
    best_value = float("inf")
    best_action = None
    for action in actions(board):
        new_value, _ = max_value(result(board, action))
        if new_value < best_value:
            best_value = new_value
            best_action = action
    
    return best_value, best_action
    

