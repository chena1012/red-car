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
            ("powerup", "Power Up"),
            ("reset", "Reset"),
            ("prev", "Previous Level"),
            ("next", "Next Level"),
        ]
        y = C.TITLE_BAR_HEIGHT + (C.CONTROL_BAR_HEIGHT - C.BUTTON_HEIGHT) // 2

        widths: list[int] = []
        for _key, label in specs:
            if _key == "powerup":
                w = self._font.size("Power Up (3/3)")[0] + 2 * C.BUTTON_PAD_X
            else:
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
        powerup_remain: int,
    ) -> None:
        label = f"Level {level_index + 1}/{level_total}"
        surf = self._font.render(label, True, C.COLOR_TITLE)
        y_text = C.TITLE_BAR_HEIGHT + (C.CONTROL_BAR_HEIGHT - surf.get_height()) // 2
        surface.blit(surf, (16, y_text))

        for key, btn in self._buttons.items():
            if key == "powerup":
                self._draw_powerup_button(surface, btn, mouse_pos, powerup_remain)
            else:
                btn.draw(surface, mouse_pos)

    def _draw_powerup_button(self, surface, btn, mouse_pos, remain):
        hovered = mouse_pos is not None and btn.rect.collidepoint(mouse_pos)
        fill = C.COLOR_BUTTON_FILL_HOVER if hovered else C.COLOR_BUTTON_FILL

        # 画按钮背景
        pygame.draw.rect(surface, fill, btn.rect, border_radius=C.BUTTON_RADIUS)
        pygame.draw.rect(
            surface,
            C.COLOR_BUTTON_BORDER,
            btn.rect,
            width=2,
            border_radius=C.BUTTON_RADIUS,
        )

        # 画动态文字：Power Up (x/3)
        text = self._font.render(f"Power Up ({remain}/3)", True, C.COLOR_BUTTON_TEXT)
        text_rect = text.get_rect(center=btn.rect.center)
        surface.blit(text, text_rect)

    def action_at(self, pos: tuple[int, int]) -> str | None:
        for key, btn in self._buttons.items():
            if btn.contains(pos):
                return key
        return None
