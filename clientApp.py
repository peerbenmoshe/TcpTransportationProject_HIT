import socket
from serverApp import HOST, PORT

def main():
    start_client()

def start_client():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientSocket.connect((HOST, PORT))
        print(f"[CLIENT] Connected to the server: {HOST}:{PORT}")
        welcomeMessage = clientSocket.recv(1024).decode("utf-8")
        print(f"[CLIENT] [SERVER RESPONSE] {welcomeMessage}")

        while True:
            message = input("[CLIENT] Enter message to send (or 'exit' to quit): ")
            if message.lower() == "exit":
                print("[CLIENT] Exiting...")
                break
            clientSocket.sendall(message.encode("utf-8"))
            response = clientSocket.recv(1024).decode("utf-8")
            print(f"[CLIENT] [SERVER RESPONSE] {response}")


    except ConnectionRefusedError:
        print(f"[CLIENT] Could not connect to the server: {HOST}:{PORT}")
    finally:
        clientSocket.close()

if __name__ == "__main__":
    main()