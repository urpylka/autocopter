def check_internet():
    import socket
    try:
        socket.gethostbyaddr('ya.ru')
    except socket.gaierror:
        return False
    return True
def wait_internet():
    while not check_internet():
        import time
        time.sleep(1)
def get_ip():
    import http.client
    conn = http.client.HTTPConnection("smirart.ru")
    conn.request("GET", "/ip")
    return conn.getresponse().read()