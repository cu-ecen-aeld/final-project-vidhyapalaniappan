import socket

HOST = "169.254.59.104"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('Server started')
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        #print(f"Connected by {addr}")

        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    #print(f"Connection closed by {addr}")
                    break
                print(f"Received from client {addr}: {data.decode('utf-8')}")

                try:
                    conn.sendall(data)
                except (BrokenPipeError, ConnectionResetError):
                    #print(f"Connection closed by {addr}")
                    break

