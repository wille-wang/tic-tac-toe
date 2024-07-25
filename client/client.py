import json
import socket


class Client:
    def __init__(self, host, port) -> None:
        # connect to the server
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print(f"Connected to the server: {host}:{port}.")

    def send_req(self, req: dict):
        """send a request to the server

        Args:
            req (dict): request sent to the server
        """
        try:
            self.sock.sendall(json.dumps(req).encode())
            print(f"Sent request to the server: {req}")
        except Exception:
            print(f"Failed to send the request to the server.")

    def received_res(self) -> dict:
        """receive the response from the server

        Returns:
            dict: decoded response from the servers
        """
        try:
            res = self.sock.recv(1_000)
            res = json.loads(res.decode())
            print(f"Received response from the server: {res}")
            return res
        except json.JSONDecodeError:
            print(f"Disconnected from the server.")
            self.sock.close()
            exit(1)
        except Exception:
            print(f"Failed to receive the response from the server.")
            self.sock.close()
            exit(1)
