"""Info panels and Menu screen implementation."""

from __future__ import annotations

import pygame

from game import constants as C
from .button import Button


class Menu:
    """Game start menu with Start and Exit buttons."""

    def __init__(self, screen_width: int, screen_height: int, title_font: pygame.font.Font, button_font: pygame.font.Font) -> None:
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._title_font = title_font
        self._button_font = button_font
        self._buttons: dict[str, Button] = {}
        self._layout()

    def _layout(self) -> None:
        # Title position
        self._title_y = self._screen_height // 4
        
        # Button specs
        specs = [
            ("start", "Start"),
            ("exit", "Exit"),
        ]
        
        button_w = 200
        button_h = 50
        gap = 20
        
        total_height = (button_h * len(specs)) + (gap * (len(specs) - 1))

        # Move menu buttons lower
        button_offset_y = 90
        start_y = self._screen_height // 2 + button_offset_y

        x = (self._screen_width - button_w) // 2
        y = start_y
        
        for key, label in specs:
            rect = pygame.Rect(x, y, button_w, button_h)
            self._buttons[key] = Button(rect, label, self._button_font)
            y += button_h + gap

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int] | None) -> None:
        # surface.fill(C.COLOR_BG)
        
        # Draw Title
        # title_surf = self._title_font.render("Little Red Car", True, C.COLOR_TITLE)
        # title_rect = title_surf.get_rect(center=(self._screen_width // 2, self._title_y))
        # surface.blit(title_surf, title_rect)
        
        # Draw Buttons
        for btn in self._buttons.values():
            btn.draw(surface, mouse_pos)

    def action_at(self, pos: tuple[int, int]) -> str | None:
        for key, btn in self._buttons.items():
            if btn.contains(pos):
                return key
        return None
