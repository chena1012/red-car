"""Info panels and Menu screen implementation."""

from __future__ import annotations
from game.audio import audio

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

        self.click_sound = None
        try:
            self.click_sound = pygame.mixer.Sound(C.SFX_CLICK)
            self.click_sound.set_volume(0.6)
        except:
            print("No click sound found")

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

        # Move menu buttons lower to avoid covering the title/background art.
        button_offset_y = 90
        start_y = self._screen_height // 2 + button_offset_y

        x = (self._screen_width - button_w) // 2
        y = start_y

        self._buttons.clear()
        for key, label in specs:
            rect = pygame.Rect(x, y, button_w, button_h)
            self._buttons[key] = Button(rect, label, self._button_font)
            y += button_h + gap

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int] | None) -> None:
        # The menu background and title are drawn in game/game.py.
        # Only draw the menu buttons here so the background image stays visible.

        # Draw Buttons
        for btn in self._buttons.values():
            btn.draw(surface, mouse_pos)

    def action_at(self, pos: tuple[int, int]) -> str | None:
        for key, btn in self._buttons.items():
            if btn.contains(pos):
                from game.audio import audio
                audio.play_click()
                return key
        return None


class LevelSelect:
    """Level selection screen between main menu and gameplay."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        title_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._title_font = title_font
        self._button_font = button_font
        self._level_buttons: list[tuple[int, Button]] = []
        self._back_button: Button | None = None

        self._level_bg = self._load_scaled_image(
            C.LEVEL_BG_PATH,
            (self._screen_width, self._screen_height),
            use_alpha=False,
        )

        self._level_button_img = self._load_scaled_image(
            C.LEVEL_BUTTON_PATH,
            (C.LEVEL_BUTTON_SIZE, C.LEVEL_BUTTON_SIZE),
            use_alpha=True,
        )

    def _load_scaled_image(
        self,
        path: str,
        size: tuple[int, int],
        use_alpha: bool = True,
    ) -> pygame.Surface | None:
        """Load and scale an image. Return None if the asset is missing."""
        try:
            image = pygame.image.load(path)
            image = image.convert_alpha() if use_alpha else image.convert()
            return pygame.transform.smoothscale(image, size)
        except pygame.error:
            return None

    def _layout(self, level_total: int) -> None:
        self._level_buttons.clear()

        button_size = C.LEVEL_BUTTON_SIZE
        positions = C.LEVEL_BUTTON_POSITIONS

        for i in range(level_total):
            if i < len(positions):
                center_x, center_y = positions[i]
            else:
                # Fallback positions if more levels are added later.
                extra = i - len(positions)
                center_x = 220 + (extra % 4) * 190
                center_y = 520 + (extra // 4) * 110

            rect = pygame.Rect(0, 0, button_size, button_size)
            rect.center = (center_x, center_y)

            self._level_buttons.append(
                (i, Button(rect, f"Level {i + 1}", self._button_font))
            )

        self._back_button = Button(
            pygame.Rect(C.LEVEL_BACK_BUTTON_RECT),
            "Back",
            self._button_font,
        )

    def _draw_text_with_shadow(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        center: tuple[int, int],
    ) -> None:
        """Draw readable text on top of the light paw image."""
        shadow_surf = font.render(text, True, (255, 255, 255))
        shadow_rect = shadow_surf.get_rect(center=(center[0] + 2, center[1] + 2))
        surface.blit(shadow_surf, shadow_rect)

        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=center)
        surface.blit(text_surf, text_rect)

    def _draw_level_button(
        self,
        surface: pygame.Surface,
        btn: Button,
        level_index: int,
        unlocked: bool,
        stars: int,
    ) -> None:
        """Draw one paw-shaped level button without changing its click logic."""
        if self._level_button_img is not None:
            surface.blit(self._level_button_img, btn.rect.topleft)
        else:
            pygame.draw.rect(
                surface,
                C.COLOR_BUTTON_FILL,
                btn.rect,
                border_radius=C.BUTTON_RADIUS,
            )
            pygame.draw.rect(
                surface,
                C.COLOR_BUTTON_BORDER,
                btn.rect,
                width=2,
                border_radius=C.BUTTON_RADIUS,
            )

        if unlocked:
            title_text = f"Level {level_index + 1}"
            text_color = (77, 60, 38)
        else:
            title_text = "LOCKED"
            text_color = (95, 95, 95)

        # Put both lines on the larger lower part of the paw.
        self._draw_text_with_shadow(
            surface,
            title_text,
            self._button_font,
            text_color,
            (btn.rect.centerx, btn.rect.centery + 18),
        )

        self._draw_text_with_shadow(
            surface,
            f"Stars: {stars}/3",
            self._button_font,
            text_color,
            (btn.rect.centerx, btn.rect.centery + 44),
        )

    def _draw_back_button(
            self,
            surface: pygame.Surface,
            mouse_pos: tuple[int, int] | None,
    ) -> None:
        """Draw the Back button with an orange style."""
        if self._back_button is None:
            return

        hovered = mouse_pos is not None and self._back_button.contains(mouse_pos)

        fill_color = (255, 173, 135) if not hovered else (255, 190, 150)
        border_color = (255, 219, 128)
        text_color = (255, 255, 255)

        pygame.draw.rect(
            surface,
            fill_color,
            self._back_button.rect,
            border_radius=18,
        )

        pygame.draw.rect(
            surface,
            border_color,
            self._back_button.rect,
            width=3,
            border_radius=18,
        )

        text_surf = self._button_font.render("Back", True, text_color)
        text_rect = text_surf.get_rect(center=self._back_button.rect.center)
        surface.blit(text_surf, text_rect)

    def draw(
        self,
        surface: pygame.Surface,
        mouse_pos: tuple[int, int] | None,
        level_total: int,
        unlocked_count: int,
        stars_by_level: dict[int, int],
    ) -> None:
        self._layout(level_total)

        if self._level_bg is not None:
            surface.blit(self._level_bg, (0, 0))
        else:
            surface.fill(C.COLOR_BG)

        title = self._title_font.render("Select Level", True, C.COLOR_TITLE)
        title_shadow = self._title_font.render("Select Level", True, (82, 104, 64))

        title_rect = title.get_rect(
            center=(self._screen_width // 2, 82)
        )
        shadow_rect = title_shadow.get_rect(
            center=(self._screen_width // 2 + 3, 85)
        )

        surface.blit(title_shadow, shadow_rect)
        surface.blit(title, title_rect)

        for i, btn in self._level_buttons:
            unlocked = i < unlocked_count
            stars = max(0, min(3, int(stars_by_level.get(i, 0))))

            self._draw_level_button(
                surface,
                btn,
                i,
                unlocked,
                stars,
            )

        self._draw_back_button(surface, mouse_pos)

    def action_at(
        self, pos: tuple[int, int], unlocked_count: int
    ) -> str | tuple[str, int] | None:
        for i, btn in self._level_buttons:
            if btn.contains(pos):
                if i < unlocked_count:
                    audio.play_click()
                    return ("level", i)
                return "locked"

        if self._back_button is not None and self._back_button.contains(pos):
            audio.play_click()
            return "back"

        return None


class PausePanel:
    """Pause overlay with Continue / Exit choices."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        title_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._title_font = title_font
        self._button_font = button_font
        self._buttons: dict[str, Button] = {}
        self._layout()

    def _layout(self) -> None:
        button_w = 260
        button_h = 48
        gap = 16
        x = (self._screen_width - button_w) // 2
        start_y = self._screen_height // 2 - 10
        specs = [
            ("continue", "Continue"),
            ("save_exit", "Save and Exit"),
            ("exit_no_save", "Exit Without Saving"),
        ]
        self._buttons.clear()
        y = start_y
        for key, label in specs:
            self._buttons[key] = Button(
                (x, y, button_w, button_h), label, self._button_font)
            y += button_h + gap

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int] | None) -> None:
        overlay = pygame.Surface(
            (self._screen_width, self._screen_height), pygame.SRCALPHA)
        overlay.fill((10, 14, 20, 180))
        surface.blit(overlay, (0, 0))

        title = self._title_font.render("Paused", True, C.COLOR_WIN_TEXT)
        title_rect = title.get_rect(
            center=(self._screen_width // 2, self._screen_height // 2 - 72))
        surface.blit(title, title_rect)

        for btn in self._buttons.values():
            btn.draw(surface, mouse_pos)

    def action_at(self, pos: tuple[int, int]) -> str | None:
        for key, btn in self._buttons.items():
            if btn.contains(pos):
                audio.play_click()
                return key
        return None
