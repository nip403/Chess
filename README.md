# Chess
A Python 3.7 chess library.

# Known bugs

# Todo
### Short term
- finish graphics engine
- add usage, requirements
- PGN/FEN generator
  - allow (complete) FEN input to update game
  - add commands in move function for above (e.g. "pgn [move x]", "fen", "inputfen x")
- timer (+ intervals)
  - create graphics banner
- cmd line integration, refreshing cmd line each move (os.system("cls))
  - timer
- titlescreen for graphics engine
- algebraic notation & other notation
  - conversion from input to standard notation
  - comprehensive notation i.e. +/-, !, ? etc

### Long term
- enable multiplayer using sockets/podsixnet
- implement stockfish
  - move recommendations
  - play against diff. versions
- nn model
