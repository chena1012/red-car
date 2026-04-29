"""Top control bar: level info and Reset / Previous / Next buttons."""

from __future__ import annotations

import pygame

from game import constants as C

from .button import Button


class ControlBar:
    """Draws level info and buttons in a row below the title."""

    def __init__(self, screen_width: int, font: pygame.font.Font) -> None:
        self._screen_width = screen_width
        self._font = font
        self._buttons: dict[str, Button] = {}
        self._layout()

    def _layout(self) -> None:
        specs = [
            ("reset", "Reset"),
            ("prev", "Previous Level"),
            ("next", "Next Level"),
            ("pause", "Pause"),
        ]
        y = C.TITLE_BAR_HEIGHT + (C.CONTROL_BAR_HEIGHT - C.BUTTON_HEIGHT) // 2

        widths: list[int] = []
        for _key, label in specs:
            w = self._font.size(label)[0] + 2 * C.BUTTON_PAD_X
            widths.append(max(w, 96))

        gap = 10
        total = sum(widths) + gap * (len(specs) - 1)
        # 靠右成组，避免与左侧「关卡」文字重叠
        right_margin = 16
        x = self._screen_width - right_margin - total

        self._buttons.clear()
        for (key, label), bw in zip(specs, widths):
            rect = pygame.Rect(x, y, bw, C.BUTTON_HEIGHT)
            self._buttons[key] = Button(rect, label, self._font)
            x += bw + gap

    def draw(
        self,
        surface: pygame.Surface,
        mouse_pos: tuple[int, int] | None,
        level_index: int,
        level_total: int,
    ) -> None:
        label = f"Level {level_index + 1}/{level_total}"
        surf = self._font.render(label, True, C.COLOR_TITLE)
        y_text = C.TITLE_BAR_HEIGHT + (C.CONTROL_BAR_HEIGHT - surf.get_height()) // 2
        surface.blit(surf, (16, y_text))

        for btn in self._buttons.values():
            btn.draw(surface, mouse_pos)

    def action_at(self, pos: tuple[int, int]) -> str | None:
        for key, btn in self._buttons.items():
            if btn.contains(pos):
                return key
        return None
