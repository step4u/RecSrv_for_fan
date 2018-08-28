import socket               # Import socket module

s = socket.socket()         # Create a socket object
# host = socket.gethostname() # Get local machine name
host = "192.168.0.8"
port = 10000                # Reserve a port for your service.

s.connect((host, port))
print(s.recv(1024).decode())
s.close                     # Close the socket when done
