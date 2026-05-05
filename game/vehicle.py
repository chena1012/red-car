"""Vehicle data model: grid occupation, translation (logical movement, no interaction verification in this phase)."""

from __future__ import annotations


class Vehicle:
    """A vehicle is represented on the board by an anchor cell (row, col).

    - Horizontal vehicle: The anchor is the leftmost cell, occupying (row, col) .. (row, col+length-1)
    - Vertical vehicle: The anchor is the topmost cell, occupying (row, col) .. (row+length-1, col)

    Consistent with the common Rush Hour game rules: 
    - Horizontal vehicles can only change column (col)
    - Vertical vehicles can only change row (row)
    """

    def __init__(
        self,
        id: str,
        row: int,
        col: int,
        length: int,
        horizontal: bool,
        color: tuple[int, int, int],
        is_target: bool,
    ) -> None:
        """Initialize a Vehicle instance.

        Args:
            id: Unique identifier for the vehicle
            row: Row coordinate of the anchor cell
            col: Column coordinate of the anchor cell
            length: Number of grid cells the vehicle occupies
            horizontal: True if vehicle is horizontal (left-right), False if vertical (up-down)
            color: RGB color tuple representing the vehicle (e.g., (255, 0, 0) for red)
            is_target: True if this is the target vehicle to move to exit
        """
        self.id = id
        self.row = row
        self.col = col
        self.length = length
        self.horizontal = horizontal
        self.color = color
        self.is_target = is_target

    def cells(self) -> list[tuple[int, int]]:
        """Get all grid cells occupied by the vehicle.

        Returns:
            List of (row, col) tuples representing all cells occupied by the vehicle
        """
        if self.horizontal:
            return [(self.row, self.col + i) for i in range(self.length)]
        return [(self.row + i, self.col) for i in range(self.length)]

    def move(self, distance: int) -> None:
        """Translate the vehicle by a number of cells along its allowed direction.
        
        Positive distance: 
        - Horizontal vehicle: move to the right
        - Vertical vehicle: move downwards
        
        Negative distance:
        - Horizontal vehicle: move to the left
        - Vertical vehicle: move upwards

        Args:
            distance: Number of cells to move (can be positive or negative)
        """
        if self.horizontal:
            self.col += distance
        else:
            self.row += distance