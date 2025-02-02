"""
Created by: Joshua Sizemore
Version 0.2.2
"""
import socket
import threading
import customtkinter


header = 64
stopServer = False


#Server part of code
clients =[]
server = None
clientNum = 0
totalClientsConnected = 0
nextClient = "client" + str(clientNum + 1)
commands = ["/join", "/help", "/clients", "/create"]
serverRunning = False
clientNumChange = False
rooms = []

#Server global methods
def stopServer():
    global serverRunning
    global clientNum
    global totalClientsConnected

    clients.clear()
    clientNum = 0
    totalClientsConnected = 0
    serverRunning = False


def startServerThread():
    global serverRunning

    serverRunning = True
    serverThread = threading.Thread(target= startServer)
    serverThread.start()



def startServer():
    global server
    global serverRunning
    global clientNumChange

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverIp = "10.17.21.170"
    print(serverIp)
    port = 443
    server.bind((serverIp, port))
    server.listen(1)

    clientTetheringThread = threading.Thread(target= clientTethering)
    clientTetheringThread.start()
    
    print("Online")


    while serverRunning:

        if clientNumChange == True:
            currentUserText.configure(state= "normal")
            currentUserText.delete("1.0",customtkinter.END)
            for i in range(len(clients)):
                currentUserText.insert(customtkinter.END, "\n" + str(clients[i].id))
            for j in range(len(rooms)):
                currentUserText.insert(customtkinter.END, "\n" + str(rooms[j][0]))
            currentUserText.configure(state= "disabled")
            clientNumChange = False


    print("Killed")
    server.close()



def clientTethering():
    global server
    global clientNum
    global nextClient
    global clientNumChange
    global totalClientsConnected

    try:
        while serverRunning:
            clientNum = clientNum + 1
            totalClientsConnected = totalClientsConnected + 1
            nextClient = "client" + str(totalClientsConnected + 1)
            clientSocket, addr = server.accept()

            clients.append(exec("%s = None" % (nextClient)))
            for i in range(len(clients)):
                if clients[i] == None:
                    clients[i] = Client("Undef", totalClientsConnected, clientSocket, addr,)
            clientNumChange = True


            thread = threading.Thread(target= clients[totalClientsConnected - 1].handleClient)
            thread.start()
    except Exception as e:
        pass


#Sends a message to the specified client
def sendConsoleMess(client, msg):
  message = msg.encode("utf-8")
  msgLength = len(message)
  sendLength = str(msgLength).encode("utf-8")
  sendLength += b' ' * (header - len(sendLength))
  client.send(sendLength)
  client.send(message)


#Gets the message from the server(console) text entry (messageEntry) and sends it to every client using the sendConsoleMess method
def consoleMess(event):
    if len(clients) > 0:
        for i in range(len(clients)):
            sendConsoleMess(clients[i].clientSocket, ("Console: "+ messageEntry.get()))
        messageEntry.delete(0, customtkinter.END)


class Client():
    def __init__ (self, username, id, clientSocket, addr,):
        self.username = username
        self.id = id
        self.clientSocket = clientSocket
        self.addr = addr,
        self.request = ""
        self.requestUpdate = False
        self.requestLength = 0
        self.session = True
        self.currentRoom = "not"
        self.created = False
        self.userType = "user"
        self.roomConnectingStatus = "not"
        self.numRooms = len(rooms)
        

    def clientRequest(self):
        try:
            while self.session == True:
                self.requestLength  = self.clientSocket.recv(header).decode("utf-8")
                self.requestLength = int(self.requestLength)
                self.request = self.clientSocket.recv(self.requestLength).decode("utf-8")
                self.requestUpdate = True
        except Exception as e:
            pass

    
    def handleClient(self):
        global clientNumChange

        response = "Connected"
        print(self.addr)
        sendConsoleMess(self.clientSocket, response)

        self.requestLength  = self.clientSocket.recv(header).decode("utf-8")
        self.requestLength = int(self.requestLength)
        self.username = self.clientSocket.recv(self.requestLength).decode("utf-8")
        if self.username == "Guest":
            self.username = self.username + str(self.id)
        print( self.username + " joined the server.")
        

        requestThread = threading.Thread(target= self.clientRequest)
        requestThread.start()

        while self.session == True:
            global clientNum
            if len(rooms) > self.numRooms:
                allRooms = ""
                if len(rooms) > 0:
                    for room in rooms:
                        allRooms = allRooms + room[0] + "."
                    sendConsoleMess(self.clientSocket, "/rooms " + allRooms)
                self.numRooms = len(rooms)


            if self.requestUpdate == True:

                if(self.request[0:1] == "/"):
                    if(self.request[1:5] == "join"):
                        if len(rooms) > 0 and self.currentRoom == "not":
                            for i in range(len(rooms)):
                                if self.request[6: ] == rooms[i][0]:
                                    self.roomConnectingStatus = "connecting"
                                    self.currentRoom = rooms[i][0]
                                    sendConsoleMess(self.clientSocket, "Connecting ...")
                                    for j in range(len(rooms[i])):
                                        for client in clients:
                                            if rooms[i][j] == client.username:
                                                if client.userType == "owner":
                                                    sendConsoleMess(client.clientSocket, self.username + " is wanting to connect. Do you want them to join (/y or /n) \n")
                        else:
                            sendConsoleMess(self.clientSocket, "There are no rooms (or you are already in a room so type /leave)")
                        
                                    
                    elif(self.request[1:] == "help"):
                        sendConsoleMess(self.clientSocket, "Here is a list of the commands and what they Do:\n\n'/clients' : shows all the current clients connected to the server\n\n'/join (room name)'  : Allows you to join an open room")
                    
                    elif(self.request[1:] == "clients"):
                        if len(clients) > 1:
                            mes = ""
                            for i in range(len(clients)):
                                mes = mes + "\n" + clients[i].username
                            sendConsoleMess(self.clientSocket, mes)
                        else:
                            sendConsoleMess(self.clientSocket, "You're all Alone :(")
                    
                    elif(self.request[1:] == "c"):
                        clientNumChange = True
                        if self.created == False:
                            self.userType = "owner"
                            newRoom = [self.username + "'s room", self.username]
                            rooms.append(newRoom)
                            self.currentRoom = rooms[-1][0]
                            self.roomConnectingStatus = "connected"
                            self.created = True
                        else: 
                            sendConsoleMess(self.clientSocket, "You already have a room")
                        
                    elif(self.request[1:] == "rooms"):
                        if len(rooms) > 0:
                            mes = ""
                            for i in range(len(rooms)):
                                mes = mes +  "\n" + rooms[i][0]
                            sendConsoleMess(self.clientSocket, mes)
                        else:
                            sendConsoleMess(self.clientSocket, "There are no rooms open")
                    
                    elif(self.request[1:] == "y"):
                        for client in clients:
                            if client.roomConnectingStatus == "connecting" and client.currentRoom == self.currentRoom:
                                sendConsoleMess(client.clientSocket, "\nConnected\n")
                                client.roomConnectingStatus = "connected"
                                client.currentRoom = self.currentRoom

                    elif(self.request[1:] == "n"):
                        for client in clients:
                            if client.roomConnectingStatus == "connecting" and client.currentRoom == self.currentRoom:
                                sendConsoleMess(client.clientSocket, "\nConnection Denied\n")
                                client.roomConnectingStatus = "not"
                                client.currentRoom = "not"

                    elif(self.request[1:] == "leave"):
                        if self.currentRoom != "not":
                            self.currentRoom = "not"
                            self.roomConnectingStatus = "not"
                            for room in rooms:
                                for i in range(len(room)):
                                    if room[i] == self.username:
                                        #remove user from room
                                        pass

                    elif(self.request[1:] == "close"):
                        self.session = False
                else:
                    if self.currentRoom != "not":
                        for client in clients:
                            if client.currentRoom == self.currentRoom:
                                sendConsoleMess(client.clientSocket, self.username + ": " + self.request + "\n")                            
                                print(self.currentRoom + "- " + self.username + ": " + self.request)
                    else:
                        print(self.username + ": " + self.request)
            self.requestUpdate = False


        print(self.username + " left the server.")
        self.clientSocket.close()
        for i in range(len(clients)):
            if clients[i].id == self.id:
                del clients[i]
            break
        clientNum = clientNum - 1
        clientNumChange = True


#Tkinter part of code

win = customtkinter.CTk()
win.geometry("700x350")
win.title("Message Server")

messageEntry = customtkinter.CTkEntry(win)
startButton = customtkinter.CTkButton(win, text= "Start Server", command= startServerThread)
endButton = customtkinter.CTkButton(win, text= "Shut Off Server", command= stopServer)


currentUserText = customtkinter.CTkTextbox(win,bg_color= "transparent", border_width= 0, font= ("Helvetica", 11))
currentUserText.configure(state= "disabled")


def close():
    global serverRunning
    for i in range(len(clients)):
        clients[i].session = False
    serverRunning = False
    
    win.destroy()

win.protocol("WM_DELETE_WINDOW", close)

#print(len(clients))
win.bind('<Return>', consoleMess)


messageEntry.pack(padx = 5, pady= 5)
endButton.pack(padx = 5, pady= 5)
startButton.pack(padx = 5, pady= 5)
currentUserText.pack(padx = 5, pady= 5)
win.mainloop()