# Tic-Tac-Toe WASM

A simple Tic-Tac-Toe game implemented in Rust and compiled to WebAssembly, featuring an AI opponent using the Minimax algorithm.

## Features

- WebAssembly module written in Rust
- Minimax AI with alpha-beta pruning for efficient optimal play
- Adjustable difficulty levels (Easy, Medium, Hard) via search depth
- Hint feature to suggest best moves
- Simple web interface with DOM grid
- wasm-bindgen for JavaScript interop

## Usage

### Online
Visit https://markusisaksson1982.github.io/projects/tic-tac-toe-wasm/ to play the game directly in your browser.

### Locally
1. Download or clone the repository: `git clone https://github.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io.git`
2. Navigate to `projects/tic-tac-toe-wasm/`
3. Open `index.html` in a modern web browser that supports WebAssembly.

### Development
To modify and rebuild:
1. Install Rust: https://rustup.rs/
2. Install wasm-pack: `cargo install wasm-pack`
3. Run `wasm-pack build --target web` in the project directory
4. Serve with a local server and open `index.html`

## API Documentation

### TicTacToe

- `new()`: Creates a new game instance.
- `get_board()`: Returns the current board as an array of i32 (0=empty, 1=player, 2=AI).
- `make_move(position: usize)`: Makes a move at the given position (0-8). Returns true if successful.
- `check_win()`: Returns the winner (1=player, 2=AI, 0=none).
- `check_draw()`: Returns true if the game is a draw.
- `get_best_move(max_depth: i32)`: Returns the best move for AI with given depth limit. Returns usize::MAX if game over.

## Deployment

The project uses GitHub Actions for automatic deployment to GitHub Pages. Push to the main branch to trigger a build and deploy. The workflow builds the WASM module and deploys the site.

For manual deployment:
1. Build: `wasm-pack build --target web`
2. Commit and push the `pkg/` directory and static files.
3. Enable GitHub Pages in repository settings, set source to GitHub Actions.

## New Features

- **Alpha-Beta Pruning**: Implemented to reduce computation time, making the AI faster while maintaining optimality.
- **Difficulty Levels**: Select Easy (depth 3), Medium (6), or Hard (9) to adjust AI strength.
- **Hint Button**: Highlights the best move for the current player without making it.

## Testing

After building, test the AI by playing multiple games. The AI should never lose on Hard difficulty. Use the Hint feature to verify optimal moves. Performance should be instant due to pruning.

## Extensions

- **Game History**: Implement undo functionality and game replay.
- **Multiplayer**: Add online multiplayer support.
- **Themes**: Add different visual themes for the board.
- **Larger Boards**: Extend to 4x4 or larger grids with heuristic evaluation.

## Development

To modify the Rust code, edit `src/lib.rs` and rebuild with `wasm-pack build --target web`.

For the web interface, edit `index.html`.