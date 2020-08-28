import numpy as np


def check_full(n, game_board):
    for i in range(n):
        for j in range(n):
            if (game_board[i][j] == "."):
                return False
    return True

def is_goal(n, game_board, turn):
    player = ""
    if (turn == "1"):
        player = "X"
    elif (turn == "2"):
        player = "O"
    # diagonal
    count_1 = 0
    for i in range(n):
        if (player == game_board[i][i]):
            count_1 += 1
    if (count_1 == n):
        return player
    # horizontal
    for i in range(n):
        count_2 = 0
        for j in range(n):
            if (game_board[i][j] == player):
                count_2 += 1
        if (count_2 == n):
            return player
    # vertical
    for i in range(n):
        count_3 = 0
        for j in range(n):
            if (game_board[j][i] == player):
                count_3 += 1
        if (count_3 == n):
            return player
    # reverse_diagonal
    count_4 = 0
    for i in range(n):
        if (game_board[i][(n-1)-i] == player):
            count_4 += 1
    if (count_4 == n):
        return player
    return "continue"


def game(n, game_board, turn):
    player = ""
    if (turn == "1"):
        player = "X"
    elif (turn == "2"):
        player = "O"
    chosen_box_x, chosen_box_y = eval(input("insert your box number:(in pair) "))
    if (game_board[chosen_box_x][chosen_box_y] == "."):
        game_board[chosen_box_x][chosen_box_y] = player
    else:
        while (game_board[chosen_box_x][chosen_box_y] != "."):
            chosen_box_x, chosen_box_y = eval(input("insert your box number:(in pair) "))
        game_board[chosen_box_x][chosen_box_y] = player
    result = is_goal(n,game_board,turn)
    if (check_full(n,game_board) == True and result == "continue"):
        return "D",game_board,chosen_box_x, chosen_box_y
    if (result == "X"):
        return "1",game_board,chosen_box_x, chosen_box_y
    elif (result == "O"):
        return "2",game_board,chosen_box_x, chosen_box_y
    else:
        return "C",game_board,chosen_box_x, chosen_box_y