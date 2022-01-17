import TCP_connection_module
import othello_module

ipaddr = "127.0.0.1"
port   = 18408

server_socket = TCP_connection_module.setup_server(ipaddr, port, 10)

client_socket_list = []
not_matching_list = []
pair_list = []
waiting_list = []

while True:
  try:
    client_socket, address = server_socket.accept()

  except BlockingIOError:
    # No client accepted.
    ret = othello_module.handling_game(client_socket_list, pair_list, not_matching_list, waiting_list, id(server_socket))
    if ret != None:
      for closed_socket in ret:
        for each_pair in pair_list:
          if each_pair[0] == closed_socket:
            send_data = othello_module.packet(id(server_socket), id(each_pair[1]), othello_module.packet.OPPONENTS_CONNECTION_ERROR, None)
            TCP_connection_module.send_data(each_pair[1], send_data)
            pair_list.remove(each_pair)
            waiting_list.append(each_pair[1])

          elif each_pair[1] == closed_socket:
            send_data = othello_module.packet(id(server_socket), id(each_pair[0]), othello_module.packet.OPPONENTS_CONNECTION_ERROR, None)
            TCP_connection_module.send_data(each_pair[0], send_data)
            pair_list.remove(each_pair)
            waiting_list.append(each_pair[0])

      closed_socket.close()
      client_socket_list.remove(closed_socket)

  else:
    # A client accepted.
    print("New client connected. id = " + str(id(client_socket)))
    othello_module.handling_newclient(server_socket, client_socket, client_socket_list, not_matching_list)

  othello_module.matching(server_socket, not_matching_list, pair_list)