from Chessnut import Game
import random
import time
from concurrent.futures import ThreadPoolExecutor

# Define piece values for material evaluation
PIECE_VALUES = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0, ' ': 0}

# Define an opening book
OPENINGS = {
    # King's Pawn Opening
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": "e2e4",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1": "e7e5",

    # Sicilian Defense
    "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "c7c5",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2": "g1f3",

    # French Defense
    "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "e7e6",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2": "d2d4",

    # Queen's Gambit
    "rnbqkbnr/pppppppp/8/8/8/3P4/PPP1PPPP/RNBQKBNR b KQkq - 0 1": "d7d5",
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d5 0 2": "c2c4",
    "rnbqkbnr/pp1ppppp/8/2p5/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2": "e7e6",

    # King's Indian Defense
    "rnbqkbnr/pppppppp/8/8/8/3P4/PPP1PPPP/RNBQKBNR b KQkq - 0 1": "g8f6",
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq f6 0 2": "c2c4",
    "rnbqkbnr/pppppppp/8/8/2PP4/8/PP3PPP/RNBQKBNR b KQkq c3 0 2": "g7g6",

    # Caro-Kann Defense
    "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "c7c6",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2": "d2d4",

    # Italian Game
    "rnbqkbnr/pppppppp/8/8/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": "b8c6",
    "r1bqkbnr/pppppppp/2n5/8/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3": "f1c4",

    # Ruy-Lopez
    "rnbqkbnr/pppppppp/8/8/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": "b8c6",
    "r1bqkbnr/pppppppp/2n5/1B6/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 2 3": "a7a6",

    # English Opening
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": "c2c4",
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3 0 1": "e7e5",

    # Scandinavian Defense
    "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "d7d5",
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 2": "e4e5",

    # Alekhine Defense
    "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "g8f6",
    "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq f6 0 2": "e4e5",
}

transposition_table = {}

def evaluate_capture(game, move):
    target_square = Game.xy2i(move[2:4])
    target_piece = game.board.get_piece(target_square).lower()
    return PIECE_VALUES.get(target_piece, 0)

def prioritize_promotion(moves):
    promotion_moves = [move for move in moves if move[-1].lower() in ('q', 'r', 'b', 'n')]
    return max(promotion_moves, key=lambda move: PIECE_VALUES.get(move[-1].lower(), 9), default=None)

def minimax(game, depth, is_maximizing, alpha, beta, start_time, time_limit=0.9):
    elapsed_time = time.time() - start_time
    if elapsed_time >= time_limit or depth == 0 or game.status in (Game.CHECKMATE, Game.STALEMATE):
        return evaluate_board_with_cache(game), None

    legal_moves = sorted(game.get_moves(), key=lambda move: evaluate_capture(game, move), reverse=True)
    best_score, best_move = (-float('inf'), None) if is_maximizing else (float('inf'), None)

    for move in legal_moves:
        g = Game(game.get_fen())
        g.apply_move(move)
        score, _ = minimax(g, depth - 1, not is_maximizing, alpha, beta, start_time, time_limit)
        if is_maximizing and score > best_score or not is_maximizing and score < best_score:
            best_score, best_move = score, move
        alpha, beta = (max(alpha, best_score), beta) if is_maximizing else (alpha, min(beta, best_score))
        if beta <= alpha:
            break

    return best_score, best_move

def evaluate_board_with_cache(game):
    fen = game.get_fen()
    if fen not in transposition_table:
        transposition_table[fen] = evaluate_board(game)
    return transposition_table[fen]

def evaluate_board(game):
    board = game.get_fen().split()[0]
    return sum(PIECE_VALUES.get(char.lower(), 0) * (1 if char.isupper() else -1) for char in board if char.isalpha())

def iterative_deepening(game, max_depth, time_limit, start_time):
    best_move = None
    for depth in range(1, max_depth + 1):
        remaining_time = time_limit - (time.time() - start_time)
        if remaining_time <= 0:
            break
        try:
            _, move = minimax(game, depth, True, -float('inf'), float('inf'), start_time, remaining_time)
            if move:
                best_move = move
        except TimeoutError:
            break
    return best_move if best_move else fallback_move(game)

def fallback_move(game):
    legal_moves = list(game.get_moves())
    return random.choice(legal_moves) if legal_moves else None

def chess_bot(obs):
    start_time = time.time()
    game = Game(obs.board)

    if game.get_fen() in OPENINGS:
        return OPENINGS[game.get_fen()]

    max_depth = min(3, int(0.5 / 0.1))  # Example: Adjust max depth based on allocated time

    return iterative_deepening(game, max_depth=max_depth, time_limit=0.5, start_time=start_time)
