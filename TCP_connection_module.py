import socket
import pickle
import sys
import threading
from collections import deque

"""
Using module "pickle" to send or receive data.

In the TCP, if send some times without receive, receive one in a low data.
So appending a header.  The header means data size. (NOT included own size.)
"""

class ConnectionError(Exception):
  pass

class SendDataIsTooLarge(Exception):
  pass

HEADER_SIZE = 4 #byte
MAX_DATA_SIZE = 2**(HEADER_SIZE*8) #byte
#2**(4*8) == 4GB


def setup_server(ipaddr, port, max_listen):
  """
  Outline
    Set up the server socket connection.

  Argument
    ipaddr: IP address of server. Type is string.
    port: Port of server. Type is integer.
    max_listen: Maximam number of client to connect.

  Return Value
    Server socket used othello game.
  """
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind((ipaddr, port))
  s.listen(max_listen)
  s.setblocking(False)
  return s


def setup_client(ipaddr, port):
  """
  Outline
    Setup the client socket connection.
  
  Argument
    ipaddr: IP address of server. Type is string.
    port: Port of server. Type is integer.

  Return Value
    Client socket used othello game.
  """
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect( (ipaddr, port) )
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.setblocking(False)
  return s


def send_data (sock, data):
  """
  Outline
    Send a data to socket.
  
  Argument
    sock: Socket used to send a data.
    data: Data to send.

  Return Value
    Size of sended data. (Including header size.)
  """
  pickle_send_data = pickle.dumps(data)

  if sys.getsizeof(pickle_send_data) > MAX_DATA_SIZE:
    raise SendDataIsTooLarge

  pickle_send_data = sys.getsizeof(pickle_send_data).to_bytes(HEADER_SIZE, 'big') + pickle_send_data
  sock.send(pickle_send_data)
  return sys.getsizeof(pickle_send_data)


def recv_data(sock):
  """
  Outline
    Receive a data from a socket.

  Argument
    sock: Socket to receive a data.

  Return Value
    List of received data. Index means sequence of received. 
  """
  try:
    hashed_recv_data = sock.recv(64)
  
  except BlockingIOError:
    return None

  else:
    if hashed_recv_data == b'':
      raise ConnectionError('Error000: recv() failed')
    
    else:
      recv_data = hashed_recv_data

  while True:
    try:
      hashed_recv_data = sock.recv(64)
    
    except BlockingIOError:
      break
    
    else:
      if len(hashed_recv_data) <= 0:
        break
      recv_data += hashed_recv_data

  ret_data = []

  while True:
    if recv_data == b'':
      break

    data_size = b''
    while sys.getsizeof(data_size) != sys.getsizeof(b'') + HEADER_SIZE:
      data_size += recv_data[:1]
      recv_data = recv_data[1:]

    data_size = int.from_bytes(data_size, 'big')
    
    each_data = b''
    while sys.getsizeof(each_data) != data_size:
      each_data += recv_data[:1]
      recv_data = recv_data[1:]
    
    ret_data.append(pickle.loads(each_data))
    
  return ret_data


class recv_thread(threading.Thread):
  """
  Outline
    Receive a data from a socket using thread.

  How to Use
    1. Make a thread to call "__init__"  (ex. thread1 = recv_thread(socket)
    2. Start the thread to call "start"  (ex. thread1.start()
    3. If you want to stop the thread, call "stop"  (ex. thread1.stop()
       Note: Thread is running even you call "stop".
             Lots of thread makes your computer slower even any thread was called "stop". 
    4. If you want to start again, call "restart"  (ex. thread1.restart()
    5. If you want to kill the thread, call "kill"  (ex. thread1.kill()
    6. Received data is recv_thread.recv. Type is deque() 
  """
  def __init__(self, sock):
    threading.Thread.__init__(self)
    self.socket = sock
    self.recv = deque()
    self._mystop = [0]
    self._kill = [0]
    
  def run(self):
    data = None
    while self._kill[0] == False:
      while self._mystop[0] == False and self._kill[0] == False:
        data = recv_data(self.socket)
        if data != None:
          for each_data in data:
            self.recv.append(each_data)
          data = None
  
  def mystop(self):
    self._mystop[0] = True

  def restart(self):
    self._mystop[0] = False

  def kill(self):
    self._kill[0] = True