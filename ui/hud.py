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
        self._big_font = pygame.font.Font(None, 30)
        self._top_font = pygame.font.Font(None, 22)
        self._buttons: dict[str, Button] = {}
        self._layout()

    def _layout(self) -> None:
        specs = [
            ("hint", "Hint"),
            ("undo", "Undo"),
            ("powerup", "Remove"),
            ("reset", "Reset"),
            ("prev", "Previous Level"),
            ("next", "Next Level"),
            ("pause", "Pause"),
        ]

        y = C.TITLE_BAR_HEIGHT + (C.CONTROL_BAR_HEIGHT - C.BUTTON_HEIGHT) // 2

        normal_specs = [
            ("prev", "Previous Level"),
            ("next", "Next Level"),
            ("pause", "Pause"),
        ]

        # Make the top three buttons slightly larger.
        top_button_h = 46
        top_gap = 16

        top_widths = {
            "prev": 130,
            "next": 130,
            "pause": 110,
        }

        # Move the top three buttons to the position marked in the screenshot.
        x = 570
        y = C.TITLE_BAR_HEIGHT + 48

        self._buttons.clear()

        # Keep Previous Level, Next Level, Pause in the original top-right area.
        for key, label in normal_specs:
            bw = top_widths[key]
            rect = pygame.Rect(x, y, bw, top_button_h)
            self._buttons[key] = Button(rect, label, self._top_font)
            x += bw + top_gap

        # Move Power Up, Reset and Hint to the lower area, and make them larger.
        big_w = 160  # 稍微减小宽度以放下三个按钮
        big_h = 58
        bottom_y = C.WINDOW_HEIGHT - 90

        # 调整 x 坐标，让三个按钮并排
        self._buttons["hint"] = Button(
            pygame.Rect(800, bottom_y - 70, big_w, big_h),
            "Hint",
            self._font,
        )
        
        self._buttons["undo"] = Button(
            pygame.Rect(625, bottom_y - 70, big_w, big_h),
            "Undo",
            self._font,
        )

        self._buttons["powerup"] = Button(
            pygame.Rect(625, bottom_y, big_w, big_h),
            "Remove",
            self._font,
        )

        self._buttons["reset"] = Button(
            pygame.Rect(800, bottom_y, big_w, big_h),
            "Reset",
            self._font,
        )

    def draw(
        self,
        surface: pygame.Surface,
        mouse_pos: tuple[int, int] | None,
        level_index: int,
        level_total: int,
        powerup_remain: int,
        mode: str = C.MODE_NORMAL,
    ) -> None:
        label = f"Level {level_index + 1}/{level_total}"
        surf = self._font.render(label, True, C.COLOR_TITLE2)
        y_text = C.TITLE_BAR_HEIGHT + \
            (C.CONTROL_BAR_HEIGHT - surf.get_height()) // 2
        surface.blit(surf, (16, y_text))

        # Define buttons to draw based on mode
        if mode == C.MODE_NORMAL:
            draw_keys = ("prev", "next", "pause", "hint", "undo", "powerup", "reset")
        else:
            draw_keys = ("pause", "hint", "undo", "powerup", "reset")

        for key in draw_keys:
            btn = self._buttons[key]

            # For non-normal mode, we might want to shift the 'pause' button position
            # but let's first implement the hiding logic.
            if key == "pause" and mode != C.MODE_NORMAL:
                # If in challenge mode, we can optionally move the pause button
                # to where 'next' or 'prev' was to keep it tidy, or just keep it there.
                # The prompt suggests re-layout is optional but recommended.
                # Let's keep it simple first.
                pass

            if key == "powerup":
                self._draw_big_powerup_button(
                    surface, btn, mouse_pos, powerup_remain
                )
            elif key == "reset":
                self._draw_big_button(
                    surface, btn, mouse_pos, "Reset"
                )
            elif key == "hint":
                self._draw_big_button(
                    surface, btn, mouse_pos, "Hint"
                )
            elif key == "undo":
                self._draw_big_button(
                    surface, btn, mouse_pos, "Undo"
                )
            else:
                btn.draw(surface, mouse_pos)

    def _draw_big_button(self, surface, btn, mouse_pos, label):
        hovered = mouse_pos is not None and btn.rect.collidepoint(mouse_pos)
        fill = C.COLOR_BUTTON_FILL_HOVER if hovered else C.COLOR_BUTTON_FILL

        pygame.draw.rect(
            surface,
            fill,
            btn.rect,
            border_radius=C.BUTTON_RADIUS,
        )
        pygame.draw.rect(
            surface,
            C.COLOR_BUTTON_BORDER,
            btn.rect,
            width=3,
            border_radius=C.BUTTON_RADIUS,
        )

        text = self._big_font.render(label, True, C.COLOR_BUTTON_TEXT)
        text_rect = text.get_rect(center=btn.rect.center)
        surface.blit(text, text_rect)

    def _draw_big_powerup_button(self, surface, btn, mouse_pos, remain):
        self._draw_big_button(
            surface,
            btn,
            mouse_pos,
            f"Remove ({remain}/3)",
        )

    def action_at(self, pos: tuple[int, int], mode: str = C.MODE_NORMAL) -> str | None:
        for key, btn in self._buttons.items():
            if mode != C.MODE_NORMAL and key in ("prev", "next"):
                continue
            if btn.contains(pos):
                return key
        return None
