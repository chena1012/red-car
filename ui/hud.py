"""Top control bar: level info and Reset / Previous / Next buttons."""

from __future__ import annotations

import pygame

from game import constants as C

from .button import Button


class ControlBar:
    """Draws level info and functional buttons in the UI layout.
    Manages button positioning, rendering, and click detection for game controls.
    """

    def __init__(self, screen_width: int, font: pygame.font.Font) -> None:
        """Initialize the control bar with UI fonts, images, and button layout.
        
        Args:
            screen_width: Total width of the game window
            font: Base font for UI text rendering
        """
        self._screen_width = screen_width
        self._font = font
        self._big_font = pygame.font.Font(None, 30)
        self._top_font = pygame.font.Font(None, 26)
        self._buttons: dict[str, Button] = {}
        # Load bone button background image once.
        self._bone_button_img = pygame.image.load(C.BONE_BUTTON_PATH).convert_alpha()
        self._layout()
        self._level_font = pygame.font.Font(None, 36)
        self._level_font.set_bold(True)

    def _layout(self) -> None:
        """Configure position and size for all control buttons.
        Separates buttons into top-right navigation bar and bottom functional area.
        """
        specs = [
            ("hint", "Hint"),
            ("undo", "Undo"),
            ("remove", "Remove"),
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
        top_button_h =70
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

            if key == "prev":
                x += bw + 45
            else:
                x += bw + 16
        # Move Remove, Reset and Hint to the lower area, and make them larger.
        big_w = 165
        big_h = 82
        bottom_y = C.WINDOW_HEIGHT - 90

        # Adjust the x-coordinate to align the three buttons side by side.
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

        self._buttons["remove"] = Button(
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
        remove_remain: int,
        mode: str = C.MODE_NORMAL,
    ) -> None:
        """Render the control bar, level label, and all visible buttons.
        
        Args:
            surface: Pygame surface to draw on
            mouse_pos: Current mouse coordinates for hover effects
            level_index: Index of the current level
            level_total: Total number of available levels
            remove_remain: Remaining uses for the remove feature
            mode: Current game mode (normal/challenge)
        """
        label = f"Level {level_index + 1}/{level_total}"
        surf = self._level_font.render(label, True, C.COLOR_TITLE2)
        y_text = C.TITLE_BAR_HEIGHT + \
                 (C.CONTROL_BAR_HEIGHT - surf.get_height()) // 2
        surface.blit(surf, (16, y_text))

        # Define buttons to draw based on mode
        if mode == C.MODE_NORMAL:
            draw_keys = ("prev", "next", "pause", "hint", "undo", "remove", "reset")
        else:
            draw_keys = ("pause", "hint", "undo", "remove", "reset")

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

            if key == "remove":
                self._draw_big_remove_button(
                    surface, btn, mouse_pos, remove_remain
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
                label_map = {
                    "prev": "Previous Level",
                    "next": "Next Level",
                    "pause": "Pause",
                }
                self._draw_top_bone_button(
                    surface,
                    btn,
                    mouse_pos,
                    label_map[key],
                )

    def _draw_big_button(self, surface, btn, mouse_pos, label):
        """Render a large functional button with bone background and hover effect.
        
        Args:
            surface: Pygame surface to draw on
            btn: Button object to render
            mouse_pos: Current mouse coordinates for hover detection
            label: Text to display on the button
        """
        hovered = mouse_pos is not None and btn.rect.collidepoint(mouse_pos)

        # Do not stretch the bone image.
        # Keep the original image ratio and only control its height.
        bone_h = int(btn.rect.height * (0.95 if not hovered else 1.05))

        original_w = self._bone_button_img.get_width()
        original_h = self._bone_button_img.get_height()
        bone_w = int(original_w * bone_h / original_h)

        img = pygame.transform.smoothscale(
            self._bone_button_img,
            (bone_w, bone_h)
        )

        # Put the bone on the left side of the button area.
        img_rect = img.get_rect()
        img_rect.midleft = (btn.rect.left + 8, btn.rect.centery)

        surface.blit(img, img_rect)

        # Draw text on top of the bone.
        text = self._big_font.render(label, True, C.COLOR_TITLE2)

        text_rect = text.get_rect(
            center=(img_rect.centerx + 35, img_rect.centery)
        )

        surface.blit(text, text_rect)

    def _draw_top_bone_button(self, surface, btn, mouse_pos, label):
        """Render a small top navigation button with bone background.
        
        Args:
            surface: Pygame surface to draw on
            btn: Button object to render
            mouse_pos: Current mouse coordinates for hover detection
            label: Text to display on the button
        """
        hovered = mouse_pos is not None and btn.rect.collidepoint(mouse_pos)

        bone_h = int(btn.rect.height * (0.95 if not hovered else 1.05))

        original_w = self._bone_button_img.get_width()
        original_h = self._bone_button_img.get_height()
        bone_w = int(original_w * bone_h / original_h)

        img = pygame.transform.smoothscale(
            self._bone_button_img,
            (bone_w, bone_h)
        )

        img_rect = img.get_rect()
        img_rect.midleft = (btn.rect.left + 8, btn.rect.centery)

        surface.blit(img, img_rect)

        text = self._top_font.render(label, True, C.COLOR_TITLE2)

        text_rect = text.get_rect(
            midleft=(img_rect.left + 18, btn.rect.centery)
        )

        surface.blit(text, text_rect)

    def _draw_big_remove_button(self, surface, btn, mouse_pos, remain):
        """Render the remove button with remaining usage count.
        
        Args:
            surface: Pygame surface to draw on
            btn: Button object to render
            mouse_pos: Current mouse coordinates for hover detection
            remain: Number of remaining remove uses
        """
        self._draw_big_button(
            surface,
            btn,
            mouse_pos,
            f"Remove ({remain}/3)",
        )

    def action_at(self, pos: tuple[int, int], mode: str = C.MODE_NORMAL) -> str | None:
        """Detect which button was clicked at the given position.
        
        Args:
            pos: Mouse click coordinates
            mode: Current game mode to filter visible buttons
        Returns:
            Button key if clicked, None otherwise
        """
        for key, btn in self._buttons.items():
            if mode != C.MODE_NORMAL and key in ("prev", "next"):
                continue
            if btn.contains(pos):
                return key
        return None