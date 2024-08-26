"""
Created by: Joshua Sizemore
Version 0.2.2
"""

#Import the required libraries
import threading
import socket
import time
import customtkinter

#Socket Part
header = 64

def serverConnect():
  global connected
  if user.session == False:
    clientThread = threading.Thread(target= user.run_client)
    clientThread.start()
    user.session = True

rooms = []


class User:
    def __init__ (self, username, id):
        self.username = username
        self.id = id
        self.clientInfo = ""
        self.request = ""
        self.requestUpdate = False
        self.requestLength = 0
        self.roomConnectedTo = 0
        self.session = False
        self.roomUpdate = False

    def showMess(self, event):
      message = self.username + ": " + messageEntry.get()
      if (message != "" or message != " "):
          messageText.configure(state= "normal")
          messageText.insert(customtkinter.END, "\n" + message)
          messageText.configure(state= "disabled")
          messageEntry.delete(0, customtkinter.END)
    
    def serverRequest(self):
      try:
        while True:
          requestLength  = self.clientInfo.recv(header).decode("utf-8")
          requestLength = int(requestLength)
          self.request = self.clientInfo.recv(requestLength).decode("utf-8")
          if self.request[:1] == "/":
            if self.request[1:] == "rooms":
              self.request = self.request[6:]
              while self.request != "":
                if self.request[:self.request.index(".")] in rooms:
                  pass
                else:
                  rooms.append(self.request[:self.request.index(".")])
                  self.roomUpdate = True
                self.request = self.request[self.request.index(".") + 1:]
            elif self.request[1:] == "disconect":
              self.session = False
          else:
            self.requestUpdate = True
      except Exception as e:
        pass


    def run_client(self):
      self.session = True
      self.clientInfo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server_ip = "10.17.21.170"
      server_port = 443 
      self.clientInfo.connect((server_ip, server_port))

      intializing = user.username
      self.sendServerMess(intializing)
      
      self.requestThread = threading.Thread(target= self.serverRequest)
      self.requestThread.start()


      while self.session:
        if self.requestUpdate:

          messageText.configure(state= "normal")
          messageText.insert(customtkinter.END, self.request + "\n")
          messageText.configure(state= "disabled")
          messageText.see("end")
          self.requestUpdate = False


        if self.roomUpdate:
          roomText.configure(state= "normal")
          roomText.delete("1.0", customtkinter.END)
          roomText.insert("1.0", "Open Rooms: \n\n")
          roomText.insert(customtkinter.END, "\n ".join(rooms))
          roomText.configure(state= "disabled")
          self.roomUpdate = False


      self.sendServerMess("/close")
      time.sleep(0.1)
      self.clientInfo.close()


    def sendMess(self, event):
      message = messageEntry.get()
      if len(message) > 0 and message != " " and user.session == True:
        self.sendServerMess(message)
      messageEntry.delete(0, customtkinter.END)

    def sendServerMess(self, msg):
      message = msg.encode("utf-8")
      msgLength = len(message)
      sendLength = str(msgLength).encode("utf-8")
      sendLength += b' ' * (header - len(sendLength))
      self.clientInfo.send(sendLength)
      self.clientInfo.send(message)




    

#Tkinter Part
win = customtkinter.CTk()
customtkinter.set_appearance_mode("light")
win_size = [900, 400]
win.geometry((str(win_size[0]) + "x" + str(win_size[1])))
win.title("Messaging")
win.minsize(900, 400)

menuFrame = customtkinter.CTkFrame(win, width= 125, fg_color= "light grey", border_width=0, corner_radius= 0)
roomText = customtkinter.CTkTextbox(menuFrame, fg_color= "light grey", border_width= 0,  corner_radius= 0, font= ("Helvetica", 10))
connectButton = customtkinter.CTkButton(menuFrame, text= "Connect", text_color= "black", hover_color= "grey", fg_color= "dark grey", command= serverConnect)

messageTextFrame = customtkinter.CTkFrame(win, fg_color = "transparent", border_width=0, corner_radius= 0)
messageText = customtkinter.CTkTextbox(messageTextFrame, fg_color= "transparent", border_width= 0, corner_radius= 0,  font= ("Helvetica", 11))
messageEntry = customtkinter.CTkEntry(messageTextFrame, fg_color= "light grey", border_width= 0, corner_radius= 5)


messageText.insert("1.0", "Welcome to Peer Messenger!\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nClick the Connect button to join\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nAfter you connect type '/help' to learn more\n\n")
messageText.configure(state= "disabled")

roomText.insert("1.0", "Open Rooms: \n\n")
roomText.configure(state= "disabled")

messageText.insert("1.0", "Welcome to Peer Messenger!\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nClick the Connect button to join\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nAfter you connect type '/help' to learn more\n\n")
messageText.configure(state= "disabled")

user = User("Guest", 1)


def close():
  user.session = False
  time.sleep(0.1)
  win.destroy()

win.protocol("WM_DELETE_WINDOW", close)
win.bind('<Return>', user.sendMess)

menuFrame.pack_propagate(False)
menuFrame.pack(anchor= "nw", fill= customtkinter.Y, side= customtkinter.LEFT)
roomText.pack(anchor= "nw", fill= customtkinter.Y)
connectButton.pack(padx= 10, pady =10, anchor= "s", side= customtkinter.BOTTOM)

messageTextFrame.pack(fill= customtkinter.BOTH, expand= True)
messageText.pack(padx = 5, pady = 5, fill= customtkinter.BOTH)
messageEntry.pack(padx= 10, pady= 10, fill= customtkinter.X, side= customtkinter.BOTTOM)




win.mainloop()