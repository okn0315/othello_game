import TCP_connection_module
import copy


class othello:
  NOTHING = 0
  WHITE   = 1
  BLACK   = 2

  def __init__(self):
  
    self.field = [[0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 1, 2, 0, 0, 0,],
                  [0, 0, 0, 2, 1, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0,],
                  [0, 0, 0, 0, 0, 0, 0, 0,],]
    """
    self.field = [[1, 1, 1, 1, 1, 1, 1, 1,],
                  [2, 2, 2, 2, 2, 2, 2, 2,],
                  [1, 2, 1, 2, 1, 1, 1, 1,],
                  [1, 2, 1, 2, 0, 0, 1, 2,],
                  [1, 2, 1, 2, 0, 0, 1, 2,],
                  [1, 2, 1, 2, 1, 2, 2, 2,],
                  [1, 2, 1, 1, 1, 1, 1, 1,],
                  [1, 2, 1, 2, 2, 2, 2, 2,],]
    """
    self.my_color = othello.NOTHING

  def other_side(color):
    if color == othello.WHITE:
      return othello.BLACK

    if color == othello.BLACK:
      return othello.WHITE
    
    return othello.NOTHING


  def _check_turn_over_line(self, place, direction, color):
    look = copy.copy(place)
    update_len = 0

    if self.field[place[1]][place[0]] != othello.NOTHING:
      return 0

    while True:
      look = [x+y for (x, y) in zip(look, direction)]

      if min(look[0], look[1]) < 0 or max(look[0], look[1]) > 7:
        break

      if self.field[look[1]][look[0]] != color and self.field[look[1]][look[0]] != othello.NOTHING:
        update_len += 1

      if self.field[look[1]][look[0]] == color:
        return update_len

      if self.field[look[1]][look[0]] == othello.NOTHING:
        break

    return 0


  def _turn_over_line(self, place, direction, color):
    look = copy.copy(place)
    update_len = 0

    if self.field[place[1]][place[0]] != othello.NOTHING:
      return 0

    while True:
      look = [x+y for (x, y) in zip(look, direction)]

      if min(look[0], look[1]) < 0 or max(look[0], look[1]) > 7:
        break

      if self.field[look[1]][look[0]] != color and self.field[look[1]][look[0]] != othello.NOTHING:
        update_len += 1

      if self.field[look[1]][look[0]] == color:
        for i in range(update_len):
          self.field[place[1]+direction[1]*(i+1)][place[0]+direction[0]*(i+1)] = color
        return update_len

      if self.field[look[1]][look[0]] == othello.NOTHING:
        break

    return 0


  def check_turn_over(self, place, color):
    total = 0
    for x in [-1, 0, 1]:
      for y in [-1, 0, 1]:
        if x != 0 or y != 0:
          total += self._check_turn_over_line(place, [x, y], color)
      
    return total


  def _turn_over(self, place, color):
    total = 0
    for x in [-1, 0, 1]:
      for y in [-1, 0, 1]:
        if x != 0 or y != 0:
          total += self._turn_over_line(place, [x, y], color)
      
    self.field[place[1]][place[0]] = color
    return total


  def put(self, place, color):
    if self.field[place[1]][place[0]] != self.NOTHING:
      return False

    if color != othello.BLACK and color != othello.WHITE:
      return False

    if self.check_turn_over(place, color) == 0:
      return False

    self._turn_over(place, color)
    
    return True


  def check_game_over(self):
    num_of_black = 0
    num_of_white = 0
    for y in range(8):
      for x in range(8):
        if self.field[y][x] == othello.BLACK:
          num_of_black += 1
        elif self.field[y][x] == othello.WHITE:
          num_of_white += 1
    
    if num_of_black + num_of_white == 64:
      if num_of_black > num_of_white:
        return othello.BLACK
      elif num_of_black < num_of_white:
        return othello.WHITE
      else:
        return othello.NOTHING  

    if num_of_black == 0:
      return othello.WHITE
    
    elif num_of_white == 0:
      return othello.BLACK

    return None


  def print_field(self):
    print("  0 1 2 3 4 5 6 7")
    print(" +---------------+")
    for i in range(len(self.field)):
      print(str(i) + "|", end="")
      for j in range(len(self.field[i])):
        if self.field[i][j] == othello.NOTHING:
          print(" ", end="|")
        elif self.field[i][j] == othello.BLACK:
          print("B", end="|")
        elif self.field[i][j] == othello.WHITE:
          print("W", end="|")
      print("")
      if i < len(self.field)-1:
        print(" |-+-+-+-+-+-+-+-|")
      else:
        print(" +---------------+")


class packet:
  MESSAGE                    = 0
  OTHELLO_COORDINATE         = 1
  YOUR_OPPONENT              = 2
  YOUR_COLOR                 = 3
  END_OF_THE_GAME            = 4
  END_OF_THE_GAME_RETRY      = 5
  END_OF_THE_GAME_QUIT       = 6
  OPPONENTS_CONNECTION_ERROR = 7
  REQUEST_REMATCH_WITH_ERROR = 8
  REQUEST_RESEND_WITH_ERROR  = 9
  RESEND_WITH_ERROR          = 10
  RECONNECT_WITH_ERROR       = 11
  QUIT_WITH_ERROR            = 12
  UNEXPECTED_ERROR_RECONNECT = 13
  UNEXPECTED_ERROR_QUIT      = 14

  def __init__(self, source_sock_id, destination_sock_id, typ, dat):
    self.source_id = source_sock_id
    self.destination_id = destination_sock_id
    self.data_type = typ
    self.data = dat


class ReturnError(Exception):
  pass


def server_read_data(data, client_socket_list, matching_list, not_matching_list, waiting_list):
  if data.data_type == packet.MESSAGE:
    print(data.data)

  elif data.data_type == packet.OTHELLO_COORDINATE:
    send_data = packet(data.source_id,
                       data.destination_id,
                       packet.OTHELLO_COORDINATE,
                       data.data)
    for each_sock in client_socket_list:
      if id(each_sock) ==  data.destination_id:
        TCP_connection_module.send_data(each_sock, send_data)
        break
  
  elif data.data_type == packet.END_OF_THE_GAME_RETRY:
    for each_wait in waiting_list:
      if id(each_wait) == data.source_id:
        not_matching_list.append(each_wait)
        waiting_list.remove(each_wait)
        break

    for each_pair in matching_list:
      if id(each_pair[0]) == data.source_id:
        not_matching_list.append(each_pair[0])
        waiting_list.append(each_pair[1])
        matching_list.remove(each_pair)
        break

      elif id(each_pair[1]) == data.source_id:
        not_matching_list.append(each_pair[1])
        waiting_list.append(each_pair[1])
        matching_list.remove(each_pair)
        break

  elif data.data_type == packet.END_OF_THE_GAME_QUIT:
    for each_wait in waiting_list:
      if id(each_wait) == data.source_id:
        each_wait.close()
        waiting_list.remove(each_wait)
        break

    for each_pair in matching_list:
      if id(each_pair[0]) == data.source_id:
        each_pair[0].close()
        waiting_list.append(each_pair[1])
        matching_list.remove(each_pair)
        break

      elif id(each_pair[1]) == data.source_id:
        each_pair[1].close()
        waiting_list.append(each_pair[0])
        matching_list.remove(each_pair)
        break
  
  elif data.data_type == packet.OPPONENTS_CONNECTION_ERROR:
    pass
  
  elif data.data_type == packet.REQUEST_REMATCH_WITH_ERROR:
    pass
  
  elif data.data_type == packet.REQUEST_RESEND_WITH_ERROR:
    pass
  
  elif data.data_type == packet.RESEND_WITH_ERROR:
    pass
  
  elif data.data_type == packet.RECONNECT_WITH_ERROR:
    pass
  
  elif data.data_type == packet.QUIT_WITH_ERROR:
    pass
  
  elif data.data_type == packet.UNEXPECTED_ERROR_RECONNECT:
    pass
  
  elif data.data_type == packet.UNEXPECTED_ERROR_QUIT:
    pass
  
  else:
    pass


def handling_game(client_socket_list, matching_list, not_matching_list, waiting_list):
  """
  Outline
    Execute othello game.

  Argument
    List of client socket

  Return Value
    nomally: None
    socket closed: List of closed socket
  """
  recv_data = None
  recv_data_list = []
  closed_client_list = []

  for sock in client_socket_list:
    try:
      recv_data = TCP_connection_module.recv_data(sock)

    except TCP_connection_module.ConnectionError:
      closed_client_list.append(sock)

    except ConnectionResetError:
      closed_client_list.append(sock)

    except OSError: #Client closed socket
      closed_client_list.append(sock)

    else:
      if recv_data != None:
        recv_data_list.append(recv_data)

  for each_sock_data in recv_data_list:
    for each_recv_data in each_sock_data:
      server_read_data(each_recv_data, client_socket_list, matching_list ,not_matching_list, waiting_list)

  if len(closed_client_list) == 0:
    return None
  else :
    return closed_client_list

  raise ReturnError


def handling_newclient(server_sock, client_sock, sock_list, not_matching_list):
  """
  Outline
    Setup the socket of new client. Append new index to sock_list.

  Argument
    client_socket: New client socket
    sock_list: List of client cocket  (NOT included own size)

  Return Value
    Nothing
  """
  client_sock.setblocking(False)
  sock_list.append(client_sock)

  
  send_data = packet(id(server_sock), id(client_sock), packet.MESSAGE, "Server: Serching opponent...")
  TCP_connection_module.send_data(client_sock, send_data)

  not_matching_list.append(client_sock)


  
def matching(server_sock, not_matching_list, pair_list):
  if len(not_matching_list) >= 2: 
    try:
      send_data = packet(id(server_sock), id(not_matching_list[0]), packet.YOUR_OPPONENT, id(not_matching_list[1]))
      TCP_connection_module.send_data(not_matching_list[0], send_data)
    
      send_data = packet(id(server_sock), id(not_matching_list[0]), packet.YOUR_COLOR, othello.WHITE)
      TCP_connection_module.send_data(not_matching_list[0], send_data)
    
    except OSError:
      pass

    try:
      send_data = packet(id(server_sock), id(not_matching_list[1]), packet.YOUR_OPPONENT, id(not_matching_list[0]))
      TCP_connection_module.send_data(not_matching_list[1], send_data)

      send_data = packet(id(server_sock), id(not_matching_list[1]), packet.YOUR_COLOR, othello.BLACK)
      TCP_connection_module.send_data(not_matching_list[1], send_data)

    except OSError:
      pass

    pair_list.append([not_matching_list[0], not_matching_list[1]])


    not_matching_list.pop(0)
    not_matching_list.pop(0)