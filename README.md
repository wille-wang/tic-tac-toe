# Distributed Tic-Tac-Toe

This repository contains a distributed Tic-Tac-Toe game featuring a graphical user interface (GUI) built with [PySide6](https://pypi.org/project/PySide6/) on the client side, and a multithreaded server with a thread-per-connection architecture to manage game logic and player communication.

The server maintains the game state in memory without persistent storage.

![GUI](/img/gui.png)

## Components

- **client side**
  - `main.py`: entry point of the server side
  - `board.py`: defines the `Board` class, responsible for rendering the GUI, managing game board interactions, and updating game status
  - `client.py`: contains the `Client` class that handles communication with the server
- **server side**
  - `main.py`: entry point of the client side
  - `server.py`: defines the `Server` class to handle client connections, process game-related requests, and manage the game state and player interactions
  - `database.py`: contains the `Database` class, which manages player connections, waiting lists, and active games
  - `game.py`: contains the `Game` class that represents the game state, processes moves, and determines the game outcome

## Installation and Usage

1. Clone this repository and install dependencies:

```sh
git clone https://github.com/wille-wang/tic-tac-toe
cd tic-tac-toe
pip install -r requirements.txt
```

2. Run the server:

```sh
python src/server/main.py \
  --host [hostname] \
  --port [port]
```

- `host`: (_optional_) hostname of the server (default: `localhost`)
- `post`: (_optional_) port number of the server (default: `44444`)

3. Run the client(s):

```sh
python src/client/main.py \
  --username <username> \
  --host [hostname] \
  --port [port]
```

- `username`: (**_compulsory_**) username for the player
- `host`: (_optional_) hostname of the server (default: `localhost`)
- `port`: (_optional_) port number of the server (default: `44444`)
