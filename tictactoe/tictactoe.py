"""
Tic Tac Toe Player
"""

import copy
import math

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
    x_count = 0
    o_count = 0
    for row in board:
        for tile in row:
            if tile == X:
                x_count += 1
            elif tile == O:
                o_count += 1
    if x_count == o_count:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    valid_actions = actions(board)
    if action not in valid_actions:
        print(f"ERROR!!!! attempted action {action} on board {board}")
        raise RuntimeError("Invalid Action!")

    curr_player = player(board)
    new_board = copy.deepcopy(board)
    i, j = action

    new_board[i][j] = curr_player
    # print(f"made new board {new_board} from previous state {board} and action {action}")
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check rows and columns
    for i in range(3):
        # check row
        check_row = set()
        # add row to a set to check if they are not EMPTY and identical
        for cell in board[i]:
            check_row.add(cell)
            # all cells in the column contain the same tile --> return if not EMPTY
        if len(check_row) == 1:
            tile = check_row.pop()
            if not tile == EMPTY:
                return tile

        # check column
        check_col = set()
        for row in board:
            cell = row[i]
            check_col.add(cell)
        # all cells in the column contain the same tile --> return if not EMPTY
        if len(check_col) == 1:
            tile = check_col.pop()
            if not tile == EMPTY:
                return tile

    # check diagonal
    forward_diagonal = set()
    for i in range(3):
        cell = board[i][i]
        forward_diagonal.add(cell)
    if len(forward_diagonal) == 1:
        tile = forward_diagonal.pop()
        if not tile == EMPTY:
            return tile
    
    back_diagonal = set()
    back_diagonal_cells = [board[0][2], board[1][1], board[2][0]]
    for cell in back_diagonal_cells:
        back_diagonal.add(cell)
    if len(back_diagonal) == 1:
        tile = back_diagonal.pop()
        if not tile == EMPTY:
            return tile
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # check winner
    if not winner(board) == EMPTY:
        return True
    
    # check full
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winning_player = winner(board)
    if winning_player == X:
        return 1
    elif winning_player == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None
    
    curr_player = player(board)
    if curr_player == X:
        _, action = max_value(board)
        return action
    else:
        _, action = min_value(board)
        return action


def max_value(board):
    value = float('-inf')
    opt_action = None

    if terminal(board):
        return (utility(board), None)

    possible_actions = actions(board)
    for action in possible_actions:
        # print(f"attempting action: {action} in MAX FUNCTION")
        v, _ = min_value(result(board, action))
        if v >= value:
            value = v
            opt_action = action
    return (value, opt_action)


def min_value(board):
    value = float('inf')
    opt_action = None

    if terminal(board):
        return (utility(board), None)

    possible_actions = actions(board)
    for action in possible_actions:
        # print(f"attempting action: {action} in MIN FUNCTION")
        v, _ = max_value(result(board, action))
        if v < value:
            value = v
            opt_action = action
    return (value, opt_action)