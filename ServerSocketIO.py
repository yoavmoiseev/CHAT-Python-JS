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
    nickname = message[1:message.find(" ")]
    # Building List of clients on base of SocketID, started above- after "import"----------------------------
    #  check the first item of every tuple in list
    if all(str(sid) != item[0] for item in SocketList):
        SocketList.append([str(sid), nickname])
        print(nickname + ", entered to the chat. Time:" + time.asctime())
        # for debugging
        print(SocketList)

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
