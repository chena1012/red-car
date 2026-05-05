from collections import deque

class RushHourHint:
    """BFS-based hint generator for the RushHour puzzle.
    Computes the optimal first move to solve the current level by searching all valid game states.
    """
    # Fixed game board dimensions (6x6 grid)
    rows = 6
    cols = 6

    @staticmethod
    def board_from_state(state):
        """Convert a GameState object into a 6x6 grid representation.
        
        Args:
            state: Current game state containing all vehicles
        Returns:
            2D list representing the board with vehicle IDs in their positions
        """
        board = [[None for _ in range(6)] for _ in range(6)]
        for v in state.vehicles:
            for r, c in v.cells():
                if 0 <= r < 6 and 0 <= c < 6:
                    board[r][c] = v.id
        return board

    @staticmethod
    def is_win(board):
        """Check if the win condition is met (red car 'R' reaches the exit cell).
        
        Args:
            board: 6x6 game board grid
        Returns:
            True if red car is at the exit (row 2, column 5)
        """
        return board[2][5] == 'R'

    @staticmethod
    def get_car_info(board, cid):
        """Retrieve complete positional data for a specific vehicle.
        
        Args:
            board: 6x6 game board grid
            cid: Unique ID of the vehicle to inspect
        Returns:
            Dictionary with vehicle orientation, bounds, and length; None if vehicle not found
        """
        positions = []
        for r in range(6):
            for c in range(6):
                if board[r][c] == cid:
                    positions.append((r, c))
        if not positions:
            return None
        
        rs = sorted({r for r, c in positions})
        cs = sorted({c for r, c in positions})
        return {
            'id': cid,
            'horizontal': (rs[0] == rs[-1]),
            'min_r': rs[0], 'max_r': rs[-1],
            'min_c': cs[0], 'max_c': cs[-1],
            'length': len(positions)
        }

    @staticmethod
    def clone_board(board):
        """Create a deep copy of the board to avoid modifying the original state.
        
        Args:
            board: 6x6 game board grid
        Returns:
            New independent copy of the board
        """
        return [row.copy() for row in board]

    @staticmethod
    def next_states(board):
        """Generate all valid next game states by moving any vehicle as far as possible.
        
        Args:
            board: Current 6x6 game board grid
        Returns:
            List of tuples (new_board, move_description) for all valid moves
        """
        nexts = []
        # Collect all unique vehicle IDs on the board
        cars = set(ch for row in board for ch in row if ch is not None)

        for cid in cars:
            car = RushHourHint.get_car_info(board, cid)
            if not car:
                continue

            h = car['horizontal']
            mr, Mr = car['min_r'], car['max_r']
            mc, Mc = car['min_c'], car['max_c']
            L = car['length']

            # Handle horizontal vehicle movement (left/right)
            if h:
                r = mr
                left = mc - 1
                # Move left as far as possible
                while left >= 0 and board[r][left] is None:
                    nb = RushHourHint.clone_board(board)
                    # Clear old position
                    for x in range(L): nb[r][Mc - x] = None
                    # Set new position
                    for x in range(L): nb[r][left + x] = cid
                    steps = mc - left
                    nexts.append((nb, f"Move {cid} LEFT ×{steps}"))
                    left -= 1

                right = Mc + 1
                # Move right as far as possible
                while right < 6 and board[r][right] is None:
                    nb = RushHourHint.clone_board(board)
                    # Clear old position
                    for x in range(L): nb[r][mc + x] = None
                    # Set new position
                    for x in range(L): nb[r][right - L + 1 + x] = cid
                    steps = right - Mc
                    nexts.append((nb, f"Move {cid} RIGHT ×{steps}"))
                    right += 1
            # Handle vertical vehicle movement (up/down)
            else:
                c = mc
                up = mr - 1
                # Move up as far as possible
                while up >= 0 and board[up][c] is None:
                    nb = RushHourHint.clone_board(board)
                    # Clear old position
                    for x in range(L): nb[Mr - x][c] = None
                    # Set new position
                    for x in range(L): nb[up + x][c] = cid
                    steps = mr - up
                    nexts.append((nb, f"Move {cid} UP ×{steps}"))
                    up -= 1

                down = Mr + 1
                # Move down as far as possible
                while down < 6 and board[down][c] is None:
                    nb = RushHourHint.clone_board(board)
                    # Clear old position
                    for x in range(L): nb[mr + x][c] = None
                    # Set new position
                    for x in range(L): nb[down - L + 1 + x][c] = cid
                    steps = down - Mr
                    nexts.append((nb, f"Move {cid} DOWN ×{steps}"))
                    down += 1
        return nexts

    @staticmethod
    def get_hint(state):
        """Breadth-First Search to find the shortest solution and return the FIRST move as a hint.
        
        Args:
            state: Current game state to analyze
        Returns:
            String with the optimal first move, or status message (Solved/No solution)
        """
        try:
            board = RushHourHint.board_from_state(state)
            if RushHourHint.is_win(board):
                return "Solved"

            # Convert board to tuple for hashable visited set
            start = tuple(tuple(r) for r in board)
            # BFS queue: (current_board, move_path)
            q = deque([(board, [])])
            vis = {start}

            while q:
                cur, path = q.popleft()
                # Win condition found: return the first move in the solution path
                if RushHourHint.is_win(cur):
                    return path[0] if path else "Solved"

                # Explore all valid next moves
                for nxt, move in RushHourHint.next_states(cur):
                    t = tuple(tuple(r) for r in nxt)
                    if t not in vis:
                        vis.add(t)
                        q.append((nxt, path + [move]))

            return "No solution"
        except:
            # Fallback for any unexpected errors
            return "No solution"