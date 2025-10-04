use wasm_bindgen::prelude::*;

// Board representation: 0 = empty, 1 = player (X), 2 = AI (O)
#[wasm_bindgen]
pub struct TicTacToe {
    board: [i32; 9],
    current_player: i32,
}

#[wasm_bindgen]
impl TicTacToe {
    #[wasm_bindgen(constructor)]
    pub fn new() -> TicTacToe {
        TicTacToe {
            board: [0; 9],
            current_player: 1, // Player starts
        }
    }

    #[wasm_bindgen]
    pub fn get_board(&self) -> Vec<i32> {
        self.board.to_vec()
    }

    #[wasm_bindgen]
    pub fn make_move(&mut self, position: usize) -> bool {
        if position >= 9 || self.board[position] != 0 {
            return false;
        }
        self.board[position] = self.current_player;
        self.current_player = if self.current_player == 1 { 2 } else { 1 };
        true
    }

    #[wasm_bindgen]
    pub fn check_win(&self) -> i32 {
        check_win_for_board(&self.board)
    }

    #[wasm_bindgen]
    pub fn check_draw(&self) -> bool {
        is_draw(&self.board)
    }

    #[wasm_bindgen]
    pub fn get_best_move(&self, max_depth: i32) -> usize {
        if self.check_win() != 0 || self.check_draw() {
            return usize::MAX; // Game over
        }

        let mut best_score = i32::MIN;
        let mut best_move = usize::MAX;
        let ai_player = 2;

        for i in 0..9 {
            if self.board[i] == 0 {
                let mut board_copy = self.board;
                board_copy[i] = ai_player;
                let score = minimax(&board_copy, 1, false, i32::MIN, i32::MAX, ai_player, max_depth);
                if score > best_score {
                    best_score = score;
                    best_move = i;
                }
            }
        }
        best_move
    }
}

fn check_win_for_board(board: &[i32; 9]) -> i32 {
    let win_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ];

    for pattern in win_patterns.iter() {
        if board[pattern[0]] != 0 &&
           board[pattern[0]] == board[pattern[1]] &&
           board[pattern[1]] == board[pattern[2]] {
            return board[pattern[0]];
        }
    }
    0
}

fn is_draw(board: &[i32; 9]) -> bool {
    board.iter().all(|&x| x != 0) && check_win_for_board(board) == 0
}

fn minimax(
    board: &[i32; 9],
    depth: i32,
    is_maximizing: bool,
    mut alpha: i32,
    mut beta: i32,
    ai_player: i32,
    max_depth: i32,
) -> i32 {
    let winner = check_win_for_board(board);
    if winner == ai_player {
        return 10 - depth; // Prefer quicker wins
    } else if winner != 0 {
        return -10 + depth; // Prefer delaying losses
    } else if is_draw(board) {
        return 0;
    }

    if depth >= max_depth {
        return 0; // Heuristic: neutral
    }

    if is_maximizing {
        let mut best_score = i32::MIN;
        for i in 0..9 {
            if board[i] == 0 {
                let mut board_copy = *board;
                board_copy[i] = ai_player;
                let score = minimax(&board_copy, depth + 1, false, alpha, beta, ai_player, max_depth);
                best_score = best_score.max(score);
                alpha = alpha.max(score);
                if beta <= alpha {
                    break; // Prune
                }
            }
        }
        best_score
    } else {
        let mut best_score = i32::MAX;
        for i in 0..9 {
            if board[i] == 0 {
                let mut board_copy = *board;
                board_copy[i] = if ai_player == 2 { 1 } else { 2 }; // Opponent
                let score = minimax(&board_copy, depth + 1, true, alpha, beta, ai_player, max_depth);
                best_score = best_score.min(score);
                beta = beta.min(score);
                if beta <= alpha {
                    break; // Prune
                }
            }
        }
        best_score
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_check_win() {
        let mut board = [0; 9];
        board[0] = 1; board[1] = 1; board[2] = 1;
        assert_eq!(check_win_for_board(&board), 1);

        board = [2, 0, 0, 2, 0, 0, 2, 0, 0];
        assert_eq!(check_win_for_board(&board), 2);

        board = [1, 2, 1, 2, 1, 2, 2, 1, 2];
        assert_eq!(check_win_for_board(&board), 0);
    }

    #[test]
    fn test_is_draw() {
        let board = [1, 2, 1, 2, 1, 2, 2, 1, 2];
        assert!(is_draw(&board));

        let board = [1, 0, 0, 0, 0, 0, 0, 0, 0];
        assert!(!is_draw(&board));
    }

    #[test]
    fn test_minimax() {
        let board = [0; 9];
        let score = minimax(&board, 0, true, i32::MIN, i32::MAX, 2, 9);
        assert_eq!(score, 0); // Should be draw for optimal play
    }
}

}