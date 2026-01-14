import socket
import threading
import helperApp

#if using Windows
HOST = helperApp.get_host_ip()
#otherwise, find the IP from your machine manually
#HOST = " . . . . "
PORT = 12345

def main():
    global connectedClients
    connectedClients = {}
    start_server()

def start_server():
    """start the server, accept connections from clients, create a thread to handle each client"""

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((HOST, PORT))
    serverSocket.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT}")
    
    while True:
        clientSocket, addr = serverSocket.accept()
        print(f"[SERVER] Established connection with {addr}")
        clientThread = threading.Thread(target=handle_client, args=(clientSocket, addr))
        clientThread.start()
        print(f"[SERVER] Active connections: {len(connectedClients) + 1}")


def handle_client(clientSocket, addr):
    """handle the communication with a connected client:
    - ask for client name (unique)
    - send a welcome message
    - accept messages/commands from the client
    - process the messages/commands accordingly
    - handle client disconnection"""

    try:
        name = ask_client_name(clientSocket)
        connectedClients[name] = clientSocket #store the client name:socket mapping in a global dictionary
        print(f"[SERVER] {name} : {addr} has joined the chat")
        welcomeMessage = f"Welcome to the chat, {name}!\n"
        showCommands = """\tShow active clients: /show
        Send to specific client: /msg <client_name> <message>
        Send to all clients: /all <message>
        Show these commands: /help
        Exit chat: /exit"""
        helperApp.send_msg(clientSocket, welcomeMessage + showCommands)
        
        while True:
            data = helperApp.recv_msg(clientSocket)
            if not data:
                break
            process_data(data, clientSocket, name)

    except ConnectionResetError:
        print(f"[SERVER] Connection with client: {addr} was reset")
    finally:
        clientSocket.close()
        del connectedClients[name]
        print(f"[SERVER] {name} : {addr} has left the chat, connection closed")
        print(f"[SERVER] Active connections: {len(connectedClients)}")


def ask_client_name(clientSocket):
    """ask the client for a unique name, return the name when accepted"""

    askName = "What's your name?"
    while True:
        helperApp.send_msg(clientSocket, askName)
        name = helperApp.recv_msg(clientSocket)
        if name not in connectedClients.keys(): #verify that the name is unique (not in the dict)
            return name
        askName = "Name already taken. Please provide another name: "


def process_data(data, clientSocket, senderName):
    """process the received data, act accordingly based on the command"""

    parts = data.strip().split(' ', 1)
    if not parts:
        return None
    command = parts[0]
    if command == "/show":
        show_active_clients(clientSocket)
    elif command == "/help":
        show_help(clientSocket)
    elif command == "/all":
        broadcast_message(parts, clientSocket, senderName)
    elif command == "/msg":
        direct_message(parts, clientSocket, senderName)
    else:
        helperApp.send_msg(clientSocket, "[SERVER] Unknown command. Type /help for a list of commands.")
  

def direct_message(parts, clientSocket, senderName):
    """send a direct message to a specific client"""

    if len(parts) < 2: #no arguments after /msg
        helperApp.send_msg(clientSocket, "[SERVER] Usage: /msg <client_name> <message>")
        return
    
    parts = parts[1].split(' ', 1)
    if len(parts) < 2: #missing message part
        helperApp.send_msg(clientSocket, "[SERVER] Usage: /msg <client_name> <message>")
        return
    
    destinationName = parts[0]
    message = parts[1]
    if destinationName in connectedClients: #check if the destination client exists
        destinationSocket = connectedClients[destinationName]
        helperApp.send_msg(destinationSocket, f"[DM from {senderName}] {message}")
    else:
        helperApp.send_msg(clientSocket, f"[SERVER] Client: {destinationName} is not found. Use /show to see active clients.")


def broadcast_message(parts, clientSocket, senderName):
    """send a message to all connected clients except the sender"""

    if len(parts) < 2: #missing message part
        helperApp.send_msg(clientSocket, "[SERVER] Usage: /all <message>")
        return
    
    message = parts[1]

    for destinationSocket in connectedClients.values(): #send to all clients except sender
        if destinationSocket != clientSocket:
            helperApp.send_msg(destinationSocket, f"[Broadcast from {senderName}] {message}")


def show_active_clients(clientSocket):
    """send the list of active clients to the requesting client"""

    activeClients = ", ".join(connectedClients.keys())
    response = f"[SERVER] Active clients: [{activeClients}]"
    helperApp.send_msg(clientSocket, response)


def show_help(clientSocket):
    """send the list of available commands to the requesting client"""

    helpMessage = """[SERVER] Available commands:
    Show active clients: /show
    Send to specific client: /msg <client_name> <message>
    Send to all clients: /all <message>
    Show these commands: /help
    Exit chat: /exit"""
    helperApp.send_msg(clientSocket, helpMessage)


if __name__ == "__main__":
    main()