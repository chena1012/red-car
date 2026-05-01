from collections import deque

class RushHourHint:
    rows = 6
    cols = 6

    @staticmethod
    def board_from_state(state):
        board = [[None for _ in range(6)] for _ in range(6)]
        for v in state.vehicles:
            for r, c in v.cells():
                if 0 <= r < 6 and 0 <= c < 6:
                    board[r][c] = v.id
        return board

    @staticmethod
    def is_win(board):
        return board[2][5] == 'R'

    @staticmethod
    def get_car_info(board, cid):
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
        return [row.copy() for row in board]

    @staticmethod
    def next_states(board):
        nexts = []
        cars = set(ch for row in board for ch in row if ch is not None)

        for cid in cars:
            car = RushHourHint.get_car_info(board, cid)
            if not car:
                continue

            h = car['horizontal']
            mr, Mr = car['min_r'], car['max_r']
            mc, Mc = car['min_c'], car['max_c']
            L = car['length']

            if h:
                r = mr
                left = mc - 1
                while left >= 0 and board[r][left] is None:
                    nb = RushHourHint.clone_board(board)
                    for x in range(L): nb[r][Mc - x] = None
                    for x in range(L): nb[r][left + x] = cid
                    steps = mc - left
                    nexts.append((nb, f"Move {cid} LEFT ×{steps}"))
                    left -= 1

                right = Mc + 1
                while right < 6 and board[r][right] is None:
                    nb = RushHourHint.clone_board(board)
                    for x in range(L): nb[r][mc + x] = None
                    for x in range(L): nb[r][right - L + 1 + x] = cid
                    steps = right - Mc
                    nexts.append((nb, f"Move {cid} RIGHT ×{steps}"))
                    right += 1
            else:
                c = mc
                up = mr - 1
                while up >= 0 and board[up][c] is None:
                    nb = RushHourHint.clone_board(board)
                    for x in range(L): nb[Mr - x][c] = None
                    for x in range(L): nb[up + x][c] = cid
                    steps = mr - up
                    nexts.append((nb, f"Move {cid} UP ×{steps}"))
                    up -= 1

                down = Mr + 1
                while down < 6 and board[down][c] is None:
                    nb = RushHourHint.clone_board(board)
                    for x in range(L): nb[mr + x][c] = None
                    for x in range(L): nb[down - L + 1 + x][c] = cid
                    steps = down - Mr
                    nexts.append((nb, f"Move {cid} DOWN ×{steps}"))
                    down += 1
        return nexts

    @staticmethod
    def get_hint(state):
        try:
            board = RushHourHint.board_from_state(state)
            if RushHourHint.is_win(board):
                return "Solved"

            start = tuple(tuple(r) for r in board)
            q = deque([(board, [])])
            vis = {start}

            while q:
                cur, path = q.popleft()
                if RushHourHint.is_win(cur):
                    return path[0] if path else "Solved"

                for nxt, move in RushHourHint.next_states(cur):
                    t = tuple(tuple(r) for r in nxt)
                    if t not in vis:
                        vis.add(t)
                        q.append((nxt, path + [move]))

            return "No solution"
        except:
            return "No solution"