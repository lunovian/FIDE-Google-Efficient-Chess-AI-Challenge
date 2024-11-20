from Chessnut import Game
import random

PIECE_VALUES = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0, ' ': 0}

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

def chess_bot(obs):
    """
    Improved chess bot prioritizing checkmates, high-value captures, and queen promotions.

    Args:
        obs: An object with a 'board' attribute representing the current board state as a FEN string.

    Returns:
        A string representing the chosen move in UCI notation (e.g., "e2e4")
    """
    # Initialize game state
    game = Game(obs.board)
    moves = list(game.get_moves())
    
    # 1. Check for checkmate moves
    for move in moves:
        g = Game(obs.board)
        g.apply_move(move)
        if g.status == Game.CHECKMATE:
            return move

    # 2. Prioritize captures by value
    capture_moves = [(move, evaluate_capture(game, move)) for move in moves]
    capture_moves = sorted(capture_moves, key=lambda x: x[1], reverse=True)
    if capture_moves and capture_moves[0][1] > 0:
        return capture_moves[0][0]

    # 3. Prioritize queen promotions
    for move in moves:
        if move[-1].lower() == 'q':
            return move

    # 4. Random fallback move
    return random.choice(moves)
