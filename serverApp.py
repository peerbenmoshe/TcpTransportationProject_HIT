import socket
import threading
import helperApp

HOST = helperApp.get_host_ip()
PORT = 12345

def main():
    global connectedClients
    connectedClients = {}
    start_server()

def start_server():
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
    try:
        name = ask_client_name(clientSocket)
        connectedClients[name] = clientSocket
        print(f"[SERVER] {name} : {addr} has joined the chat")
        welcomeMessage = f"Welcome to the chat, {name}!\n"
        showCommands = """\tShow active clients: /show
        Send to specific client: /msg <client_name> <message>
        Send to all clients: /all <message>
        Show these commands: /help
        Exit chat: /exit"""
        clientSocket.sendall((welcomeMessage+showCommands).encode("utf-8"))
        
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            process_data(data.decode("utf-8"), clientSocket, name)

    except ConnectionResetError:
        print(f"[SERVER] Connection with client: {addr} was reset")
    finally:
        clientSocket.close()
        del connectedClients[name]
        print(f"[SERVER] {name} : {addr} has left the chat, connection closed")
        print(f"[SERVER] Active connections: {len(connectedClients)}")


def ask_client_name(clientSocket):
    askName = "What's your name?"
    while True:
        clientSocket.sendall(askName.encode("utf-8"))
        name = clientSocket.recv(1024).decode("utf-8")
        if name not in connectedClients.keys():
            return name
        askName = "Name already taken. Please provide another name: "


def process_data(data, clientSocket, senderName):
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
        clientSocket.sendall("[SERVER] Unknown command. Type /help for a list of commands.".encode("utf-8"))


    

def direct_message(parts, clientSocket, senderName):
    if len(parts) < 2:
        clientSocket.sendall("[SERVER] Usage: /msg <client_name> <message>".encode("utf-8"))
        return
    
    parts = parts[1].split(' ', 1)
    if len(parts) < 2:
        clientSocket.sendall("[SERVER] Usage: /msg <client_name> <message>".encode("utf-8"))
        return
    
    destinationName = parts[0]
    message = parts[1]
    if destinationName in connectedClients:
        destinationSocket = connectedClients[destinationName]
        destinationSocket.sendall(f"[DM from {senderName}] {message}".encode("utf-8"))
    else:
        clientSocket.sendall(f"[SERVER] Client: {destinationName} is not found. Use /show to see active clients.".encode("utf-8"))


def broadcast_message(parts, clientSocket, senderName):
    if len(parts) < 2:
        clientSocket.sendall("[SERVER] Usage: /all <message>".encode("utf-8"))
        return
    
    message = parts[1]
    if message.strip() == "":
        clientSocket.sendall("[SERVER] Message cannot be empty.".encode("utf-8"))
        return
    for destinationSocket in connectedClients.values():
        if destinationSocket != clientSocket:
            destinationSocket.sendall(f"[Broadcast from {senderName}] {message}".encode("utf-8"))


def show_active_clients(clientSocket):
    activeClients = ", ".join(connectedClients.keys())
    response = f"[SERVER] Active clients: [{activeClients}]"
    clientSocket.sendall(response.encode("utf-8"))


def show_help(clientSocket):
    helpMessage = """[SERVER] Available commands:
    Show active clients: /show
    Send to specific client: /msg <client_name> <message>
    Send to all clients: /all <message>
    Show these commands: /help
    Exit chat: /exit"""
    clientSocket.sendall(helpMessage.encode("utf-8"))
        

if __name__ == "__main__":
    main()