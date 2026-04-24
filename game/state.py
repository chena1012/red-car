"""棋盘状态：车辆列表、占格查询、越界、重叠与移动合法性。"""

from __future__ import annotations

from . import constants as C
from .vehicle import Vehicle


class GameState:
    """固定 6x6 棋盘上的车辆集合；移动一步的合法性在此集中判定。"""

    def __init__(self, vehicles: list[Vehicle]) -> None:
        self._vehicles = list(vehicles)

    @property
    def vehicles(self) -> tuple[Vehicle, ...]:
        return tuple(self._vehicles)

    def get_vehicle(self, vehicle_id: str) -> Vehicle | None:
        for v in self._vehicles:
            if v.id == vehicle_id:
                return v
        return None

    def occupant_at(self, row: int, col: int) -> Vehicle | None:
        """返回占据该格的车辆；若无则 None。"""
        for v in self._vehicles:
            if (row, col) in v.cells():
                return v
        return None

    def occupation_map(self) -> dict[tuple[int, int], Vehicle]:
        """所有被占格子 -> 车辆（若关卡数据有误出现重叠，后写入者覆盖）。"""
        m: dict[tuple[int, int], Vehicle] = {}
        for v in self._vehicles:
            for cell in v.cells():
                m[cell] = v
        return m

    def is_within_bounds(self, vehicle: Vehicle) -> bool:
        """车辆所有占格是否都在棋盘内（不含红车探出出口的合法占位）。"""
        for r, c in vehicle.cells():
            if not (0 <= r < C.GRID_ROWS and 0 <= c < C.GRID_COLS):
                return False
        return True

    @staticmethod
    def cells_on_board(vehicle: Vehicle) -> set[tuple[int, int]]:
        """落在 6x6 内的占格，用于与其他车判断是否挡路。"""
        return {
            (r, c)
            for r, c in vehicle.cells()
            if 0 <= r < C.GRID_ROWS and 0 <= c < C.GRID_COLS
        }

    def _all_cells_respect_board_rules(self, v: Vehicle) -> bool:
        """越界判定：普通车必须完全在盘内；目标横车可从出口行右侧探出。"""
        for r, c in v.cells():
            if not (0 <= r < C.GRID_ROWS):
                return False
            if 0 <= c < C.GRID_COLS:
                continue
            if c < 0:
                return False
            if v.is_target and v.horizontal and r == C.EXIT_ROW and c >= C.GRID_COLS:
                continue
            return False
        return True

    def _has_overlap_on_board(self, candidate: Vehicle, exclude_id: str) -> bool:
        mine = self.cells_on_board(candidate)
        for other in self._vehicles:
            if other.id == exclude_id:
                continue
            if mine & self.cells_on_board(other):
                return True
        return False

    def cells_overlap(self, a: Vehicle, b: Vehicle) -> bool:
        """两辆车是否共用至少一格（含盘外格）。"""
        sa = set(a.cells())
        sb = set(b.cells())
        return not sa.isdisjoint(sb)

    def has_any_overlap(self) -> bool:
        """任意两车是否占格冲突（用于校验关卡数据）。"""
        vs = self._vehicles
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                if self.cells_overlap(vs[i], vs[j]):
                    return True
        return False

    def is_won(self) -> bool:
        """目标车（红车）从右侧出口离开：在出口行且右端已越过棋盘右边界。"""
        for v in self._vehicles:
            if not v.is_target:
                continue
            if not v.horizontal:
                return False
            if v.row != C.EXIT_ROW:
                return False
            return v.col + v.length >= C.GRID_COLS
        return False

    def can_move_step(self, vehicle: Vehicle, dr: int, dc: int) -> bool:
        """是否允许该车按一步 (dr, dc) 移动；不修改状态。横车仅左右，竖车仅上下。"""
        if vehicle.horizontal:
            if dr != 0 or dc not in (-1, 1):
                return False
        else:
            if dc != 0 or dr not in (-1, 1):
                return False

        nr = vehicle.row + dr
        nc = vehicle.col + dc
        trial = Vehicle(
            vehicle.id,
            nr,
            nc,
            vehicle.length,
            vehicle.horizontal,
            vehicle.color,
            vehicle.is_target,
        )
        if not self._all_cells_respect_board_rules(trial):
            return False
        if self._has_overlap_on_board(trial, vehicle.id):
            return False
        return True

    def try_move_step(self, vehicle_id: str, dr: int, dc: int) -> bool:
        """合法则移动一格并返回 True，否则不改动并返回 False。"""
        v = self.get_vehicle(vehicle_id)
        if v is None:
            return False
        if not self.can_move_step(v, dr, dc):
            return False
        v.row += dr
        v.col += dc
        return True

    def max_steps_in_direction(
        self, vehicle_id: str, dr: int, dc: int, max_steps: int | None = None
    ) -> int:
        """Return how many continuous steps the vehicle can move in a direction."""
        v = self.get_vehicle(vehicle_id)
        if v is None:
            return 0

        if v.horizontal:
            if dr != 0 or dc not in (-1, 1):
                return 0
        else:
            if dc != 0 or dr not in (-1, 1):
                return 0

        steps = 0
        row, col = v.row, v.col
        while max_steps is None or steps < max_steps:
            trial = Vehicle(
                v.id,
                row + dr,
                col + dc,
                v.length,
                v.horizontal,
                v.color,
                v.is_target,
            )
            if not self._all_cells_respect_board_rules(trial):
                break
            if self._has_overlap_on_board(trial, v.id):
                break
            row += dr
            col += dc
            steps += 1
        return steps
