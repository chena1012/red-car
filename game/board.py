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

    def draw(self, surface: pygame.Surface, board_bg: pygame.Surface) -> None:
        surface.blit(board_bg, self._topleft)
