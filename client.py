import socket
import select
import errno
import sys
import game
import numpy as np

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

my_username = input("Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
# client_socket.setblocking(False)

status = input("1. play 2. wait")

username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(username_header + username)

status_2 = status.encode("utf-8")
status_header = f"{len(status_2):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(status_header + status_2)

header_onlineplayer = client_socket.recv(HEADER_LENGTH)
header_length_onlineplayer = int(header_onlineplayer.decode("utf-8").strip())
online_player = client_socket.recv(header_length_onlineplayer).decode("utf-8")

print(f"online players: {online_player}")

def start_game(game_board, board_dimension, turn):

    while True:
        result, game_board, chosen_box_x, chosen_box_y = game.game(board_dimension, game_board,turn)
        # send
        msg_chosen_action = (result + f"{chosen_box_x}{chosen_box_y}" + f"{turn}" + f"{board_dimension}").encode("utf-8")
        msg_chosen_action_header = f"{len(msg_chosen_action):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(msg_chosen_action_header + msg_chosen_action)

        # receive
        server_response_header = client_socket.recv(HEADER_LENGTH)
        server_response_header = int(server_response_header.decode("utf-8").strip())
        server_response = client_socket.recv(server_response_header).decode("utf-8")

        if (server_response == "W"):
            print("You won!")
            sys.exit()
        elif (server_response == "T"):
            print("Time exceeded!")
            sys.exit()
        elif (server_response == "L"):
            print("You lost!")
            sys.exit()
        elif (server_response == "D"):
            print("Draw!")
            sys.exit()

        result = server_response[0]
        chosen_box_x = eval(server_response[1])
        chosen_box_y = eval(server_response[2])
        turn = server_response[3]

        print(result)
        print(chosen_box_x,chosen_box_y)
        print(turn)
        
        if (turn == "1"):
            game_board[chosen_box_x][chosen_box_y] = "O"
        elif (turn == "2"):
            game_board[chosen_box_x][chosen_box_y] = "X"        
        
        print(game_board)

while True:
    # COMMAND: Sending request
    if (status == "1"):
        if (online_player != "No Online Player!"):
            rival = input("insert player you want to play with: ")
            if rival in online_player:
                client_socket.send((f"{len(rival):<{HEADER_LENGTH}}" + rival).encode("utf-8"))
                # receiving the request response
                request_response_header = client_socket.recv(HEADER_LENGTH)
                request_response_header = int(request_response_header.decode("utf-8").strip())
                request_response = client_socket.recv(request_response_header).decode("utf-8")

                if (request_response == "yes"):
                    print("Your request has been accepted!")

                    # COMMAND: initializing the game
                    print("** The game started **")
                    result = ""
                    board_dimension = eval(input("insert the board size: "))
                    game_board = np.zeros((board_dimension,board_dimension), dtype = str)
                    for i in range (board_dimension):
                        for j in range(board_dimension):
                            game_board[i][j] = "."
                    start_game(game_board, board_dimension,"1")

                elif (request_response == "no"):
                    print("Your request has been denied!")
            else:
                print("wrong username!")
                sys.exit()
        
    # COMMAND: Accepting the game request
    header_length_secondplayer = client_socket.recv(HEADER_LENGTH)
    header_length_secondplayer = int(header_length_secondplayer.decode("utf-8").strip())
    accept_rival_request = client_socket.recv(header_length_secondplayer).decode("utf-8")
    print(accept_rival_request)
    # sending the acceptance of the request (from another player)
    msg_response = input("insert yes or no! ")
    msg_response_2 = f"{len(msg_response):<{HEADER_LENGTH}}" + msg_response
    client_socket.send(msg_response_2.encode("utf-8"))

    # receive from server
    header_server_response = client_socket.recv(HEADER_LENGTH)
    header_server_response = int(header_server_response.decode("utf-8").strip())
    server_response = client_socket.recv(header_server_response).decode("utf-8")

    # build the game board
    chosen_box_x = eval(server_response[1])
    chosen_box_y = eval(server_response[2])
    turn = server_response[3]
    board_dimension = eval(server_response[4])
    game_board = np.zeros((board_dimension,board_dimension), dtype = str)
    for i in range (board_dimension):
        for j in range(board_dimension):
            if (i == chosen_box_x and j == chosen_box_y):
                game_board[i][j] = "X"
            else:
                game_board[i][j] = "."
    start_game(game_board, board_dimension,turn)
    
    
