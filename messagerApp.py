"""
Created by: Joshua Sizemore
Version 0.2.1
"""

#Import the required libraries
import tkinter as tk
import ttk
import threading
import socket
import time
import customtkinter

#Socket Part
header = 64
connected = False

def serverConnect():
  global connected
  if connected == False:
    
    
    clientThread = threading.Thread(target= user.run_client)
    clientThread.start()
    connected = True
    user.session = True

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
        self.session = False
        self.roomUpdate = False

    def showMess(self, event):
      message = self.username + ": " + messageEntry.get()
      if (message != "" or message != " "):
          messageText.configure(state= "normal")
          messageText.insert(tk.END, "\n" + message)
          messageText.configure(state= "disabled")
          messageEntry.delete(0, tk.END)
    
    def serverRequest(self):
      global connected
      try:
        while True:
          requestLength  = self.client.recv(header).decode("utf-8")
          requestLength = int(requestLength)
          self.request = self.client.recv(requestLength).decode("utf-8")
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
              connected = False
              self.session = False
          else:
            self.requestUpdate = True
      except Exception as e:
        pass


    def run_client(self):
      self.session = True
      self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server_ip = "10.17.0.126"
      server_port = 443 
      self.client.connect((server_ip, server_port))

      intializing = user.username
      self.sendConsoleMess(intializing)
      
      self.requestThread = threading.Thread(target= self.serverRequest)
      self.requestThread.start()


      while self.session:
        if self.requestUpdate:

          messageText.configure(state= "normal")
          messageText.insert(tk.END, self.request + "\n")
          messageText.configure(state= "disabled")
          messageText.see("end")
          self.requestUpdate = False


        if self.roomUpdate:
          roomText.configure(state= "normal")
          roomText.delete("1.0", tk.END)
          roomText.insert("1.0", "Open Rooms: \n\n")
          roomText.insert(tk.END, "\n ".join(rooms))
          roomText.configure(state= "disabled")
          self.roomUpdate = False


      self.sendConsoleMess("/close")
      time.sleep(0.1)
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
win = customtkinter.CTk()
win.geometry("900x400")
win.title("Messaging")



win.columnconfigure(0, weight= 4, uniform= "a")
win.columnconfigure(1, weight= 26, uniform= "a")

win.rowconfigure(0, weight= 23, uniform= "a")
win.rowconfigure(1, weight= 3, uniform= "a")


textFrame = customtkinter.CTkFrame(win, border_width=0, corner_radius= 0)
messageEntry = customtkinter.CTkEntry(win, fg_color= "light grey", border_width= 0, corner_radius= 5)


messageText = customtkinter.CTkTextbox(win, fg_color= "transparent", border_width= 0, corner_radius= 0,  font= ("Helvetica", 11))
messageText.insert("1.0", "Welcome to Peer Messenger!\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nClick the Connect button to join\n_-_-_-_-_-_-_-_-_-_-_-_-_-_\n\nAfter you connect type '/help' to learn more\n\n")
messageText.configure(state= "disabled")
connectButton = customtkinter.CTkButton(win, text= "Connect", text_color= "black", hover_color= "grey", fg_color= "transparent", command= serverConnect)

roomText = customtkinter.CTkTextbox(win, fg_color= "light grey", border_width= 0,  corner_radius= 0, font= ("Helvetica", 10))
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
if user.session == True:
  win.bind('<Return>', user.sendMess)
roomText.grid(row= 0, column= 0, sticky= "nsew")
messageText.grid(row= 0, column= 1, sticky= "nsew")
connectButton.grid(row= 1, column= 0, sticky= "nsew", padx= 10, pady =10)
textFrame.grid(row= 0, column= 1, sticky= "nsew")
messageEntry.grid(row= 1, column= 1, sticky= "nsew", padx= 10, pady= 10)


win.mainloop()