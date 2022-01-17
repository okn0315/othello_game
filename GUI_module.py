import tkinter
import tkinter.font

class GUI:
  field_img = None
  field_black_img = None
  field_white_img = None

  def __init__(self):
    self.root = tkinter.Tk()
    self.root.title("Yothello")
    self.canvas = tkinter.Canvas(self.root, width=1300, height=900, bg="white")
    self.canvas.pack()
    self.field_img = tkinter.PhotoImage(file="othello_field.png")
    self.field_black_img = tkinter.PhotoImage(file="othello_field_black.png")
    self.field_white_img = tkinter.PhotoImage(file="othello_field_white.png")
    self.log_img = tkinter.PhotoImage(file="message_wide.png")
    self.num_of_msg_line = 35
    self.msg_list = [""]*self.num_of_msg_line
    self.msg_label_list = []
    self.game_state_label = tkinter.Label(self.canvas, text="", font=("System", 30), bg="white", fg="black")
    self.mouse_x = 0
    self.mouse_y = 0
    self.mouse_c = False
    self.click_callback_function_list = []
    self.root.bind("<Motion>", self.mouse_move)
    self.root.bind("<ButtonPress>", self.mouse_press)
    self.root.bind("<ButtonRelease>", self.mouse_release)
    self.message_width=30
    self.name_width=10

    for i in range(self.num_of_msg_line):
      self.msg_label_list.append(tkinter.Label(self.canvas, text="", font=("System", 10), bg="black", fg="white"))
      self.msg_label_list[i].place(x=830, y=120+20*i)
    
    
  def title_print(self):
    for i in range(8):
      for j in range(8):
        self.canvas.create_image(50+i*100, 150+j*100, image=self.field_img)

    self.title_label = tkinter.Label(self.root, text="Yothello", font=("System", 24) )
    self.title_label.place(x=330, y=200)

    self.start_button = tkinter.Button(self.root, text="スタート", font=("Times New Roman", 24), command=self.start_button_clicked)
    self.start_button.place(x=325, y=600)

    self.name_label = tkinter.Label(self.root, text="Name:", font=("Times New Roman", 24), bg="white")
    self.name_label.place(x=280, y=500)
    self.my_name_entry = tkinter.Entry(width=self.name_width, font=("Times New Roman", 24))
    self.my_name_entry.place(x=380, y=500)


  def msg_log_print(self):
    self.canvas.create_image(1050, 500, image=self.log_img)
    self.message_entry=tkinter.Entry(width=self.message_width, font=("System", 10))
    self.send_message_to_opponent_button = tkinter.Button(self.root, text="対戦相手", font=("System", 10), command=self.send_message_to_opponent_button_clicked)
    self.send_message_to_all_button = tkinter.Button(self.root, text=" 全体 ", font=("System", 10), command=self.send_message_to_all_button_clicked)
  

  def start_button_clicked(self):
    self.title_label.destroy()
    self.start_button.destroy()
    self.name_label.destroy()
    self.my_name = self.my_name_entry.get()
    self.my_name_entry.destroy()

  def send_message_to_opponent_button_clicked(self):
    pass

  def send_message_to_all_button_clicked(self):
    pass

  def remove_othello(self, x, y):
    self.canvas.create_image(50+x*100, 150+y*100, image=self.field_img)

  def set_othello_black(self, x,y):
    self.canvas.create_image(50+x*100, 150+y*100, image=self.field_black_img)

  def set_othello_white(self, x,y):
    self.canvas.create_image(50+x*100, 150+y*100, image=self.field_white_img)

  def print_your_turn(self):
    self.game_state_label["text"] = "あなたの番です"
    self.game_state_label.place(x=285, y=30)

  def print_opponents_turn(self):
    self.game_state_label["text"] = "相手の番です"
    self.game_state_label.place(x=300, y=30)

  def remove_game_message(self):
    self.game_state_label["text"] = ""
    
  def print_win(self):
    self.game_state_label["text"] = "あなたの勝ちです"
    self.game_state_label.place(x=270, y=30)

  def print_lose(self):
    self.game_state_label["text"] = "あなたの負けです"
    self.game_state_label.place(x=270, y=30)

  def print_drow(self):
    self.game_state_label["text"] = "引き分けです"
    self.game_state_label.place(x=300, y=30)

  def print_play_again(self):
    self.exit_button = tkinter.Button(self.root, text="終了", font=("Times New Roman", 24), command=self.exit_button_clicked)
    self.retry_button = tkinter.Button(self.root, text="リトライ", font=("Times New Roman", 24), command=self.retry_button_clicked)
    self.exit_button.place(x=100, y=600)
    self.retry_button.place(x=550, y=600)

  def exit_button_clicked(self):
    self.exit_button.destroy()
    self.retry_button.destroy()

  def retry_button_clicked(self):
    self.exit_button.destroy()
    self.retry_button.destroy()

  def msg_reflesh(self):
    for i in range(self.num_of_msg_line):
      self.msg_label_list[i]["text"] = self.msg_list[i]

  def print_new_log(self, string):
    for i in range(self.num_of_msg_line-1):
      self.msg_list[i] = self.msg_list[i+1]
    self.msg_list[self.num_of_msg_line-1] = string
    self.msg_reflesh()

  def mouse_move(self, event):
    self.mouse_x = event.x
    self.mouse_y = event.y

  def mouse_press(self, event):
    self.mouse_c = True
    for each_func in self.click_callback_function_list:
      if len(each_func) == 1:
        each_func[0]()
      else:
        each_func[0](*each_func[1])

  def mouse_release(self, event):
    self.mouse_c = False

  """
  def field_clicked(self, mouse_x, mouse_y, mouse_c):
    if (    mouse_c == True 
        and mouse_x > 0 and mouse_x < 800 
        and mouse_y > 0 and mouse_y < 800):
      return [mouse_x/100, mouse_y/100]

    else:
      return None
  """


"""
var = GUI()
var.title_print()
var.msg_log_print()
var.print_opponents_turn()
var.print_your_turn()
var.root.mainloop()
"""

"""
  def mainloop(self):
    if self.county < 8:
      if (self.countx+self.county)%2 == 0:
        self.set_othello_black(self.countx, self.county)
      else:
        self.set_othello_white(self.countx, self.county)

      if self.countx < 7:
        self.countx += 1
      else:
        self.countx = 0
        self.county += 1

    self.root.after(1000, self.mainloop)
  """


"""
root, canvas = window_make()

field_img = tkinter.PhotoImage(file="othello_field.png")
field_black_img = tkinter.PhotoImage(file="othello_field_black.png")
field_white_img = tkinter.PhotoImage(file="othello_field_white.png")
log_img = tkinter.PhotoImage(file="message.png")

title_label, start_button = title_print(root, canvas)
msg_log_print(root, canvas)

message_log = msg(root)
message_log.print_new_log("ゲームを起動しています...")

set_othello_white(root, canvas, 3, 4)
set_othello_white(root, canvas, 4, 3)
set_othello_black(root, canvas, 3, 3)
set_othello_black(root, canvas, 4, 4)

root.mainloop()
"""