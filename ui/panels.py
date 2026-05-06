"""Info panels and Menu screen implementation."""

from __future__ import annotations
from game.audio import audio

import pygame

from game import constants as C
from .button import Button, CircleButton


class Menu:
    """Main game start menu with Start and Exit interactive buttons.
    Handles UI layout, rendering, and mouse click detection for the main menu.
    """

    def __init__(self, screen_width: int, screen_height: int, title_font: pygame.font.Font, button_font: pygame.font.Font) -> None:
        """Initialize the main menu with screen dimensions and fonts.
        
        Args:
            screen_width: Total width of the game window
            screen_height: Total height of the game window
            title_font: Font for rendering menu title
            button_font: Font for rendering button text
        """
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
        """Configure position, size, and style for all menu buttons."""
        # Title vertical position
        self._title_y = self._screen_height // 4

        # Button configuration
        specs = [
            ("start", "Start"),
            ("exit", "Exit"),
        ]

        button_w = 200
        button_h = 50
        gap = 20

        total_height = (button_h * len(specs)) + (gap * (len(specs) - 1))

        # Vertical offset to position buttons below title art
        button_offset_y = 90
        start_y = self._screen_height // 2 + button_offset_y

        x = (self._screen_width - button_w) // 2
        y = start_y

        self._buttons.clear()
        for key, label in specs:
            rect = pygame.Rect(x, y, button_w, button_h)
            my_font = pygame.font.Font(None, 40)
            self._buttons[key] = Button(rect, label, my_font, border_radius=60)
            self._buttons[key].set_colors(fill=(255, 170, 140), hover=(
                249, 207, 119), border=(249, 207, 119))
            y += button_h + gap

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int] | None) -> None:
        """Render menu buttons on the screen.
        Background/title rendering is handled in the main game loop.
        
        Args:
            surface: Pygame surface to draw on
            mouse_pos: Current mouse coordinates for hover effects
        """
        # Draw Buttons
        for btn in self._buttons.values():
            btn.draw(surface, mouse_pos)

    def action_at(self, pos: tuple[int, int]) -> str | None:
        """Detect which menu button was clicked.
        
        Args:
            pos: Mouse click coordinates
        Returns:
            Button key (start/exit) if clicked, None otherwise
        """
        for key, btn in self._buttons.items():
            if btn.contains(pos):
                audio.play_click()
                return key
        return None


class LevelSelect:
    """Level selection screen with level buttons, challenge modes, and navigation.
    Manages level unlocking, star ratings, and time/step challenge modes.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        title_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        """Initialize level selection screen with dimensions and UI assets.
        
        Args:
            screen_width: Game window width
            screen_height: Game window height
            title_font: Font for screen title
            button_font: Font for level/mode buttons
        """
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._title_font = title_font
        self._button_font = button_font
        self._level_buttons: list[tuple[int, Button]] = []
        self._mode_buttons: list[tuple[int, str, CircleButton]] = []
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
        """Load an image file and scale it to the target size.
        
        Args:
            path: Image file path
            size: Target (width, height)
            use_alpha: Enable transparency if True
        Returns:
            Scaled Pygame surface, None on failure
        """
        try:
            image = pygame.image.load(path)
            image = image.convert_alpha() if use_alpha else image.convert()
            return pygame.transform.smoothscale(image, size)
        except pygame.error:
            return None

    def _get_challenge_button_positions(self, level_index: int) -> dict[str, tuple[int, int]]:
        """Get fixed screen positions for Time/Step challenge buttons per level.
        
        Args:
            level_index: Index of the current level
        Returns:
            Dictionary with 'time' and 'step' button coordinates
        """
        w = self._screen_width
        h = self._screen_height
        
        # Predefined proportional positions for each level
        layouts = [
            {"time": (0.18, 0.505), "step": (0.25, 0.515)},  # Level 1
            {"time": (0.42, 0.537), "step": (0.49, 0.515)},  # Level 2
            {"time": (0.65, 0.465), "step": (0.72, 0.480)},  # Level 3
            {"time": (0.85, 0.53), "step": (0.92, 0.535)},  # Level 4
        ]
        
        if level_index < len(layouts):
            layout = layouts[level_index]
            return {
                "time": (int(w * layout["time"][0]), int(h * layout["time"][1])),
                "step": (int(w * layout["step"][0]), int(h * layout["step"][1]))
            }
        
        # Fallback position for extra levels
        pos = C.LEVEL_BUTTON_POSITIONS[level_index] if level_index < len(C.LEVEL_BUTTON_POSITIONS) else (0,0)
        return {
            "time": (pos[0] - 40, pos[1] + 80),
            "step": (pos[0] + 40, pos[1] + 80)
        }

    def _layout(self, level_total: int) -> None:
        """Create and position all level and challenge mode buttons.
        
        Args:
            level_total: Total number of game levels
        """
        self._level_buttons.clear()

        button_size = C.LEVEL_BUTTON_SIZE
        positions = C.LEVEL_BUTTON_POSITIONS

        self._mode_buttons.clear()

        for i in range(level_total):
            if i < len(positions):
                center_x, center_y = positions[i]
            else:
                # Auto-position for additional levels
                extra = i - len(positions)
                center_x = 220 + (extra % 4) * 190
                center_y = 520 + (extra // 4) * 110

            rect = pygame.Rect(0, 0, button_size, button_size)
            rect.center = (center_x, center_y)
            self._level_buttons.append(
                (i, Button(rect, f"Level {i + 1}", self._button_font))
            )

            # Create challenge mode buttons
            radius = 28
            chal_pos = self._get_challenge_button_positions(i)
            
            self._mode_buttons.append(
                (i, C.MODE_LIMITED_TIME, CircleButton(
                    chal_pos["time"], radius, "Time", self._button_font))
            )
            self._mode_buttons.append(
                (i, C.MODE_LIMITED_STEP, CircleButton(
                    chal_pos["step"], radius, "Step", self._button_font))
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
        """Draw text with white shadow for better readability on backgrounds.
        
        Args:
            surface: Draw target surface
            text: Text to render
            font: Text font
            color: Main text color
            center: Center coordinates for text
        """
        shadow_surf = font.render(text, True, (255, 255, 255))
        shadow_rect = shadow_surf.get_rect(
            center=(center[0] + 2, center[1] + 2))
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
        """Draw a single level button with unlock status and star rating.
        
        Args:
            surface: Draw target surface
            btn: Button object
            level_index: Level number
            unlocked: True if level is playable
            stars: Earned star count (0-3)
        """
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

        # Draw level text and star count
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
        """Draw styled back button for navigation.
        
        Args:
            surface: Draw target surface
            mouse_pos: Mouse coordinates for hover effect
        """
        if self._back_button is None:
            return

        hovered = mouse_pos is not None and self._back_button.contains(
            mouse_pos)

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
        challenge_clears: dict[str, bool],
    ) -> None:
        """Render full level selection screen with all UI elements.
        
        Args:
            surface: Draw target surface
            mouse_pos: Mouse coordinates
            level_total: Total levels
            unlocked_count: Number of unlocked levels
            stars_by_level: Star rating per level
            challenge_clears: Challenge mode completion status
        """
        self._layout(level_total)

        if self._level_bg is not None:
            surface.blit(self._level_bg, (0, 0))
        else:
            surface.fill(C.COLOR_BG)

        # Draw title with shadow
        title = self._title_font.render("Select Level", True, C.COLOR_TITLE)
        title_shadow = self._title_font.render(
            "Select Level", True, (82, 104, 64))

        title_rect = title.get_rect(
            center=(self._screen_width // 2, 82)
        )
        shadow_rect = title_shadow.get_rect(
            center=(self._screen_width // 2 + 3, 85)
        )

        surface.blit(title_shadow, shadow_rect)
        surface.blit(title, title_rect)

        # Draw all level buttons
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

        # Draw challenge mode buttons
        for level_index, mode_key, btn in self._mode_buttons:
            unlocked = level_index < unlocked_count
            stars = max(0, min(3, int(stars_by_level.get(level_index, 0))))
            if unlocked and stars == 3:
                clear_key = f"{level_index}:{mode_key}"
                is_cleared = bool(challenge_clears.get(clear_key, False))
                btn.draw(surface, mouse_pos, cleared=is_cleared)

        self._draw_back_button(surface, mouse_pos)

    def action_at(
        self,
        pos: tuple[int, int],
        unlocked_count: int,
        stars_by_level: dict[int, int],
    ) -> str | tuple[str, int] | tuple[str, int, str] | None:
        """Detect user interactions on the level select screen.
        
        Args:
            pos: Click coordinates
            unlocked_count: Unlocked level count
            stars_by_level: Star ratings
        Returns:
            Interaction type and data (level, mode, back, locked)
        """
        # Check challenge mode buttons
        for level_index, mode_key, btn in self._mode_buttons:
            if btn.contains(pos):
                unlocked = level_index < unlocked_count
                stars = max(0, min(3, int(stars_by_level.get(level_index, 0))))
                if unlocked and stars == 3:
                    audio.play_click()
                    return ("mode", level_index, mode_key)

        # Check level buttons
        for i, btn in self._level_buttons:
            if btn.contains(pos):
                if i < unlocked_count:
                    audio.play_click()
                    return ("level", i)
                return "locked"

        # Check back button
        if self._back_button is not None and self._back_button.contains(pos):
            audio.play_click()
            return "back"

        return None


class PausePanel:
    """In-game pause menu overlay with continue and exit options.
    Displays a semi-transparent overlay with control buttons.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        title_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        """Initialize pause menu panel.
        
        Args:
            screen_width: Game window width
            screen_height: Game window height
            title_font: Pause title font
            button_font: Button text font
        """
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._title_font = title_font
        self._button_font = button_font
        self._buttons: dict[str, Button] = {}
        self._layout()

    def _layout(self) -> None:
        """Position and style pause menu buttons."""
        button_w = 200
        button_h = 50
        gap = 20
        x = (self._screen_width - button_w) // 2
        start_y = self._screen_height // 2 - 40
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
            self._buttons[key].set_colors(fill=C.COLOR_TITLE1, hover=(
                249, 207, 119), border=C.COLOR_TITLE1)
            y += button_h + gap

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int] | None) -> None:
        """Render pause overlay and menu UI.
        
        Args:
            surface: Draw target surface
            mouse_pos: Mouse coordinates for hover effects
        """
        # Semi-transparent dark overlay
        overlay = pygame.Surface(
            (self._screen_width, self._screen_height), pygame.SRCALPHA)
        overlay.fill((10, 14, 20, 160))
        surface.blit(overlay, (0, 0))

        # Central panel background
        panel_w = 400
        panel_h = 360
        panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        panel_rect.center = (self._screen_width // 2, self._screen_height // 2)
        
        pygame.draw.rect(surface, (120,177,124), panel_rect, border_radius=15)
        pygame.draw.rect(surface, C.COLOR_TITLE, panel_rect, width=4, border_radius=15)

        # Pause title
        title = self._title_font.render("Paused", True, C.COLOR_WIN_TEXT)
        title_rect = title.get_rect(
            center=(self._screen_width // 2, panel_rect.top + 60))
        surface.blit(title, title_rect)

        # Draw all buttons
        for btn in self._buttons.values():
            btn.draw(surface, mouse_pos)

    def action_at(self, pos: tuple[int, int]) -> str | None:
        """Detect clicks on pause menu buttons.
        
        Args:
            pos: Mouse click coordinates
        Returns:
            Button key (continue/save_exit/exit_no_save)
        """
        for key, btn in self._buttons.items():
            if btn.contains(pos):
                audio.play_click()
                return key
        return None