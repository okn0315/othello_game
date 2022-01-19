import TCP_connection_module
import othello_module
import GUI_module

ipaddr = "127.0.0.1"
port   = 18408


class game_state:
  SETUP              = 0
  DISCONNECTED       = 1
  CONNECTED          = 2
  WAIT_OPPONENT      = 3
  WAIT_COLOR_INFORM  = 4
  MY_TURN            = 5
  OPPONENT_TURN      = 6
  WON                = 7
  LOST               = 8
  DREW               = 9
  WAIT_RETRY_OR_QUIT = 10
  QUIT               = 11

  def __init__(self):
    self.state = self.SETUP


class GUI(GUI_module.GUI, othello_module.othello):
  def __init__(self):
    GUI_module.GUI.__init__(self)
    othello_module.othello.__init__(self)
    self.loop_distance = 1000

    self.title_print()
    self.msg_log_print()
    self.game = game_state()
    self.game_exit = False
    self.othello_data = othello_module.othello()
    

  def window_reflesh_loop(self):
    for j in range(8):
      for i in range(8):
        if self.othello_data.field[j][i] == othello_module.othello.BLACK:
          self.set_othello_black(i, j)
        elif self.othello_data.field[j][i] == othello_module.othello.WHITE:
          self.set_othello_white(i, j)
        else:
          self.remove_othello(i, j)

    self.msg_reflesh()

    if self.mouse_x > 50 and self.mouse_x < 750 and self.mouse_y > 150 and self.mouse_y < 850:
      if self.othello_data.my_color == othello_module.othello.BLACK:
        self.canvas.create_image(self.mouse_x, self.mouse_y, image=self.field_black_transparent_img)
      elif self.othello_data.my_color == othello_module.othello.WHITE:
        self.canvas.create_image(self.mouse_x, self.mouse_y, image=self.field_white_transparent_img)

    self.root.after(self.loop_distance, self.window_reflesh_loop)


  def back_ground_process(self):
    if self.game.state == game_state.SETUP:
      self.game.state = game_state.DISCONNECTED
      self.print_new_log("[System]Waiting for connecting to server...")


    elif self.game.state == game_state.DISCONNECTED:
      self.socket = TCP_connection_module.setup_client(ipaddr, port)
      self.game.state = game_state.CONNECTED
      self.print_new_log("[System]Server connected.")
      

    elif self.game.state == game_state.CONNECTED:
      #First player is black
      self.turn = othello_module.othello.BLACK
      self.game.state = game_state.WAIT_OPPONENT
      self.print_new_log("[System]Waiting for contact from server...")
      self.thread_recv_data = TCP_connection_module.recv_thread(self.socket)
      self.thread_recv_data.setDaemon(True)
      self.thread_recv_data.start()


    elif self.game.state == game_state.WAIT_OPPONENT:
      if len(self.thread_recv_data.recv) != 0:
        recv_data = self.thread_recv_data.recv.popleft()
        
        if  recv_data.data_type == othello_module.packet.MESSAGE:
          self.print_new_log(str(recv_data.data))
          self.my_id = recv_data.destination_id
          self.message_entry.place(x=830, y=850)
          self.send_message_to_all_button.place(x=1205, y=846)
        
        elif recv_data.data_type == othello_module.packet.YOUR_OPPONENT:
          self.my_id = recv_data.destination_id
          self.server_id = recv_data.source_id
          self.opponent_id = recv_data.data
          self.game.state = game_state.WAIT_COLOR_INFORM
          self.send_message_to_opponent_button.place(x=1115, y=846)

        elif recv_data.data_type == othello_module.packet.OPPONENTS_CONNECTION_ERROR:
          self.print_new_log("[System]Disconnected to opponent. Try againing...")

        else:
          pass #再戦時に前の戦いでの残りを読み込む可能性がある
          #self.print_new_log("[System]Error200: Unexpected packet received.")
          #self.print_new_log("[System]data_type:" + str(recv_data.data_type))
          #quit()


    elif self.game.state == game_state.WAIT_COLOR_INFORM:
      if len(self.thread_recv_data.recv) != 0:
        recv_data = self.thread_recv_data.recv.popleft()

        if   recv_data.data_type == othello_module.packet.YOUR_COLOR:
          self.othello_data.my_color = recv_data.data
          if self.othello_data.my_color == self.turn:
            self.game.state = game_state.MY_TURN
          else:
            self.game.state = game_state.OPPONENT_TURN
          self.print_new_log("[System]Connected to the opponent.")
          self.othello_data.field[3][3] = othello_module.othello.WHITE
          self.othello_data.field[4][4] = othello_module.othello.WHITE
          self.othello_data.field[4][3] = othello_module.othello.BLACK
          self.othello_data.field[3][4] = othello_module.othello.BLACK

        elif recv_data.data_type == othello_module.packet.MESSAGE:
          self.print_new_log(str(recv_data.data))
        
        elif recv_data.data_type == othello_module.packet.OPPONENTS_CONNECTION_ERROR:
          self.print_new_log("[System]Disconnected to opponent. Try againing...")
          self.send_message_to_opponent_button.place_forget()
          self.game.state = game_state.WAIT_OPPONENT

        else:
          self.print_new_log("[System]Error201: Unexpected packet received.")
          self.print_new_log("[System]data_type:" + str(recv_data.data_type))
          quit()


    elif self.game.state == game_state.MY_TURN:
      self.print_your_turn()
      if self.othello_data.my_color == othello_module.othello.BLACK:
        pass #マウスカーソルのところに自分の色の石を表示（予定）
      else:
        pass

      can_put = False
      for x in range(8):
        for y in range(8):
          if self.othello_data.check_turn_over([x, y], self.othello_data.my_color) != 0:
            can_put = True
            break
        if can_put:
          break

      if can_put:
        if [self._wait_set_my_disc] not in self.click_callback_function_list:
          self.click_callback_function_list.append([self._wait_set_my_disc])

        if len(self.thread_recv_data.recv) != 0:
          recv_data = self.thread_recv_data.recv.popleft()

          if recv_data.data_type == othello_module.packet.MESSAGE:
            self.print_new_log(str(recv_data.data))
        
          elif recv_data.data_type == othello_module.packet.OPPONENTS_CONNECTION_ERROR:
            if [self._wait_set_my_disc] in self.click_callback_function_list:
              self.click_callback_function_list.remove([self._wait_set_my_disc])
            self.print_new_log("[System]Opponent was disconnected.")
            self.send_message_to_opponent_button.place_forget()
            self.game.state = game_state.WON

          else:
            self.click_callback_function_list.clear()
            self.print_new_log("[System]Error202: Unexpected packet received.")
            self.print_new_log("[System]data_type:" + str(recv_data.data_type))
            quit()
        
      else:
        can_put = False
        for x in range(8):
          for y in range(8):
            if self.othello_data.check_turn_over([x, y], othello_module.othello.other_side(self.othello_data.my_color)) != 0:
              can_put = True
              break
          if can_put:
            break

        if can_put:
          self.game.state = game_state.OPPONENT_TURN
        else:
          winner = self.check_game_over()
          if winner == self.othello_data.my_color:
            self.game.state = game_state.WON
          elif winner == othello_module.othello.other_side(self.othello_data.my_color):
            self.game.state = game_state.LOST
          else:
            self.click_callback_function_list.clear()
            self.print_new_log("[System]Error203: Unexpected error.")
            self.print_new_log("[System]winner:" + str(winner))
            quit()


    elif self.game.state == game_state.OPPONENT_TURN:
      self.print_opponents_turn()
      
      can_put = False
      for x in range(8):
        for y in range(8):
          if self.othello_data.check_turn_over([x, y], othello_module.othello.other_side(self.othello_data.my_color)) != 0:
            can_put = True
            break

        if can_put:
          break

      if can_put:
        if len(self.thread_recv_data.recv) != 0:
          recv_data = self.thread_recv_data.recv.popleft()

          if recv_data.data_type == othello_module.packet.OTHELLO_COORDINATE:
            self.othello_data.put(recv_data.data, othello_module.othello.other_side(self.othello_data.my_color))
            winner = self.othello_data.check_game_over()

            if winner != None:
              if winner == self.othello_data.my_color:
                self.game.state = game_state.WON
              
              elif winner == othello_module.othello.other_side(self.othello_data.my_color):
                self.game.state = game_state.LOST

              elif winner == othello_module.othello.NOTHING:
                self.game.state = game_state.DREW

              else:
                self.click_callback_function_list.clear()
                self.print_new_log("[System]Error204: Unexpected winner appeared.")
                self.print_new_log("[System]" + str(winner))
                quit()
  
            else:
              self.game.state = game_state.MY_TURN


          elif recv_data.data_type == othello_module.packet.MESSAGE:
            self.print_new_log(str(recv_data.data))
        

          elif recv_data.data_type == othello_module.packet.OPPONENTS_CONNECTION_ERROR:
            self.print_new_log("[System]Opponent was disconnected.")
            self.send_message_to_opponent_button.place_forget()
            self.game.state = game_state.WON

          else:
            self.click_callback_function_list.clear()
            self.print_new_log("[System]Error205: Unexpected packet received.")
            self.print_new_log("[System]data_type:" + str(recv_data.data_type))
            quit()
      
      else:
        can_put = False
        for x in range(8):
          for y in range(8):
            if self.othello_data.check_turn_over([x, y], self.othello_data.my_color) != 0:
              can_put = True
              break
          if can_put:
            break

        if can_put:
          self.game.state = game_state.MY_TURN
        else:
          winner = self.check_game_over()
          if winner == self.othello_data.my_color:
            self.game.state = game_state.WON
          elif winner == othello_module.othello.other_side(self.othello_data.my_color):
            self.game.state = game_state.LOST
          else:
            self.click_callback_function_list.clear()
            self.print_new_log("[System]Error206: Unexpected error.")
            self.print_new_log("[System]winner:" + str(winner))
            quit()


    elif self.game.state == game_state.WON:
      self.send_message_to_opponent_button.place_forget()
      self.print_win()
      self.print_play_again()
      self.game.state = game_state.WAIT_RETRY_OR_QUIT


    elif self.game.state == game_state.LOST:
      self.send_message_to_opponent_button.place_forget()
      self.print_lose()
      self.print_play_again()
      self.game.state = game_state.WAIT_RETRY_OR_QUIT


    elif self.game.state == game_state.DREW:
      self.send_message_to_opponent_button.place_forget()
      self.print_drow()
      self.print_play_again()
      self.game.state = game_state.WAIT_RETRY_OR_QUIT

    
    elif self.game.state == game_state.WAIT_RETRY_OR_QUIT:
      pass


    elif self.game.state == game_state.QUIT:
      self.click_callback_function_list.clear()
      send_data = othello_module.packet(self.my_id, self.server_id, othello_module.packet.END_OF_THE_GAME_QUIT, None)
      TCP_connection_module.send_data(self.socket, send_data)
      self.thread_recv_data.kill()
      self.socket.close()
      quit()


    else:
      self.click_callback_function_list.clear()
      self.print_new_log("[System]Error2xx: Unexpected game status.")
      self.print_new_log("[System]" + str(self.game.state))
      quit()

    self.root.after(self.loop_distance, self.back_ground_process)


  def _wait_set_my_disc(self):
    x = self.mouse_x
    y = self.mouse_y
    if x > 0 and x < 800 and y > 100 and y < 900:
      x = int(x/100)
      y = int(y/100-1)
      if self.othello_data.check_turn_over([x,y], self.othello_data.my_color) != 0:
        self.othello_data.put([x,y], self.othello_data.my_color)
        self.click_callback_function_list.remove([self._wait_set_my_disc])

        send_data = othello_module.packet(self.my_id, self.opponent_id, othello_module.packet.OTHELLO_COORDINATE, [x,y])
        TCP_connection_module.send_data(self.socket, send_data)

        winner = self.othello_data.check_game_over()

        if winner != None:
          send_data = othello_module.packet(self.my_id, self.opponent_id, othello_module.packet.END_OF_THE_GAME, None)
          TCP_connection_module.send_data(self.socket, send_data)

          if winner == self.othello_data.my_color:
            self.game.state = game_state.WON

          elif winner == othello_module.othello.other_side(self.othello_data.my_color):
            self.game.state = game_state.LOST

          elif winner == othello_module.othello.NOTHING:
            self.game.state = game_state.DREW

          else:
            self.click_callback_function_list.clear()
            self.print_new_log("[System]Error2xx: Unexpected winner appeared.")
            self.print_new_log("[System]" + str(winner))
            quit()
        
        else:
          self.game.state = game_state.OPPONENT_TURN
          if [self._wait_set_my_disc] in self.click_callback_function_list:
            self.click_callback_function_list.remove([self._wait_set_my_disc])


  def start_button_clicked(self): #Over load from GUI_module.GUI
    GUI_module.GUI.start_button_clicked(self)
    window.back_ground_process()


  def exit_button_clicked(self): #Over load from GUI_module.GUI
    GUI_module.GUI.exit_button_clicked(self)
    self.game.state = game_state.QUIT


  def retry_button_clicked(self): #Over load from GUI_module.GUI
    GUI_module.GUI.retry_button_clicked(self)
    self.remove_game_message()
    self.message_entry.place_forget()
    self.send_message_to_all_button.place_forget()
    self.send_message_to_opponent_button.place_forget()
    self.othello_data = othello_module.othello()
    self.game.state = game_state.WAIT_OPPONENT
    send_data = othello_module.packet(self.my_id, self.server_id, othello_module.packet.END_OF_THE_GAME_RETRY, None)
    TCP_connection_module.send_data(self.socket, send_data)


  def send_message_to_opponent_button_clicked(self): #Over load from GUI_module.GUI
    input = str(self.message_entry.get())
    if input != "":
      send_txt = "[" + str(self.my_name) + "]" + input
      self.message_entry.delete(0, "end")
      send_data = othello_module.packet(self.my_id, self.opponent_id, othello_module.packet.MESSAGE, send_txt)
      TCP_connection_module.send_data(self.socket, send_data)
      self.print_new_log(send_txt)


  def send_message_to_all_button_clicked(self): #Over load from GUI_module.GUI
    input = str(self.message_entry.get())
    if input != "":
      send_txt = "[" + str(self.my_name) + "]" + input
      self.message_entry.delete(0, "end")
      send_data = othello_module.packet(self.my_id, 0, othello_module.packet.MESSAGE, send_txt)
      TCP_connection_module.send_data(self.socket, send_data)


  def mouse_move(self, event): #Over load from GUI_module.GUI
    x = int(self.mouse_x/100)
    y = int((self.mouse_y-100)/100)

    GUI_module.GUI.mouse_move(self, event)
    
    if self.mouse_x > 50 and self.mouse_x < 750 and self.mouse_y > 150 and self.mouse_y < 850:

      for coordinate in [[x-1, y-1], [x, y-1], [x+1, y-1],
                        [x-1, y  ], [x, y  ], [x+1, y  ],
                        [x-1, y+1], [x, y+1], [x+1, y+1],]:
        if coordinate[0] >= 0 and coordinate[0] < 8 and coordinate[1] >= 0 and coordinate[1] < 8:
          if self.othello_data.field[coordinate[1]][coordinate[0]] == othello_module.othello.NOTHING:
            self.remove_othello(coordinate[0], coordinate[1])

          elif self.othello_data.field[coordinate[1]][coordinate[0]] == othello_module.othello.BLACK:
            self.set_othello_black(coordinate[0], coordinate[1])

          elif self.othello_data.field[coordinate[1]][coordinate[0]] == othello_module.othello.WHITE:
            self.set_othello_white(coordinate[0], coordinate[1])

      if self.othello_data.my_color == othello_module.othello.BLACK:
        self.canvas.create_image(self.mouse_x, self.mouse_y, image=self.field_black_transparent_img)
      elif self.othello_data.my_color == othello_module.othello.WHITE:
        self.canvas.create_image(self.mouse_x, self.mouse_y, image=self.field_white_transparent_img)


    """
    x = self.mouse_x
    y = self.mouse_y
    #if self.mouse_x > 50 and self.mouse_x < 750 and self.mouse_y > 150 and self.mouse_y < 850:
    if x > 50 and x < 750 and y > 150 and y < 850:
      x_min = max(int( x/100-0.5), 0)
      y_min = max(int((y-100)/100-0.5), 0)
      x_max = min(int( x/100+0.5), 7)
      y_max = min(int((y-100)/100+0.5), 7)

      for coordinate in [[x_min, y_min], [x_min, y_max], [x_max, y_min], [x_max, y_max]]:
        if self.othello_data.field[coordinate[1]][coordinate[0]] == othello_module.othello.NOTHING:
           self.remove_othello(coordinate[0], coordinate[1])

        elif self.othello_data.field[coordinate[1]][coordinate[0]] == othello_module.othello.BLACK:
           self.set_othello_black(coordinate[0], coordinate[1])

        elif self.othello_data.field[coordinate[1]][coordinate[0]] == othello_module.othello.WHITE:
          self.set_othello_white(coordinate[0], coordinate[1])

      if self.othello_data.my_color == othello_module.othello.BLACK:
        self.canvas.create_image(self.mouse_x, self.mouse_y, image=self.field_black_transparent_img)
      elif self.othello_data.my_color == othello_module.othello.WHITE:
        self.canvas.create_image(self.mouse_x, self.mouse_y, image=self.field_white_transparent_img)
    """

    
class UnexpectedInput(Exception):
  pass

"""
class thread_getpacket():
  pass
"""



window = GUI()
window.window_reflesh_loop()
window.canvas.mainloop()

"""
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
    othello_data, my_id, server_id, opponent_id, game.state = game_setup(game, thread_recv_data, turn)

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
"""