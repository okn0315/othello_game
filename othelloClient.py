import TCP_connection_module
import othello_module
import threading


class game_state:
  DISCONNECTED       = 0
  CONNECTED          = 1
  WAIT_OPPONENT      = 2
  WAIT_COLOR_INFORM  = 3
  MY_TURN            = 4
  OPPONENT_TURN      = 5
  WON                = 6
  LOST               = 7
  DREW               = 8

  def __init__(self):
    self.state = self.DISCONNECTED


class UnexpectedInput(Exception):
  pass

class thread_getpacket():
  pass


def game_setup(game :game_state, thread_recv_data :TCP_connection_module.recv_thread):
  while game.state == game_state.WAIT_OPPONENT:
    if len(thread_recv_data.recv) != 0:
      recv_data = thread_recv_data.recv.popleft()

      if   recv_data.data_type == othello_module.packet.MESSAGE:
        print("Message received.\n>", end="")
        print(recv_data.data)

      elif recv_data.data_type == othello_module.packet.YOUR_OPPONENT:
        my_id = recv_data.destination_id
        server_id = recv_data.source_id
        opponent_id = recv_data.data
        game.state = game_state.WAIT_COLOR_INFORM

      elif recv_data.data_type == othello_module.packet.OPPONENTS_CONNECTION_ERROR:
        continue

      else:
        print("Error200: Unexpected packet received.")
        print("data_type:", recv_data.data_type)
        quit()

  while game.state == game_state.WAIT_COLOR_INFORM:
    if len(thread_recv_data.recv) != 0:
      recv_data = thread_recv_data.recv.popleft()

      if   recv_data.data_type == othello_module.packet.YOUR_COLOR:
        othello_data = othello_module.othello()
        othello_data.my_color = recv_data.data
        if othello_data.my_color == turn:
          game.state = game_state.MY_TURN
        else:
          game.state = game_state.OPPONENT_TURN

  return [othello_data, my_id, server_id, opponent_id, game.state]


ipaddr = "127.0.0.1"
port   = 18408

game = game_state()
print("Waiting for connecting to server...")

socket = TCP_connection_module.setup_client(ipaddr, port)

game.state = game_state.CONNECTED
print("Server connected.")

#First player is black
turn = othello_module.othello.BLACK

game.state = game_state.WAIT_OPPONENT
print("Waiting for contact from server...")

thread_recv_data = TCP_connection_module.recv_thread(socket)
thread_recv_data.setDaemon(True)
thread_recv_data.start()


game_exit = False


while game_exit == False:
  if game.state == game_state.WAIT_OPPONENT:
    othello_data, my_id, server_id, opponent_id, game.state = game_setup(game, thread_recv_data)

  elif game.state == game_state.MY_TURN:
    print('\nYour turn')
    othello_data.print_field()
    if othello_data.my_color == othello_module.othello.BLACK:
      print('Your color is BLACK (Input is "x, y")',)
    else:
      print('Your color is WHITE (Input is "x, y")')
    
    can_put = 0
    for x in range(8):
      for y in range(8):
        if othello_data.check_turn_over([x, y], othello_data.my_color) != 0:
          can_put = 1
          break
      if can_put == 1:
        break

    if can_put == 1:      
      while True:
        try:
          coordinate = [int(i) for i in input().split(',')]
          if len(coordinate) != 2:
            raise UnexpectedInput
          if coordinate[0] < 0 or coordinate[0] > 7 :
            raise UnexpectedInput
          if coordinate[1] < 0 or coordinate[1] > 7 :
            raise UnexpectedInput
          if othello_data.check_turn_over(coordinate, othello_data.my_color) == 0:
            raise UnexpectedInput

        except UnexpectedInput:
          pass

        except ValueError:
          pass

        else:
          break

      othello_data.put(coordinate, othello_data.my_color)
      
      if len(thread_recv_data.recv) == 0 or thread_recv_data.recv[0].data_type != othello_module.packet.OPPONENTS_CONNECTION_ERROR:
        send_data = othello_module.packet(my_id, opponent_id, othello_module.packet.OTHELLO_COORDINATE, coordinate)
        TCP_connection_module.send_data(socket, send_data)

        winner = othello_data.check_game_over()
      else :
        print("Opponent isn't connecting to server now...")
        winner = othello_data.my_color
      
      if winner != None:
        send_data = othello_module.packet(my_id, opponent_id, othello_module.packet.END_OF_THE_GAME, None)
        TCP_connection_module.send_data(socket, send_data)

        if winner == othello_data.my_color:
          game.state = game_state.WON
        
        elif winner == othello_module.othello.other_side(othello_data.my_color):
          game.state = game_state.LOST

        elif winner == othello_data.othello.NOTHING:
          game.state = game_state.DREW
      
      else:
        game.state = game_state.OPPONENT_TURN
        
    else: #can_put == 0
      print("You can't put any place... You have to pass...")
      send_data = othello_module.packet(my_id, opponent_id, othello_module.packet.OTHELLO_COORDINATE, None)
      game.state = game_state.OPPONENT_TURN


  elif game.state == game_state.OPPONENT_TURN:
    print("\nOpponent's turn")

    can_put = 0
    for x in range(8):
      for y in range(8):
        if othello_data.check_turn_over([x, y], othello_module.othello.other_side(othello_data.my_color)) != 0:
          can_put = 1
          break

      if can_put == 1:
        break

    if can_put == 0:
      print("Your opponent can't put any place. You can put again!")
      game.state = game_state.MY_TURN
    
    else:
      othello_data.print_field()
      while True:
        while len(thread_recv_data.recv) == 0:
          pass
        recv_data = thread_recv_data.recv.popleft()
        if recv_data.data_type == othello_module.packet.OTHELLO_COORDINATE:
          othello_data.put(recv_data.data, othello_module.othello.other_side(othello_data.my_color))
          winner = othello_data.check_game_over()
          break

        elif recv_data.data_type == othello_module.packet.OPPONENTS_CONNECTION_ERROR:
          print("Opponent isn't connecting to server now...")
          winner = othello_data.my_color
          break 


      if winner != None:
        send_data = othello_module.packet(my_id, opponent_id, othello_module.packet.END_OF_THE_GAME, None)
        TCP_connection_module.send_data(socket, send_data)

        if winner == othello_data.my_color:
          game.state = game_state.WON
        
        elif winner == othello_module.othello.other_side(othello_data.my_color):
          game.state = game_state.LOST

        elif winner == othello_data.othello.NOTHING:
          game.state = game_state.DREW

      else:
        game.state = game_state.MY_TURN

  elif game.state == game_state.WON:
    print("You Win!")
    print("Play again? (Y\\n)")
    while True:
      str = input()
      if len(str) != 0:
        if str[0] == 'y' or str[0] == 'Y':
          game.state = game_state.WAIT_OPPONENT
          send_data = othello_module.packet(my_id, server_id, othello_module.packet.END_OF_THE_GAME_RETRY, None)
          TCP_connection_module.send_data(socket, send_data)
          break

        elif str[0] == 'n' or str[0] == 'N':
          game_exit = 1
          break

  elif game.state == game_state.LOST:
    print("You Lose.")
    print("Play again? (Y\\n)")
    while True:
      str = input()
      if len(str) != 0:
        if str[0] == 'y' or str[0] == 'Y':
          game.state = game_state.WAIT_OPPONENT
          send_data = othello_module.packet(my_id, server_id, othello_module.packet.END_OF_THE_GAME_RETRY, None)
          TCP_connection_module.send_data(socket, send_data)
          break

        elif str[0] == 'n' or str[0] == 'N':
          game_exit = 1
          break

  elif game.state == game_state.DREW:
    print("Wow. It's DROW!!")
    print("Play again? (y\\n)")
    while True:
      str = input()
      if len(str) != 0:
        if str[0] == 'y' or str[0] == 'Y':
          game.state = game_state.WAIT_OPPONENT
          send_data = othello_module.packet(my_id, server_id, othello_module.packet.END_OF_THE_GAME_RETRY, None)
          TCP_connection_module.send_data(socket, send_data)
          break

        elif str[0] == 'n' or str[0] == 'N':
          game_exit = 1
          break

  else:
    print("Error201: Undefined game state.")
    print("game_state:", game.state)
    print(game_state.WAIT_OPPONENT)
    thread_recv_data.kill()
    quit()


send_data = othello_module.packet(my_id, server_id, othello_module.packet.END_OF_THE_GAME_QUIT, None)
TCP_connection_module.send_data(socket, send_data)
thread_recv_data.kill()
socket.close()
quit()