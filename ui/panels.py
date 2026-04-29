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

        # Move menu buttons lower
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

    def _layout(self, level_total: int) -> None:
        self._level_buttons.clear()
        cols = 4
        button_w = 120
        button_h = 72
        gap_x = 18
        gap_y = 18
        rows = (level_total + cols - 1) // cols
        total_w = cols * button_w + (cols - 1) * gap_x
        total_h = rows * button_h + (rows - 1) * gap_y
        start_x = (self._screen_width - total_w) // 2
        start_y = self._screen_height // 2 - total_h // 2 + 30

        for i in range(level_total):
            row = i // cols
            col = i % cols
            x = start_x + col * (button_w + gap_x)
            y = start_y + row * (button_h + gap_y)
            self._level_buttons.append(
                (i, Button((x, y, button_w, button_h), f"Level {i + 1}", self._button_font))
            )

        back_rect = pygame.Rect(
            (self._screen_width - 200) // 2,
            self._screen_height - 90,
            200,
            44,
        )
        self._back_button = Button(back_rect, "Back", self._button_font)

    def draw(
        self,
        surface: pygame.Surface,
        mouse_pos: tuple[int, int] | None,
        level_total: int,
        unlocked_count: int,
        stars_by_level: dict[int, int],
    ) -> None:
        self._layout(level_total)
        surface.fill(C.COLOR_BG)
        title = self._title_font.render("Select Level", True, C.COLOR_TITLE)
        title_rect = title.get_rect(center=(self._screen_width // 2, self._screen_height // 4))
        surface.blit(title, title_rect)

        for i, btn in self._level_buttons:
            unlocked = i < unlocked_count
            btn.draw(surface, mouse_pos if unlocked else None)
            stars = max(0, min(3, int(stars_by_level.get(i, 0))))
            stars_surf = self._button_font.render(f"Stars: {stars}/3", True, C.COLOR_BUTTON_TEXT)
            stars_rect = stars_surf.get_rect(center=(btn.rect.centerx, btn.rect.bottom - 14))
            surface.blit(stars_surf, stars_rect)
            if not unlocked:
                lock_surf = self._button_font.render("LOCKED", True, C.COLOR_WIN_TEXT)
                lock_rect = lock_surf.get_rect(center=btn.rect.center)
                shade = pygame.Surface(btn.rect.size, pygame.SRCALPHA)
                shade.fill((10, 12, 16, 170))
                surface.blit(shade, btn.rect.topleft)
                surface.blit(lock_surf, lock_rect)

        if self._back_button is not None:
            self._back_button.draw(surface, mouse_pos)

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
            self._buttons[key] = Button((x, y, button_w, button_h), label, self._button_font)
            y += button_h + gap

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int] | None) -> None:
        overlay = pygame.Surface((self._screen_width, self._screen_height), pygame.SRCALPHA)
        overlay.fill((10, 14, 20, 180))
        surface.blit(overlay, (0, 0))

        title = self._title_font.render("Paused", True, C.COLOR_WIN_TEXT)
        title_rect = title.get_rect(center=(self._screen_width // 2, self._screen_height // 2 - 72))
        surface.blit(title, title_rect)

        for btn in self._buttons.values():
            btn.draw(surface, mouse_pos)

    def action_at(self, pos: tuple[int, int]) -> str | None:
        for key, btn in self._buttons.items():
            if btn.contains(pos):
                audio.play_click()
                return key
        return None
