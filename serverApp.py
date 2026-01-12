import socket
import threading
import helperApp

HOST = helperApp.get_host_ip()
PORT = 12345

def main():
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
        print(f"[SERVER] Active connections: {threading.active_count() - 1}")


def handle_client(clientSocket, addr):
    print(f"[SERVER] Connected to {addr}")
    try:
        welcomeMessage = "You are connected to the server!"
        clientSocket.sendall(welcomeMessage.encode("utf-8"))
        
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            print(f"[SERVER] Received from {addr}: {data.decode("utf-8")}")
            serverResponse = f"I received: {data.decode("utf-8").upper()}"
            clientSocket.sendall(serverResponse.encode("utf-8"))  # Echo back the received data
    except ConnectionResetError:
        print(f"[SERVER] Connection with client: {addr} was reset")
    finally:
        clientSocket.close()
        print(f"[SERVER] Connection with client: {addr} closed")



    

if __name__ == "__main__":
    main()