"""车辆数据模型：占格、平移（逻辑移动，本阶段不做交互校验）。"""

from __future__ import annotations


class Vehicle:
    """一辆车在棋盘上用锚点格 (row, col) 表示位置。

    - 横向车：锚点为最左一格，占据 (row, col) .. (row, col+length-1)
    - 竖向车：锚点为最上一格，占据 (row, col) .. (row+length-1, col)

    与常见 Rush Hour 一致：横向只能改 col，竖向只能改 row。
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
        self.id = id
        self.row = row
        self.col = col
        self.length = length
        self.horizontal = horizontal
        self.color = color
        self.is_target = is_target

    def cells(self) -> list[tuple[int, int]]:
        if self.horizontal:
            return [(self.row, self.col + i) for i in range(self.length)]
        return [(self.row + i, self.col) for i in range(self.length)]

    def move(self, distance: int) -> None:
        """沿允许方向平移若干格。distance 为正：横向向右、竖向向下。"""
        if self.horizontal:
            self.col += distance
        else:
            self.row += distance
