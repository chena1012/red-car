"""6x6 棋盘绘制（网格与背景）。"""

from __future__ import annotations

import pygame

from . import constants as C


class Board:
    """在指定左上角坐标绘制固定大小的棋盘网格。"""

    def __init__(self, topleft: tuple[int, int]) -> None:
        self._topleft = topleft

    @property
    def topleft(self) -> tuple[int, int]:
        return self._topleft

    def draw(self, surface: pygame.Surface) -> None:
        x0, y0 = self._topleft
        w = C.GRID_COLS * C.CELL_SIZE
        h = C.GRID_ROWS * C.CELL_SIZE
        board_rect = pygame.Rect(x0, y0, w, h)

        pygame.draw.rect(surface, C.COLOR_BOARD, board_rect)

        line_width = 2
        for c in range(C.GRID_COLS + 1):
            px = x0 + c * C.CELL_SIZE
            pygame.draw.line(
                surface,
                C.COLOR_GRID_LINE,
                (px, y0),
                (px, y0 + h),
                line_width,
            )
        for r in range(C.GRID_ROWS + 1):
            py = y0 + r * C.CELL_SIZE
            pygame.draw.line(
                surface,
                C.COLOR_GRID_LINE,
                (x0, py),
                (x0 + w, py),
                line_width,
            )
