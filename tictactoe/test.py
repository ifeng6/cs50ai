from tictactoe import player, minimax, result

X = "X"
O = "O"
EMPTY = None

board = [[EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY]]

next_X_board = [[EMPTY, O, EMPTY],
                [EMPTY, X, EMPTY],
                [EMPTY, EMPTY, EMPTY]]

next_O_board = [[EMPTY, EMPTY, EMPTY],
                [EMPTY, X, EMPTY],
                [EMPTY, EMPTY, EMPTY]]

# print(f"should be X: {player(next_X_board)}")
# print(f"should be O: {player(next_O_board)}")

result_board = [[EMPTY, EMPTY, EMPTY],
                [EMPTY, X, EMPTY],
                [EMPTY, EMPTY, EMPTY]]
action = (0, 2)
# print(result(result_board, action))

minimax_board = [[EMPTY, EMPTY, O],
                [O, X, X],
                [X, O, X]]

print(minimax(minimax_board))
