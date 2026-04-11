"""游戏主类：主循环、关卡索引、输入事件、绘制与胜利提示。"""

from __future__ import annotations

import sys

import pygame

from ui.hud import ControlBar

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
        self._won = False

        try:
            self._font_title = pygame.font.SysFont("segoeui", 28, bold=True)
            self._font_ui = pygame.font.SysFont("segoeui", 18)
            self._font_btn = pygame.font.SysFont("segoeui", 17)
            self._font_win = pygame.font.SysFont("segoeui", 48, bold=True)
        except OSError:
            self._font_title = pygame.font.Font(None, 32)
            self._font_ui = pygame.font.Font(None, 20)
            self._font_btn = pygame.font.Font(None, 19)
            self._font_win = pygame.font.Font(None, 52)

        self._control_bar = ControlBar(C.WINDOW_WIDTH, self._font_btn)

    def run(self) -> None:
        running = True
        while running:
            running = self._handle_events()
            self._draw()
            pygame.display.flip()
            self._clock.tick(C.FPS)
        pygame.quit()
        sys.exit(0)

    def _load_level(self, index: int) -> None:
        """切换到指定关卡并清空本关步数、胜利与选中状态。"""
        n = level_count()
        self._level_index = index % n
        self._state = load_game_state(self._level_index)
        self._steps = 0
        self._won = False
        self._selected_id = None

    def _reset_current_level(self) -> None:
        """恢复当前关初始布局（步数归零，可继续玩）。"""
        self._state = load_game_state(self._level_index)
        self._steps = 0
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
                self._on_mouse_down(event.pos)
            elif event.type == pygame.KEYDOWN:
                self._on_key_down(event.key)
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
        steps_surf = self._font_ui.render(f"步数: {self._steps}", True, C.COLOR_TITLE)
        steps_rect = steps_surf.get_rect(
            bottomright=(C.WINDOW_WIDTH - 16, C.WINDOW_HEIGHT - 12)
        )
        self._screen.blit(steps_surf, steps_rect)

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
            pygame.draw.rect(self._screen, v.color, body, border_radius=8)
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

    def _draw_win_overlay(self) -> None:
        """半透明层只盖住棋盘与底部 HUD，保留顶部标题与按钮可点（便于胜利后点 Next）。"""
        w, h = self._screen.get_size()
        y0 = C.TOP_SECTION_HEIGHT
        overlay = pygame.Surface((w, h - y0), pygame.SRCALPHA)
        overlay.fill(C.COLOR_WIN_OVERLAY)
        self._screen.blit(overlay, (0, y0))

        last = self._level_index == level_count() - 1
        line1 = self._font_win.render("You Win!", True, C.COLOR_WIN_TEXT)
        if last:
            line2 = self._font_ui.render(
                "All levels completed!", True, C.COLOR_WIN_TEXT
            )
            panel_w = max(line1.get_width(), line2.get_width()) + 80
            panel_h = line1.get_height() + line2.get_height() + 56
        else:
            line2 = None
            panel_w = line1.get_width() + 80
            panel_h = line1.get_height() + 48

        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (C.WINDOW_WIDTH // 2, C.WINDOW_HEIGHT // 2)
        pygame.draw.rect(self._screen, C.COLOR_WIN_PANEL, panel, border_radius=12)
        pygame.draw.rect(
            self._screen, C.COLOR_EXIT_HIGHLIGHT, panel, width=3, border_radius=12
        )

        y = panel.top + 24
        r1 = line1.get_rect(centerx=panel.centerx, top=y)
        self._screen.blit(line1, r1)
        if line2 is not None:
            r2 = line2.get_rect(
                centerx=panel.centerx, top=r1.bottom + 12,
            )
            self._screen.blit(line2, r2)

    def _draw(self) -> None:
        self._screen.fill(C.COLOR_BG)
        self._draw_title()
        mouse = pygame.mouse.get_pos()
        self._control_bar.draw(
            self._screen,
            mouse,
            self._level_index,
            level_count(),
        )
        self._board.draw(self._screen)
        self._draw_exit_portal()
        self._draw_vehicles()
        self._draw_hud()
        if self._won:
            self._draw_win_overlay()
