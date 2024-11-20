from Chessnut import Game
import random

# Define piece values for material evaluation
PIECE_VALUES = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0, ' ': 0}

def minimax(game, depth, is_maximizing, alpha, beta):
    """
    Minimax algorithm with Alpha-Beta pruning.

    Args:
        game: An instance of the Chessnut Game class.
        depth: The remaining depth to search.
        is_maximizing: True if it's the maximizing player's turn, False otherwise.
        alpha: The best value that the maximizing player can guarantee.
        beta: The best value that the minimizing player can guarantee.

    Returns:
        A tuple (best_score, best_move).
    """
    # Base case: Return evaluation if at depth 0 or the game is over
    if depth == 0 or game.status in (Game.CHECKMATE, Game.STALEMATE):
        return evaluate_board(game), None

    legal_moves = list(game.get_moves())
    if is_maximizing:
        best_score = -float('inf')
        best_move = None
        for move in legal_moves:
            g = Game(game.get_fen())
            g.apply_move(move)
            score, _ = minimax(g, depth - 1, False, alpha, beta)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:  # Prune the branch
                break
        return best_score, best_move
    else:
        best_score = float('inf')
        best_move = None
        for move in legal_moves:
            g = Game(game.get_fen())
            g.apply_move(move)
            score, _ = minimax(g, depth - 1, True, alpha, beta)
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:  # Prune the branch
                break
        return best_score, best_move

def evaluate_board(game):
    """
    Evaluate the current board state.

    Args:
        game: An instance of the Chessnut Game class.

    Returns:
        A numerical score where positive values favor the maximizing player.
    """
    fen = game.get_fen()
    board = fen.split()[0]  # Get the board part of the FEN
    score = 0
    for char in board:
        if char.isalpha():
            piece_value = PIECE_VALUES.get(char.lower(), 0)
            score += piece_value if char.isupper() else -piece_value  # Uppercase: maximizing, lowercase: minimizing
    return score

def chess_bot(obs):
    """
    Improved chess bot using Minimax with Alpha-Beta pruning.

    Args:
        obs: An object with a 'board' attribute representing the current board state as a FEN string.

    Returns:
        A string representing the chosen move in UCI notation (e.g., "e2e4")
    """
    # Initialize game state
    game = Game(obs.board)

    # Use Minimax to find the best move
    _, best_move = minimax(game, depth=3, is_maximizing=True, alpha=-float('inf'), beta=float('inf'))

    # Return the best move found by Minimax
    return best_move
