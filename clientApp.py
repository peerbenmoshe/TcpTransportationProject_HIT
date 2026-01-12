import socket
import threading
from serverApp import HOST, PORT

def main():
    start_client()

def start_client():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        name = login(clientSocket)
        stopEvent = threading.Event()
        listenerThread = threading.Thread(target=listen_for_messages, args=(clientSocket, name, stopEvent), daemon=True)
        listenerThread.start()

        while True:
            message = input("[CLIENT] Enter a message: ")
            if message.lower() == "/exit":
                print("[CLIENT] Exiting...")   
                break
            clientSocket.sendall(message.encode("utf-8"))

    except ConnectionRefusedError:
        print(f"[CLIENT] Could not connect to the server: {HOST}:{PORT}")
    except Exception as e:
        print(f"[CLIENT] An error occurred: {e}")
    finally:
        clientSocket.close()
        stopEvent.set()
        listenerThread.join()
        


def login(clientSocket):
    clientSocket.connect((HOST, PORT))
    print(f"[CLIENT] Connected to the server: {HOST}:{PORT}")
    serverPrompt = clientSocket.recv(1024).decode("utf-8")
    name = input(f"[CLIENT] {serverPrompt} ")
    while True:
        clientSocket.sendall(name.encode("utf-8"))
        response = clientSocket.recv(1024).decode("utf-8")
        if "Name already taken" not in response:
            break
        name = input(f"[CLIENT] {response}")
    print(f"[CLIENT] {response}")
    return name


def listen_for_messages(clientSocket, name, stopEvent):
    while not stopEvent.is_set():
        try:
            message = clientSocket.recv(1024).decode("utf-8")
            if message:
                if "[SERVER]" in message:
                    print(f"\n{message}\n", end="")
                else:
                    print(f"\n{message}\n[CLIENT] Enter a message: ", end="")
            else:
                break
        except ConnectionAbortedError:
            break
        except Exception as e:
            print(f"[CLIENT] Error receiving message from server: {e}")
            break
        stopEvent.wait(0.1)


if __name__ == "__main__":
    main()