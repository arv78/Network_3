import socket
import select
import pickle
import game
import time
import sys

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# for the port problem
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# COMMAND: Initializing
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
# a dic. for clients
online_player = {}

def receive_message(client_socket):
    try:
        # receive from
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            # COMMAND : Accepting connection 
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            
            status_header = client_socket.recv(HEADER_LENGTH)
            status_length = int(status_header.decode("utf-8").strip())
            status = client_socket.recv(status_length).decode("utf-8")
            
            if user is False:
                continue

            # adding the online player
            sockets_list.append(client_socket)
            online_player[client_socket] = user

            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}")

            # COMMAND: Showing online players
            if (len(online_player) > 1):
                temp_dic = []
                for _, value in online_player.items():
                    temp_dic.append(value)
                for i in range(len(temp_dic)):
                    temp_dic[i] = temp_dic[i]['data'].decode("utf-8")

                length_usernames = 0
                for i in range(len(temp_dic)):
                    length_usernames += len(temp_dic[i])
                msg = f"{length_usernames + (len(temp_dic) * 2):<{HEADER_LENGTH}}"
                for i in range(len(temp_dic)):
                    msg  += temp_dic[i] + ", "

                client_socket.send(msg.encode("utf-8"))
            else:
                msg = "No Online Player!"
                msg = f"{len(msg):<{HEADER_LENGTH}}" + msg
                client_socket.send(msg.encode("utf-8"))
            
            # COMMAND: Sending request
            if (status == "1"):
                if (len(online_player) > 1):
                    rival_request = receive_message(client_socket)
                    
                    for key, value in online_player.items():
                        print("***wtf!***")
                        if (value['data'].decode("utf-8") == rival_request['data'].decode("utf-8")):
                            msg = f"player: {(online_player[client_socket]['data']).decode('utf-8')} wants to play with you!"
                            msg = f"{len(msg):<{HEADER_LENGTH}}" + msg
                            key.send(msg.encode("utf-8"))
                            # COMMAND: Initializing game
                            response = receive_message(key)
                            if (response['data'].decode("utf-8") == "yes"):
                                msg_ = "yes"
                                msg_ = f"{len(msg_):<{HEADER_LENGTH}}" + msg_
                                client_socket.send(msg_.encode("utf-8"))
                                # * the whole playing phase through server * 
                                
                                while True:
                                    # set timer 
                                    start = time.time()
                                    game_info = receive_message(client_socket)
                                    finish = time.time()
                                    if (finish - start > 20):
                                        print("Time error!")
                                        error_time = "T"
                                        error_time = f"{len(error_time):<{HEADER_LENGTH}}" + error_time
                                        key.send(error_time.encode("utf-8"))
                                        client_socket.send(error_time.encode("utf-8"))
                                        # removing the players
                                        sockets_list.remove(client_socket)
                                        sockets_list.remove(key)
                                        del online_player[client_socket]
                                        del online_player[key]
                                        break
                                    msg_game_info = game_info['data'].decode("utf-8")

                                    result = msg_game_info[0]
                                    chosen_box_x = msg_game_info[1]
                                    chosen_box_y = msg_game_info[2]
                                    turn = msg_game_info[3]
                                    board_dimension = msg_game_info[4]
                                    
                                    msg_game_info = (result + chosen_box_x + chosen_box_y + "2" + board_dimension).encode("utf-8")
                                    msg_game_info_header = f"{len(msg_game_info):<{HEADER_LENGTH}}".encode("utf-8")
                                    if (result == "C"):
                                        key.send(msg_game_info_header + msg_game_info)

                                        start = time.time()
                                        game_info = receive_message(key)
                                        finish = time.time()
                                        if (finish - start > 20):
                                            print("Time error!")
                                            error_time = "T"
                                            error_time = f"{len(error_time):<{HEADER_LENGTH}}" + error_time
                                            key.send(error_time.encode("utf-8"))
                                            client_socket.send(error_time.encode("utf-8"))
                                            # removing the players
                                            sockets_list.remove(client_socket)
                                            sockets_list.remove(key)
                                            del online_player[client_socket]
                                            del online_player[key]
                                            break
                                        msg_game_info = game_info['data'].decode("utf-8")

                                        result = msg_game_info[0]
                                        chosen_box_x = msg_game_info[1]
                                        chosen_box_y = msg_game_info[2]
                                        turn = msg_game_info[3]
                                        board_dimension = msg_game_info[4]

                                        msg_game_info = (result + chosen_box_x + chosen_box_y + "1" + board_dimension).encode("utf-8")
                                        msg_game_info_header = f"{len(msg_game_info):<{HEADER_LENGTH}}".encode("utf-8")
                                        if (result == "C"):
                                            client_socket.send(msg_game_info_header + msg_game_info)
                                        else:
                                            if (result == "2"):
                                                final_msg = "W"
                                                final_msg = f"{len(final_msg):<{HEADER_LENGTH}}" + final_msg
                                                key.send(final_msg.encode("utf-8"))
                                                print("player 2 won!")
                                                final_msg = "L"
                                                final_msg = f"{len(final_msg):<{HEADER_LENGTH}}" + final_msg
                                                client_socket.send(final_msg.encode("utf-8"))
                                                 # removing the players
                                                sockets_list.remove(client_socket)
                                                sockets_list.remove(key)
                                                del online_player[client_socket]
                                                del online_player[key]
                                                break
                                            elif (result == "D"):
                                                final_msg = "D"
                                                final_msg = f"{len(final_msg):<{HEADER_LENGTH}}" + final_msg
                                                key.send(final_msg.encode("utf-8"))
                                                client_socket.send(final_msg.encode("utf-8"))
                                                print("Draw!")
                                                 # removing the players
                                                sockets_list.remove(client_socket)
                                                sockets_list.remove(key)
                                                del online_player[client_socket]
                                                del online_player[key]
                                                break
                                    else:
                                        if (result == "1"):
                                            final_msg = "W"
                                            final_msg = f"{len(final_msg):<{HEADER_LENGTH}}" + final_msg
                                            client_socket.send(final_msg.encode("utf-8"))
                                            print("player 1 won!")
                                            final_msg = "L"
                                            final_msg = f"{len(final_msg):<{HEADER_LENGTH}}" + final_msg
                                            key.send(final_msg.encode("utf-8"))
                                             # removing the players
                                            sockets_list.remove(client_socket)
                                            sockets_list.remove(key)
                                            del online_player[client_socket]
                                            del online_player[key]
                                            break
                                        elif (result == "D"):
                                            final_msg = "D"
                                            final_msg = f"{len(final_msg):<{HEADER_LENGTH}}" + final_msg
                                            key.send(final_msg.encode("utf-8"))
                                            client_socket.send(final_msg.encode("utf-8"))
                                            print("Draw!")
                                             # removing the players
                                            sockets_list.remove(client_socket)
                                            sockets_list.remove(key)
                                            del online_player[client_socket]
                                            del online_player[key]
                                            break
                                    
                            elif (response['data'].decode("utf-8") == "no"):
                                msg_ = "no"
                                msg_ = f"{len(msg_):<{HEADER_LENGTH}}" + msg_
                                client_socket.send(msg_.encode("utf-8"))
                                break
                            break