"""Board state: vehicle list, occupancy lookup, bounds check, overlap check and movement validation."""

from __future__ import annotations

from . import constants as C
from .vehicle import Vehicle


class GameState:
    """Collection of vehicles on a fixed 6x6 board; centralized validation for single-step movement."""

    def __init__(self, vehicles: list[Vehicle]) -> None:
        """Initialize game state with a list of vehicles.
        
        Args:
            vehicles: List of Vehicle objects on the board
        """
        self._vehicles = list(vehicles)

    @property
    def vehicles(self) -> tuple[Vehicle, ...]:
        """Get an immutable tuple of all vehicles.
        
        Returns:
            Tuple of all vehicles to prevent external modification
        """
        return tuple(self._vehicles)

    def get_vehicle(self, vehicle_id: str) -> Vehicle | None:
        """Get a vehicle by its ID.
        
        Args:
            vehicle_id: Unique ID of the vehicle
        Returns:
            Vehicle if found, None otherwise
        """
        for v in self._vehicles:
            if v.id == vehicle_id:
                return v
        return None

    def occupant_at(self, row: int, col: int) -> Vehicle | None:
        """Get the vehicle occupying the given cell.
        
        Args:
            row: Cell row
            col: Cell column
        Returns:
            Vehicle at the cell, or None if empty
        """
        for v in self._vehicles:
            if (row, col) in v.cells():
                return v
        return None

    def occupation_map(self) -> dict[tuple[int, int], Vehicle]:
        """Create a map from occupied cells to their vehicle.
        
        Returns:
            Dictionary mapping (row, col) to Vehicle; later vehicles overwrite earlier ones on overlap
        """
        m: dict[tuple[int, int], Vehicle] = {}
        for v in self._vehicles:
            for cell in v.cells():
                m[cell] = v
        return m

    def is_within_bounds(self, vehicle: Vehicle) -> bool:
        """Check whether all cells of the vehicle are strictly inside the board.
        
        Does NOT allow the target vehicle to extend out the exit.
        
        Args:
            vehicle: Vehicle to check
        Returns:
            True if fully inside board bounds
        """
        for r, c in vehicle.cells():
            if not (0 <= r < C.GRID_ROWS and 0 <= c < C.GRID_COLS):
                return False
        return True

    @staticmethod
    def cells_on_board(vehicle: Vehicle) -> set[tuple[int, int]]:
        """Get the subset of vehicle cells that lie inside the 6x6 board.
        
        Used for collision and blocking checks.
        
        Args:
            vehicle: Vehicle to check
        Returns:
            Set of (row, col) cells inside the board
        """
        return {
            (r, c)
            for r, c in vehicle.cells()
            if 0 <= r < C.GRID_ROWS and 0 <= c < C.GRID_COLS
        }

    def _all_cells_respect_board_rules(self, v: Vehicle) -> bool:
        """Check whether the vehicle obeys board boundary rules.
        
        Normal vehicles must stay fully inside.
        Target horizontal vehicles may extend out the right side on the exit row.
        
        Args:
            v: Vehicle to validate
        Returns:
            True if the vehicle position is valid
        """
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
        """Check whether a candidate vehicle overlaps any other vehicle on the board.
        
        Args:
            candidate: Vehicle to test
            exclude_id: Vehicle ID to exclude (usually itself)
        Returns:
            True if overlap exists
        """
        mine = self.cells_on_board(candidate)
        for other in self._vehicles:
            if other.id == exclude_id:
                continue
            if mine & self.cells_on_board(other):
                return True
        return False

    def cells_overlap(self, a: Vehicle, b: Vehicle) -> bool:
        """Check whether two vehicles share any cell (including off-board cells).
        
        Args:
            a: First vehicle
            b: Second vehicle
        Returns:
            True if any cell is shared
        """
        sa = set(a.cells())
        sb = set(b.cells())
        return not sa.isdisjoint(sb)

    def has_any_overlap(self) -> bool:
        """Check whether any two vehicles overlap. Used for level validation.
        
        Returns:
            True if any collision exists
        """
        vs = self._vehicles
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                if self.cells_overlap(vs[i], vs[j]):
                    return True
        return False

    def is_won(self) -> bool:
        """Check win condition: target vehicle has exited via the right exit.
        
        Returns:
            True if the level is won
        """
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
        """Check if a one-step move is allowed. Does not modify state.
        
        Horizontal vehicles move only left/right. Vertical vehicles move only up/down.
        
        Args:
            vehicle: Vehicle to move
            dr: Row delta (-1, 0, 1)
            dc: Column delta (-1, 0, 1)
        Returns:
            True if the step is valid
        """
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
        """Attempt to move a vehicle by one step if valid.
        
        Args:
            vehicle_id: ID of vehicle to move
            dr: Row delta
            dc: Column delta
        Returns:
            True if movement succeeded
        """
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
        """Return how many continuous steps the vehicle can move in a direction.
        
        Args:
            vehicle_id: Vehicle to move
            dr: Row direction (-1, 0, 1)
            dc: Column direction (-1, 0, 1)
            max_steps: Maximum steps to check (None = unlimited)
        Returns:
            Maximum safe steps in that direction
        """
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

    def remove_vehicle(self, vehicle_id: str) -> bool:
        """Remove a vehicle from the board.
        
        Args:
            vehicle_id: ID of vehicle to remove
        Returns:
            True if vehicle was found and removed
        """
        for i, v in enumerate(self._vehicles):
            if v.id == vehicle_id:
                self._vehicles.pop(i)
                return True
        return False

    def export_positions(self) -> list[dict[str, int | str]]:
        """Export a snapshot of vehicle positions for saving.
        
        Returns:
            List of position dicts with id, row, col
        """
        return [{"id": v.id, "row": v.row, "col": v.col} for v in self._vehicles]

    def export_vehicles(self) -> list[dict[str, int | str | bool]]:
        """Export full vehicle data for saving.
        
        Returns:
            List of complete vehicle state dicts
        """
        return [{"id": v.id, "row": v.row, "col": v.col, "length": v.length, "horizontal": v.horizontal, "color": v.color, "is_target": v.is_target} for v in self._vehicles]

    def apply_vehicles(self, vehicles_data: list[dict[str, int | str | bool]]) -> bool:
        """Create vehicles from saved data.
        
        Args:
            vehicles_data: List of vehicle dicts
        Returns:
            True if loaded successfully with no overlaps or out-of-bounds
        """
        try:
            vehicles = []
            for item in vehicles_data:
                vid = str(item["id"])
                row = int(item["row"])
                col = int(item["col"])
                length = int(item["length"])
                horizontal = bool(item["horizontal"])
                color = tuple(item["color"]) if isinstance(
                    item["color"], list) else item["color"]
                is_target = bool(item["is_target"])
                v = Vehicle(vid, row, col, length,
                            horizontal, color, is_target)
                vehicles.append(v)
            self._vehicles = vehicles
            if self.has_any_overlap():
                return False
            for v in self._vehicles:
                if not self._all_cells_respect_board_rules(v):
                    return False
            return True
        except (KeyError, TypeError, ValueError):
            return False

    def apply_positions(self, positions: list[dict[str, int | str]]) -> bool:
        """Restore vehicle positions by ID. Reverts on invalid data.
        
        Args:
            positions: List of position dicts with id, row, col
        Returns:
            True if positions applied safely
        """
        by_id = {v.id: v for v in self._vehicles}
        if len(positions) != len(self._vehicles):
            return False

        original = {v.id: (v.row, v.col) for v in self._vehicles}
        seen: set[str] = set()
        try:
            for item in positions:
                vid = str(item.get("id", ""))
                if vid not in by_id or vid in seen:
                    raise ValueError("invalid vehicle id")
                row = int(item["row"])
                col = int(item["col"])
                by_id[vid].row = row
                by_id[vid].col = col
                seen.add(vid)
            if self.has_any_overlap():
                raise ValueError("overlap")
            for v in self._vehicles:
                if not self._all_cells_respect_board_rules(v):
                    raise ValueError("out of board")
        except (KeyError, TypeError, ValueError):
            for v in self._vehicles:
                old = original[v.id]
                v.row, v.col = old
            return False
        return True