#Import the required libraries
import tkinter as tk
import ttk
import threading
import socket
import time

#Socket Part
header = 64
connected = False

def serverConnect():
  global connected
  if connected == False:
    clientThread = threading.Thread(target= user.run_client)
    clientThread.start()
    connected = True

rooms = []


class User:
    def __init__ (self, username, id):
        self.username = username
        self.id = id
        self.client = ""
        self.request = ""
        self.requestUpdate = False
        self.requestLength = 0
        self.isConnected = False
        self.roomConnectedTo = 0
        self.session = True
        self.roomUpdate = False

    def showMess(self, event):
      message = self.username + ": " + messageEntry.get()
      if (message != "" or message != " "):
          messageText.config(state= "normal")
          messageText.insert(tk.END, "\n" + message)
          messageText.config(state= "disabled")
          messageEntry.delete(0, tk.END)
    
    def serverRequest(self):
      try:
        while True:
          requestLength  = self.client.recv(header).decode("utf-8")
          requestLength = int(requestLength)
          self.request = self.client.recv(requestLength).decode("utf-8")
          if self.request[:1] == "/":
            if self.request[1:6] == "rooms":
              self.request = self.request[6:]
              while self.request != "":
                if self.request[:self.request.index(".")] in rooms:
                  pass
                else:
                  rooms.append(self.request[:self.request.index(".")])
                  self.roomUpdate = True
                self.request = self.request[self.request.index(".") + 1:]
          else:
            self.requestUpdate = True
      except Exception as e:
        pass


    def run_client(self):
      self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      #server_ip = "192.168.206.1"
      server_ip = "10.17.0.126"
      server_port = 443 
      self.client.connect((server_ip, server_port))

      intializing = user.username
      self.sendConsoleMess(intializing)
      
      self.requestThread = threading.Thread(target= self.serverRequest)
      self.requestThread.start()


      while self.session:
        if self.requestUpdate == True:

          messageText.config(state= "normal")
          messageText.insert(tk.END, self.request + "\n")
          messageText.config(state= "disabled")
          messageText.see("end")
          self.requestUpdate = False


        if self.roomUpdate == True:
          roomText.config(state= "normal")
          roomText.delete("1.0", tk.END)
          roomText.insert("1.0", "Open Rooms: \n\n")
          roomText.insert(tk.END, "\n ".join(rooms))
          roomText.config(state= "disabled")
          self.roomUpdate = False


      self.sendConsoleMess("close")
      time.sleep(1)
      self.client.close()


    def sendMess(self, event):
      message = messageEntry.get()
      if len(message) > 0 and message != " ":
        self.sendConsoleMess(message)
      messageEntry.delete(0, tk.END)

    def sendConsoleMess(self, msg):
      message = msg.encode("utf-8")
      msgLength = len(message)
      sendLength = str(msgLength).encode("utf-8")
      sendLength += b' ' * (header - len(sendLength))
      self.client.send(sendLength)
      self.client.send(message)




    

#Tkinter Part
win = tk.Tk()
win.geometry("700x350")
win.title("Messaging")

style = ttk.Style(win)
style.layout("arrowless.Vertical.Scrollbar", 
         [("Vertical.Scrollbar.trough",
           {"children": [("Vertical.Scrollbar.thumb", 
                          {"expand": "0", "sticky": "nswe"})],
            "sticky": "ns"})])


win.columnconfigure(0, weight= 4, uniform= "a")
win.columnconfigure(1, weight= 26, uniform= "a")
win.columnconfigure(2, weight= 1, uniform= "a")
win.rowconfigure(0, weight= 23, uniform= "a")
win.rowconfigure(1, weight= 2, uniform= "a")


textFrame = tk.Frame(win, bg= None, bd= None)
messageEntry = tk.Entry(win)

scrollBar = ttk.Scrollbar(win, orient= "vertical", style= "arrowless.Vertical.Scrollbar")
messageText = tk.Text(win, bg= None, bd= 0, font= "Helvetica 11", yscrollcommand= scrollBar.set)
messageText.insert("1.0", "Welcome to Peer Messenger!\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nClick the Connect button to join\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nAfter you connect type '/help' to learn more\n\n")
messageText.config(state= "disabled")
scrollBar.config(command= messageText.yview)
connectButton = tk.Button(win, text= "Connect", command= serverConnect)

roomText = tk.Text(win, bg= "light grey", bd= 0, font= "Helvetica 10", yscrollcommand= scrollBar.set)
roomText.insert("1.0", "Open Rooms: \n\n")
roomText.config(state= "disabled")

messageText.insert("1.0", "Welcome to Peer Messenger!\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nClick the Connect button to join\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nAfter you connect type '/help' to learn more\n\n")
messageText.config(state= "disabled")

user = User("Guest", 1)


def close():
  user.session = False
  win.destroy()

win.protocol("WM_DELETE_WINDOW", close)
win.bind('<Return>', user.sendMess)
roomText.grid(row= 0, column= 0, sticky= "nsew")
messageText.grid(row= 0, column= 1, sticky= "nsew")
connectButton.grid(row= 1, column= 0, sticky= "nsew")
scrollBar.grid(row= 0, column= 2, sticky= "nsew")
textFrame.grid(row= 0, column= 1, sticky= "nsew")
messageEntry.grid(row= 1, column= 1, sticky= "nsew")


win.mainloop()