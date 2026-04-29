"""Main game class: loop, level index, input events, drawing and victory prompts."""

from __future__ import annotations

import sys
import os

import pygame

from ui.hud import ControlBar
from ui.panels import Menu

from . import constants as C
from .board import Board
from .levels import level_count, load_game_state
from .state import GameState
from .vehicle import Vehicle


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Little Red Car Game")

        self._screen = pygame.display.set_mode((C.WINDOW_WIDTH, C.WINDOW_HEIGHT))
        self._clock = pygame.time.Clock()

        self._board_x = C.BOARD_MARGIN
        self._board_y = C.TOP_SECTION_HEIGHT
        self._board = Board((self._board_x, self._board_y))

        self._level_index = 0
        self._state: GameState = load_game_state(self._level_index)

        self._selected_id: str | None = None
        self._steps = 0
        self._elapsed_ms = 0
        self._won = False
        self._state_name = "MENU"  # "MENU" or "PLAYING"

        self._font_title = pygame.font.Font(None, 28)
        self._font_title.set_bold(True)
        self._font_ui = pygame.font.Font(None, 18)
        self._font_btn = pygame.font.Font(None, 17)
        self._font_win = pygame.font.Font(None, 48)
        self._font_win.set_bold(True)
        self._font_menu_title = pygame.font.Font(None, 56)
        self._font_menu_title.set_bold(True)
        self._font_menu_btn = pygame.font.Font(None, 24)
        self._font_hud_label = pygame.font.Font(None, 42)
        self._font_hud_value = pygame.font.Font(None, 56)

        self._control_bar = ControlBar(C.WINDOW_WIDTH, self._font_btn)
        self._menu = Menu(C.WINDOW_WIDTH, C.WINDOW_HEIGHT, self._font_menu_title, self._font_menu_btn)
        self._menu_bg = pygame.image.load(C.MENU_BG_PATH).convert()
        self._menu_bg = pygame.transform.smoothscale(
            self._menu_bg,
            (C.WINDOW_WIDTH, C.WINDOW_HEIGHT)
        )
        self._board_bg = pygame.image.load(C.BOARD_BG_PATH).convert()
        self._board_bg = pygame.transform.smoothscale(
            self._board_bg,
       (C.BOARD_PIXEL_W, C.BOARD_PIXEL_H)
        )
        self._info_box_bg = pygame.image.load(C.INFO_BOX_BG_PATH).convert_alpha()
        self._info_box_bg = pygame.transform.smoothscale(
            self._info_box_bg,
            (C.INFO_BOX_WIDTH, C.INFO_BOX_HEIGHT)

    )

        self._block_image_files: dict[int, list[str]] = self._load_block_image_files()
        self._block_image_cache: dict[tuple[int, bool, tuple[int, int], str], pygame.Surface] = {}

    def run(self) -> None:
        running = True
        while running:
            dt = self._clock.tick(C.FPS)
            if self._state_name == "PLAYING" and not self._won:
                self._elapsed_ms += dt

            running = self._handle_events()
            self._draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit(0)

    def _load_level(self, index: int) -> None:
        """Switch to a level and reset steps, victory status and selection."""
        n = level_count()
        self._level_index = index % n
        self._state = load_game_state(self._level_index)
        self._steps = 0
        self._elapsed_ms = 0
        self._won = False
        self._selected_id = None

    def _reset_current_level(self) -> None:
        """Reset the current level layout."""
        self._state = load_game_state(self._level_index)
        self._steps = 0
        self._elapsed_ms = 0
        self._won = False
        self._selected_id = None

    def _go_next_level(self) -> None:
        self._load_level(self._level_index + 1)

    def _go_previous_level(self) -> None:
        self._load_level(self._level_index - 1)

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._state_name == "MENU":
                    action = self._menu.action_at(event.pos)
                    if action == "start":
                        self._state_name = "PLAYING"
                        self._reset_current_level()
                    elif action == "exit":
                        return False
                else:
                    self._on_mouse_down(event.pos)
            elif event.type == pygame.KEYDOWN:
                if self._state_name == "PLAYING":
                    self._on_key_down(event.key)
                elif self._state_name == "MENU" and event.key == pygame.K_RETURN:
                    self._state_name = "PLAYING"
                    self._reset_current_level()
        return True

    def _on_mouse_down(self, pos: tuple[int, int]) -> None:
        action = self._control_bar.action_at(pos)
        if action == "reset":
            self._reset_current_level()
            return
        if action == "next":
            self._go_next_level()
            return
        if action == "prev":
            self._go_previous_level()
            return

        if self._won:
            return

        cell = self._screen_pos_to_cell(pos)
        if cell is None:
            self._selected_id = None
            return
        row, col = cell
        v = self._state.occupant_at(row, col)
        self._selected_id = v.id if v else None

    def _on_key_down(self, key: int) -> None:
        if self._won or self._selected_id is None:
            return

        dr, dc = 0, 0
        if key == pygame.K_LEFT:
            dc = -1
        elif key == pygame.K_RIGHT:
            dc = 1
        elif key == pygame.K_UP:
            dr = -1
        elif key == pygame.K_DOWN:
            dr = 1
        else:
            return

        moved = self._state.try_move_step(self._selected_id, dr, dc)
        if moved:
            self._steps += 1
            if self._state.is_won():
                self._won = True

    def _screen_pos_to_cell(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        x, y = pos
        x0, y0 = self._board.topleft
        if not (
            x0 <= x < x0 + C.BOARD_PIXEL_W and y0 <= y < y0 + C.BOARD_PIXEL_H
        ):
            return None
        col = (x - x0) // C.CELL_SIZE
        row = (y - y0) // C.CELL_SIZE
        if 0 <= row < C.GRID_ROWS and 0 <= col < C.GRID_COLS:
            return (row, col)
        return None

    def _draw_title(self) -> None:
        text_surf = self._font_title.render(
            "Little Red Car Game", True, C.COLOR_TITLE
        )
        text_rect = text_surf.get_rect(
            center=(C.WINDOW_WIDTH // 2, C.TITLE_BAR_HEIGHT // 2)
        )
        self._screen.blit(text_surf, text_rect)

    def _draw_hud(self) -> None:
        # Format time
        total_seconds = self._elapsed_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        time_rect = pygame.Rect(C.TIME_BOX_RECT)
        step_rect = pygame.Rect(C.STEP_BOX_RECT)

        # Draw Time box background image
        self._screen.blit(self._info_box_bg, time_rect.topleft)

        time_label = self._font_hud_label.render("Time", True, C.COLOR_TITLE)
        time_label_rect = time_label.get_rect(
            center=(time_rect.centerx, time_rect.y + 38)
        )
        self._screen.blit(time_label, time_label_rect)

        time_value = self._font_hud_value.render(time_str, True, C.COLOR_TITLE)
        time_value_rect = time_value.get_rect(
            center=(time_rect.centerx, time_rect.y + 82)
        )
        self._screen.blit(time_value, time_value_rect)

        # Draw Step box background image
        self._screen.blit(self._info_box_bg, step_rect.topleft)

        step_label = self._font_hud_label.render("Step", True, C.COLOR_TITLE)
        step_label_rect = step_label.get_rect(
            center=(step_rect.centerx, step_rect.y + 38)
        )
        self._screen.blit(step_label, step_label_rect)

        step_value = self._font_hud_value.render(str(self._steps), True, C.COLOR_TITLE)
        step_value_rect = step_value.get_rect(
            center=(step_rect.centerx, step_rect.y + 82)
        )
        self._screen.blit(step_value, step_value_rect)

    def _cell_rect_pixels(self, row: int, col: int) -> pygame.Rect:
        x0, y0 = self._board.topleft
        return pygame.Rect(
            x0 + col * C.CELL_SIZE,
            y0 + row * C.CELL_SIZE,
            C.CELL_SIZE,
            C.CELL_SIZE,
        )

    def _vehicle_draw_rect(self, vehicle: Vehicle) -> pygame.Rect:
        cells = vehicle.cells()
        rects = [self._cell_rect_pixels(r, c) for r, c in cells]
        union = rects[0].copy()
        for r in rects[1:]:
            union.union_ip(r)
        return union.inflate(-2 * C.VEHICLE_INSET, -2 * C.VEHICLE_INSET)

    def _draw_exit_portal(self) -> None:
        x0, y0 = self._board.topleft
        portal_x = x0 + C.BOARD_PIXEL_W
        portal_y = y0 + C.EXIT_ROW * C.CELL_SIZE
        portal = pygame.Rect(portal_x, portal_y, C.EXIT_PORTAL_WIDTH, C.CELL_SIZE)

        pygame.draw.rect(self._screen, C.COLOR_EXIT_PORTAL, portal)
        pygame.draw.rect(self._screen, C.COLOR_EXIT_HIGHLIGHT, portal, 4)

        cy = portal_y + C.CELL_SIZE // 2
        tip = (portal_x + C.EXIT_PORTAL_WIDTH - 6, cy)
        left = (portal_x + 10, cy - 14)
        right = (portal_x + 10, cy + 14)
        pygame.draw.polygon(self._screen, C.COLOR_EXIT_HIGHLIGHT, (tip, left, right))

    def _draw_vehicles(self) -> None:
        for v in self._state.vehicles:
            body = self._vehicle_draw_rect(v)

            image = self._block_image_for_vehicle(v, body.size)

            if image is None:
                # Fallback to the original color block if the image cannot be loaded.
                pygame.draw.rect(self._screen, v.color, body, border_radius=8)
            else:
                self._screen.blit(image, body.topleft)

            if v.is_target:
                pygame.draw.rect(
                    self._screen,
                    C.COLOR_TARGET_OUTLINE,
                    body,
                    width=4,
                    border_radius=8,
                )

            if self._selected_id is not None and v.id == self._selected_id:
                pygame.draw.rect(
                    self._screen,
                    C.COLOR_SELECTION,
                    body.inflate(8, 8),
                    width=4,
                    border_radius=10,
                )

    def _load_block_image_files(self) -> dict[int, list[str]]:
        """Load grass block images from the board_tiles folder automatically."""
        files_by_length = {
            2: [],
            3: [],
        }

        if not os.path.isdir(C.BOARD_TILES_DIR):
            print(f"Warning: block image folder not found: {C.BOARD_TILES_DIR}")
            return files_by_length

        valid_exts = (".png", ".jpg", ".jpeg", ".webp")

        for filename in os.listdir(C.BOARD_TILES_DIR):
            lower_name = filename.lower()

            if not lower_name.endswith(valid_exts):
                continue

            # Reserve the target image for the red car only.
            if lower_name == C.TARGET_BLOCK_IMAGE.lower():
                continue

            # Filenames containing "_L" are used for 3-cell long blocks.
            if "_l" in lower_name:
                files_by_length[3].append(filename)
            else:
                files_by_length[2].append(filename)

        files_by_length[2].sort()
        files_by_length[3].sort()

        return files_by_length

    def _block_image_name(self, vehicle: Vehicle) -> str:
        """Choose a block image based on the vehicle type, length, and id."""
        if vehicle.is_target:
            return C.TARGET_BLOCK_IMAGE

        names = self._block_image_files.get(vehicle.length, [])

        if not names:
            return ""

        index = sum(ord(ch) for ch in vehicle.id) % len(names)
        return names[index]

    def _block_image_for_vehicle(
            self,
            vehicle: Vehicle,
            size: tuple[int, int],
    ) -> pygame.Surface | None:
        """Load, rotate, resize, and cache the grass block image."""
        image_name = self._block_image_name(vehicle)

        if not image_name:
            return None

        key = (vehicle.length, vehicle.horizontal, size, image_name)

        if key in self._block_image_cache:
            return self._block_image_cache[key]

        image_path = os.path.join(C.BOARD_TILES_DIR, image_name)

        if not os.path.exists(image_path):
            return None

        image = pygame.image.load(image_path).convert_alpha()

        # The provided images are horizontal.
        # Rotate the image automatically when the vehicle is vertical.
        if not vehicle.horizontal:
            image = pygame.transform.rotate(image, 90)

        image = pygame.transform.smoothscale(image, size)

        self._block_image_cache[key] = image
        return image

    def _draw_win_overlay(self) -> None:
        """Translucent layer covering board and HUD, keeping title and buttons clickable."""
        w, h = self._screen.get_size()
        y0 = C.TOP_SECTION_HEIGHT
        overlay = pygame.Surface((w, h - y0), pygame.SRCALPHA)
        overlay.fill(C.COLOR_WIN_OVERLAY)
        self._screen.blit(overlay, (0, y0))

        # Prepare stats text
        total_seconds = self._elapsed_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        stats_str = f"step: {self._steps} time: {minutes:02d}:{seconds:02d}"
        stats_surf = self._font_ui.render(stats_str, True, C.COLOR_WIN_TEXT)

        last = self._level_index == level_count() - 1
        line1 = self._font_win.render("You Win!", True, C.COLOR_WIN_TEXT)
        if last:
            line2 = self._font_ui.render(
                "All levels completed!", True, C.COLOR_WIN_TEXT
            )
            panel_w = max(line1.get_width(), line2.get_width(), stats_surf.get_width()) + 80
            panel_h = line1.get_height() + stats_surf.get_height() + line2.get_height() + 72
        else:
            line2 = None
            panel_w = max(line1.get_width(), stats_surf.get_width()) + 80
            panel_h = line1.get_height() + stats_surf.get_height() + 64

        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (C.WINDOW_WIDTH // 2, C.WINDOW_HEIGHT // 2)
        pygame.draw.rect(self._screen, C.COLOR_WIN_PANEL, panel, border_radius=12)
        pygame.draw.rect(
            self._screen, C.COLOR_EXIT_HIGHLIGHT, panel, width=3, border_radius=12
        )

        y = panel.top + 24
        r1 = line1.get_rect(centerx=panel.centerx, top=y)
        self._screen.blit(line1, r1)

        r_stats = stats_surf.get_rect(centerx=panel.centerx, top=r1.bottom + 12)
        self._screen.blit(stats_surf, r_stats)

        if line2 is not None:
            r2 = line2.get_rect(
                centerx=panel.centerx, top=r_stats.bottom + 12,
            )
            self._screen.blit(line2, r2)


    def _draw(self) -> None:
        mouse = pygame.mouse.get_pos()

        if self._state_name == "MENU":
            self._screen.blit(self._menu_bg, (0, 0))
            self._menu.draw(self._screen, mouse)
            return

        self._screen.fill(C.COLOR_BG)

        self._draw_title()

        self._control_bar.draw(
            self._screen,
            mouse,
            self._level_index,
            level_count(),
        )

        self._board.draw(self._screen, self._board_bg)
        self._draw_exit_portal()
        self._draw_vehicles()
        self._draw_hud()

        if self._won:
            self._draw_win_overlay()
