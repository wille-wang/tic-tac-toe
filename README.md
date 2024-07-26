# Distributed Tic-Tac-Toe

This repository aims to build a distributed Tic-Tac-Toe game, which features a graphical user interface (GUI) built with [PySide6](https://pypi.org/project/PySide6/) for the client, and a thread-per-connection multithreaded server to handle game logic and communication between players.

The server maintains state in-memory, without storing information in persistent storage.

## Components
- **client side**
  - `main.py`: entry point of the server side
  - `board.py`: contains the `Board` class that provides the GUI for the Tic-Tac-Toe game, including game board interaction and status updates
  - `client.py`: contains the `Client` class which manages communication with the server
- **server side**
  - `main.py`: entry point of the client side
  - `server.py`: contains the `Server` class that handles incoming client connections, processes game requests, and manages game state and player interactions
  - `database.py`: contains the `Database` class that maintains player connections, waiting players, and ongoing games
  - `game.py`: contains the `Game` class that represents the game state, processes moves, and determines the game outcome

## Installation and Usage

1. Clone this repository:

```sh
git clone https://github.com/wille-wang/tic-tac-toe
cd {repo_dir}
```

2. Install dependencies:

```sh
pip install -r requirements.txt
```

3. Run the server:

```sh
python server/main.py --host {hostname} --port {port}
```

- `host`: (*optional*) hostname of the server (default: `localhost`)
- `post`: (*optional*) port number of the server (default: `44444`)


4. Run the client(s):

```sh
python client/main.py --username {username} --host {host} --port {port}
```

- `username`: (***compulsory***) username for the player
- `host`: (*optional*) hostname of the server (default: `localhost`)
- `port`: (*optional*) port number of the server (default: `44444`)
