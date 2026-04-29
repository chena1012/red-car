"""Simple rectangular button: Pygame drawing and hit detection."""

from __future__ import annotations

import pygame

from game import constants as C


class Button:
    """Rounded rectangle button with centered text and hover effect."""

    def __init__(
        self,
        rect: pygame.Rect | tuple[int, int, int, int],
        label: str,
        font: pygame.font.Font,
        border_radius: int = C.BUTTON_RADIUS
    ) -> None:
        self.rect = pygame.Rect(rect)
        self._label = label
        self._font = font
        self.fill_color = C.COLOR_BUTTON_FILL
        self.hover_color = C.COLOR_BUTTON_FILL_HOVER
        self.border_color = C.COLOR_BUTTON_BORDER
        self.text_color = C.COLOR_BUTTON_TEXT
        self.border_radius = border_radius

    def set_colors(self, fill=None, hover=None, border=None, text=None):
        if fill is not None:
            self.fill_color = fill
        if hover is not None:
            self.hover_color = hover
        if border is not None:
            self.border_color = border
        if text is not None:
            self.text_color = text

    def draw(
        self,
        surface: pygame.Surface,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        hovered = mouse_pos is not None and self.rect.collidepoint(mouse_pos)
        # fill = C.COLOR_BUTTON_FILL_HOVER if hovered else C.COLOR_BUTTON_FILL
        fill = self.hover_color if hovered else self.fill_color
        pygame.draw.rect(surface, fill, self.rect,
                         border_radius=self.border_radius)
        pygame.draw.rect(
            surface,
            # C.COLOR_BUTTON_BORDER
            self.border_color,
            self.rect,
            width=2,
            border_radius= self.border_radius,
        )
        text = self._font.render(self._label, True,
        # C.COLOR_BUTTON_TEXT
        self.text_color)
        tr = text.get_rect(center=self.rect.center)
        surface.blit(text, tr)

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)
