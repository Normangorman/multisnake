import socket
import sys
import json

class SnakeClient():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # SOCK_STREAM means a TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def sendSnakeDataGetResponse(self, snakeRequest):
        request_string = json.dumps(snakeRequest)
        print("SnakeClient.sendSnakeData: request_string = " + request_string)
            
        try:
            # Connect to server and send data
            self.sock.connect((self.host, self.port))
            self.sock.sendall(bytes(request_string + "\n", "utf-8"))

            # Receive data from the server and shut down
            response = str(self.sock.recv(1024), "utf-8")
        finally:
            self.sock.close()

        return response
