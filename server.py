import argparse
import socket
import threading
import json

waiting_players = []

def handle_req(conn: socket.socket):
    """handle requests from clients

    Args:
        conn (socket.socket): _description_
    """
    # receive the request from the client
    request = conn.recv(1_000)
    request = json.loads(request.decode())
    waiting_players.append(request["username"])

    # send the response back to the client
    response = "ACK"
    conn.sendall(response.encode())

def start_server(host: str, port: int):
    """start the multithreaded server

    Args:
        host (str): hostname or IP address of the server
        port (int): port number of the server to listen on
    """
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        # create a new thread for each client
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(
                target=handle_req,
                args=(conn, addr),
            )
            thread.start()

if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=44444)
    args = parser.parse_args()

    # start the server
    start_server(host=args.host, port=args.port)