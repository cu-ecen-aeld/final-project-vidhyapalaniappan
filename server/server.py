##********************************************************************************************************************************************************
## File name        : server.py
## ​Description      : Code to integrate LCD, numpad and fingerprint sesnor 
## File​ ​Author​ ​Name : Vidhya. PL & Ashwin Ravindra
## Date             : 12/13/2023
## **********************************************************************************************************************************************************

##Importing the necessary header files
import socket

HOST = "169.254.59.104"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('Server started')
    s.bind((HOST, PORT))   #binding to the host
    s.listen()             #listening for connection requests from client

    while True: 
        conn, addr = s.accept()   #accepting connection from client
        with conn:
            while True:
                data = conn.recv(1024)   #recieving data from client
                if not data:
                    break
                print(f"Received from client {addr}: {data.decode('utf-8')}")

                try:
                    conn.sendall(data)  #sending data back
                except (BrokenPipeError, ConnectionResetError):  
                    break

