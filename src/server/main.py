import argparse
from server import Server


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=44444)
    args = parser.parse_args()

    # Start the server
    server = Server(host=args.host, port=args.port)
