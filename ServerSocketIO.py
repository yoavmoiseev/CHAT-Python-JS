import os
from ast import Constant
from asyncio import constants
from email.message import Message
from operator import indexOf
import time
from aiohttp import web
import socketio

# Creating Lists
SocketList = []
UsersList = []

# containing all the messages from all users
MessagesList = []

## creates a new Async Socket IO Server
sio = socketio.AsyncServer()
## Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
## instance
sio.attach(app)


# =====================================================================
# the server opens the "index.html" file for defined connection
# 10.0.0.200:8080 with the default path '/' --> "10.0.0.200:8080/"
async def index(request):
    file_path = os.path.join(os.path.dirname(__file__), 'index.html')
    with open(file_path) as f:
        return web.Response(text=f.read(), content_type='text/html')


# the server opens the HTML file for private chat
# when the path is "10.0.0.200:8080/prChat"
async def privateChat(request):
    file_path = os.path.join(os.path.dirname(__file__), 'Private_chat.html')
    with open(file_path) as f:
        return web.Response(text=f.read(), content_type='text/html')


## We bind our aiohttp endpoint to our app
## router
app.router.add_get('/', index)
app.router.add_get('/prChat', privateChat)


## If we wanted to create a new websocket endpoint,
## use this decorator, passing in the name of the
## event we wish to listen out for
@sio.on('message')
async def print_message(sid, message):
    nicknameDelimiter = " :"
    nickname = message[1:message.find(nicknameDelimiter)]
    startPosition= len(nickname) + len(nicknameDelimiter) + 2 # message index and space before the password
    password = message[startPosition : message.find(" :", startPosition)]
    
    # Building List of clients on base of SocketID, started above- after "import"----------------------------
    if message[0] == "2": # 2: new user entered
        #  check the first item of every tuple in list
        #     not in the list
        if all(nickname != item[0] for item in UsersList):
            UsersList.append([nickname, password])
            print(nickname + ", entered to the chat. Time:" + time.asctime())
            # for debugging
            print(UsersList)
        else: #the nickname already in list
            for item in UsersList:
                if (item[0]==nickname):# find this user
                    if (item[1] == password): # check the password is correct
                        print("Come In!")
                    else:
                        print("Wrong Password", message)
                        ## back to the client
                        await sio.emit('message', "Wrong Password", to=sid)
                        return
    
    # first message
    if(message[0] == "2"):
        message = message.replace(nicknameDelimiter + " " + password,"",1) #remove the password
    print(message)

    # Sends chat history to new clients
    if (message[0] == "2" or message[0] == "4"):
        for line in MessagesList:
            await sio.emit('message', line, to=sid)  # to send to ALL- delete-->  to=sid
    
    MessagesList.append(message)
    
    ## back to the client
    await sio.emit('message', message)

## We kick off our server
if __name__ == '__main__':
    web.run_app(app)
