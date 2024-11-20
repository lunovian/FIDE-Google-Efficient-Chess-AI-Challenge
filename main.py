from Chessnut import Game
import random

# Define piece values for material evaluation
PIECE_VALUES = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0, ' ': 0}

# Define central squares for positional evaluation
CENTER_SQUARES = {'d4', 'd5', 'e4', 'e5'}

def evaluate_capture(game, move):
    """
    Evaluate the value of a capture move based on the piece being captured.

    Args:
        game: An instance of the Chessnut Game class.
        move: A UCI string representing a move (e.g., "e2e4").

    Returns:
        An integer score representing the value of the captured piece.
    """
    target_square = Game.xy2i(move[2:4])  # Convert target square to board index
    target_piece = game.board.get_piece(target_square).lower()  # Get the piece at the target square
    return PIECE_VALUES.get(target_piece, 0)  # Return its value

def evaluate_position(move):
    """
    Evaluate a move based on positional control (center squares).

    Args:
        move: A UCI string representing a move (e.g., "e2e4").

    Returns:
        A score (higher values for moves toward the center).
    """
    target_square = move[2:4]
    return 1 if target_square in CENTER_SQUARES else 0

def evaluate_king_safety(game, move):
    """
    Evaluate king safety for a move.

    Args:
        game: The current game state.
        move: A move in UCI format.

    Returns:
        A penalty score (negative value if unsafe).
    """
    g = Game(game.get_fen())  # Create a new instance of the board
    g.apply_move(move)  # Apply the move
    return -10 if g.status == Game.CHECK else 0  # Penalize moves that leave the king in check

def chess_bot(obs):
    """
    Improved chess bot prioritizing checkmates, high-value captures, positional play, and queen promotions.

    Args:
        obs: An object with a 'board' attribute representing the current board state as a FEN string.

    Returns:
        A string representing the chosen move in UCI notation (e.g., "e2e4")
    """
    # Initialize game state
    game = Game(obs.board)
    moves = list(game.get_moves())

    # Evaluate moves
    def score_move(move):
        return (
            evaluate_capture(game, move) +
            evaluate_position(move) +
            evaluate_king_safety(game, move)
        )

    # 1. Check for checkmate moves
    for move in moves:
        g = Game(obs.board)
        g.apply_move(move)
        if g.status == Game.CHECKMATE:
            return move

    # 2. Score all moves and choose the best one
    scored_moves = [(move, score_move(move)) for move in moves]
    best_move = max(scored_moves, key=lambda x: x[1])[0]

    # 3. Prioritize queen promotions if possible
    for move in moves:
        if move[-1].lower() == 'q':
            return move

    # 4. Default to the best scored move or random fallback
    return best_move if scored_moves else random.choice(moves)
