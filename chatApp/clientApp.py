import socket
import threading
import time
#if client and server are on the same machine, import HOST and PORT from serverApp.py (will appear in loopback interface)
from serverApp import HOST, PORT
import helperApp

#if running on different machines, enter HOST IP manually (from the serverApp.py output) (will appear in non-loopback interface)
# HOST = " . . . . "
# PORT = 12345
#if encountering issues, try setting HOST to 127.0.0.1 on both client and server

def main():
    start_client()

def start_client() -> None:
    """start the client, connect to the server, handle user input and incoming messages"""

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        login(clientSocket)
        stopEvent = threading.Event() #event to signal listener thread to stop
        listenerThread = threading.Thread(target=listen_for_messages, args=(clientSocket, stopEvent), daemon=True)
        listenerThread.start()

        while True:
            message = input("[CLIENT] Enter a message: ")
            if message.lower() == "/exit":
                print("[CLIENT] Exiting...")   
                break
            helperApp.send_msg(clientSocket, message)
            time.sleep(0.1)

    except ConnectionRefusedError:
        print(f"[CLIENT] Could not connect to the server: {HOST}:{PORT}")
    except Exception as e:
        print(f"[CLIENT] An error occurred: {e}")
    finally: #close gracefully, stop listener thread when server finished sending messages
        clientSocket.shutdown(socket.SHUT_WR)
        while not stopEvent.is_set():
            time.sleep(0.1)
        listenerThread.join()
        clientSocket.close()
        


def login(clientSocket: socket.socket) -> None:
    """handle the login process:
    - receive prompt from server
    - send unique client name
    - receive welcome message"""

    clientSocket.connect((HOST, PORT))
    print(f"[CLIENT] Connected to the server: {HOST}:{PORT}")
    serverPrompt = helperApp.recv_msg(clientSocket)
    name = input(f"[CLIENT] {serverPrompt} ")
    while True:
        helperApp.send_msg(clientSocket, name)
        response = helperApp.recv_msg(clientSocket)
        if "Name already taken" not in response:
            break
        name = input(f"[CLIENT] {response}")
    print(f"[CLIENT] {response}")


def listen_for_messages(clientSocket: socket.socket, stopEvent: threading.Event) -> None:
    """listen for incoming messages from the server and print them"""

    while not stopEvent.is_set():
        try:
            message = helperApp.recv_msg(clientSocket)
            if message:
                if "[SERVER]" in message: #if it's a server message, it means i sent a command, so print without input prompt
                    print(f"\n{message}\n", end="")
                else: #if it's a message from another client, print it and re-print the input prompt
                    print(f"\n{message}\n[CLIENT] Enter a message: ", end="")
            else:
                stopEvent.set() #server has closed the connection
        except ConnectionAbortedError:
            break
        except Exception as e:
            print(f"[CLIENT] Error receiving message from server: {e}")
            break
        stopEvent.wait(0.1)


if __name__ == "__main__":
    main()