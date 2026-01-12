import subprocess
import re

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