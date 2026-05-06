"""6x6 board rendering (grid and background)."""

from __future__ import annotations

import pygame

from . import constants as C


class Board:
    """Renders a fixed-size 6x6 game board at the specified top-left coordinates."""

    def __init__(self, topleft: tuple[int, int]) -> None:
        """Initialize the board renderer with a fixed position.
        
        Args:
            topleft: (x, y) pixel coordinates for the top-left corner of the board
        """
        self._topleft = topleft

    @property
    def topleft(self) -> tuple[int, int]:
        """Get the top-left position of the board.
        
        Returns:
            (x, y) pixel coordinates of the board's top-left corner
        """
        return self._topleft

    def draw(self, surface: pygame.Surface, board_bg: pygame.Surface) -> None:
        """Draw the board background onto the game surface.
        
        Args:
            surface: Pygame surface to render the board on
            board_bg: Preloaded background image for the board
        """
        surface.blit(board_bg, self._topleft)