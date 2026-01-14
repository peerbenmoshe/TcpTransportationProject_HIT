import subprocess
import re
import socket

HEADER_LENGTH = 10

#relevant only for Widndows
def get_host_ip():
    """
    Run `ipconfig` and extract the first non-loopback IPv4 address.
    Returns '127.0.0.1' if none found or on error.
    """
    try:
        output = subprocess.run("powershell -Command ipconfig | findstr IPv4", capture_output=True, text=True, check=True, encoding="utf-8").stdout
    except Exception:
        return "127.0.0.1"

    # Match lines like:
    #    IPv4 Address. . . . . . . . . . . : 192.168.1.198
    # or older/alternate labels like "IP Address"
    matches = re.findall(r'(?:IPv4[^\:]*:|IP Address[^\:]*:)\s*([\d\.]+)', output, flags=re.IGNORECASE)
    for ip in matches:
        if ip and not ip.startswith(("127.", "169.")):
            return ip
    return "127.0.0.1"


def send_msg(sock, message):
    """
    Prefixes the message with a fixed-length header indicating its size,
    then sends the header + message.
    """
    message = message.encode("utf-8")
    # Create a header of length 10, e.g., "5         " or "1024      "
    header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
    sock.sendall(header + message)
    

def recv_msg(sock):
    """
    Reads the fixed-length header first to determine message size,
    then loops until the full message body is received.
    """
    try:
        # 1. Read the header to get the length
        header = sock.recv(HEADER_LENGTH)
        if not header:
            return None # Connection closed
        
        message_length = int(header.decode("utf-8").strip())
        
        # 2. Loop until we have the full message body
        data = b""
        while len(data) < message_length:
            packet = sock.recv(message_length - len(data))
            if not packet:
                return None # Connection interrupted
            data += packet
            
        return data.decode("utf-8")
        
    except Exception as e:
        return None