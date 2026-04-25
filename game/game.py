"""Main game class: loop, level index, input events, drawing and victory prompts."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from math import cos, pi, sin

import pygame

from ui.hud import ControlBar
from ui.panels import Menu

from . import constants as C
from .board import Board
from .levels import level_count, load_game_state
from .state import GameState
from .vehicle import Vehicle


@dataclass
class MoveAnimation:
    vehicle_id: str
    distance: int
    elapsed_ms: int
    duration_ms: int


@dataclass(frozen=True)
class WinStars:
    clear: bool
    time: bool
    best_steps: bool

    @property
    def total(self) -> int:
        return int(self.clear) + int(self.time) + int(self.best_steps)


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
        self._powerup_activity = False
        self._removed_cars: set[str] = set()
        self._powerup_remain = 3

        self._steps = 0
        self._elapsed_ms = 0
        self._won = False
        self._state_name = "MENU"  # "MENU" or "PLAYING"
        self._move_anim: MoveAnimation | None = None
        self._best_steps_by_level: dict[int, int] = {}

        self._font_title = pygame.font.Font(None, 28)
        self._font_title.set_bold(True)
        self._font_ui = pygame.font.Font(None, 18)
        self._font_btn = pygame.font.Font(None, 17)
        self._font_win = pygame.font.Font(None, 48)
        self._font_win.set_bold(True)
        self._font_menu_title = pygame.font.Font(None, 56)
        self._font_menu_title.set_bold(True)
        self._font_menu_btn = pygame.font.Font(None, 24)

        self._control_bar = ControlBar(C.WINDOW_WIDTH, self._font_btn)
        self._menu = Menu(C.WINDOW_WIDTH, C.WINDOW_HEIGHT, self._font_menu_title, self._font_menu_btn)

        self._board_bg = pygame.image.load(C.BOARD_BG_PATH).convert()
        self._board_bg = pygame.transform.smoothscale(
            self._board_bg,
       (C.BOARD_PIXEL_W, C.BOARD_PIXEL_H)
        )

    def run(self) -> None:
        running = True
        while running:
            dt = self._clock.tick(C.FPS)
            if self._state_name == "PLAYING" and not self._won:
                self._elapsed_ms += dt

            running = self._handle_events()
            self._update(dt)
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
        self._removed_cars.clear()
        self._powerup_remain = 3
        self._move_anim = None

    def _reset_current_level(self) -> None:
        """Reset the current level layout."""
        self._state = load_game_state(self._level_index)
        self._steps = 0
        self._elapsed_ms = 0
        self._won = False
        self._selected_id = None
        self._powerup_activity = False
        self._removed_cars.clear()
        self._powerup_remain = 3
        self._move_anim = None

    def _time_star_limit_seconds(self, level_index: int) -> int:
        # Harder levels get a bit more time budget.
        level_seconds = [35, 45, 55, 70]
        if 0 <= level_index < len(level_seconds):
            return level_seconds[level_index]
        return 70

    def _is_new_best_steps(self) -> bool:
        best = self._best_steps_by_level.get(self._level_index)
        if best is None:
            return True
        return self._steps <= best

    def _get_win_stars(self) -> WinStars:
        total_seconds = self._elapsed_ms // 1000
        time_limit = self._time_star_limit_seconds(self._level_index)
        return WinStars(
            clear=self._won,
            time=total_seconds <= time_limit,
            best_steps=self._is_new_best_steps(),
        )

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
        if action == "powerup":
            if self._powerup_remain > 0:
                self._powerup_activity = True
                self._selected_id = None
            return
        if self._won:
            return

        if self._move_anim is not None:
            return

        cell = self._screen_pos_to_cell(pos)
        if cell is None:
            self._selected_id = None
            return
        row, col = cell
        v = self._state.occupant_at(row, col)

        if self._powerup_activity and v is not None and not v.is_target:
            self._removed_cars.add(v.id)
            self._powerup_activity = False
            self._powerup_remain -= 1
            return
        
        self._selected_id = v.id if v else None
        if v is not None:
            self._selected_id = v.id
            return

        if self._selected_id is not None:
            self._try_click_move_to_cell(row, col)

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

        # 找到选中的车
        selected = None
        for v in self._state.vehicles:
            if v.id == self._selected_id:
                selected = v
                break
        if not selected:
            return

        # 固定方向：横向车只能左右，纵向只能上下
        if selected.horizontal:
            dr = 0
        else:
            dc = 0

        # 计算移动后的所有格子
        next_cells = []
        if selected.horizontal:
            new_col = selected.col + dc
            for i in range(selected.length):
                next_cells.append((selected.row, new_col + i))
        else:
            new_row = selected.row + dr
            for i in range(selected.length):
                next_cells.append((new_row + i, selected.col))

   
        can_move = True
        for (r, c) in next_cells:
            # 1. 行永远不能出界（所有车都不能上下出棋盘）
            if r < 0 or r >= C.GRID_ROWS:
                can_move = False
                break

            # 2. 列边界判断
            if not selected.is_target:
                # 非目标车：左右都不能出棋盘
                if c < 0 or c >= C.GRID_COLS:
                    can_move = False
                    break
            else:
                # 目标小红车：只能向右驶出出口，不能向左出界，且必须在出口行
                if c < 0:
                    can_move = False
                    break
                # 只有在出口行，才允许向右驶出棋盘
                if r != C.EXIT_ROW and c >= C.GRID_COLS:
                    can_move = False
                    break
        if not can_move:
            return
    

        # 碰撞检查：忽略被PowerUp移除的车
        for (r, c) in next_cells:
            # 小红车驶出棋盘的部分，不用做碰撞检查
            if selected.is_target and c >= C.GRID_COLS:
                continue
            for v in self._state.vehicles:
                # 跳过自己 + 跳过被移除的车
                if v.id == selected.id or v.id in self._removed_cars:
                    continue
                if (r, c) in v.cells():
                    can_move = False
                    break
            if not can_move:
                break

        # 可以移动就执行移动
        if can_move:
            dist = dc if selected.horizontal else dr
            selected.move(dist)
            self._steps += 1
            # 移动后判断是否胜利
            if self._state.is_won():
                self._won = True

    def _update(self, dt: int) -> None:
        if self._move_anim is None:
            return

        anim = self._move_anim
        anim.elapsed_ms = min(anim.elapsed_ms + dt, anim.duration_ms)
        if anim.elapsed_ms >= anim.duration_ms:
            v = self._state.get_vehicle(anim.vehicle_id)
            if v is not None:
                v.move(anim.distance)
                self._steps += 1
                if self._state.is_won():
                    self._won = True
                    if self._is_new_best_steps():
                        self._best_steps_by_level[self._level_index] = self._steps
            self._move_anim = None

    def _try_click_move_to_cell(self, row: int, col: int) -> None:
        if self._selected_id is None:
            return
        v = self._state.get_vehicle(self._selected_id)
        if v is None:
            self._selected_id = None
            return

        if v.horizontal:
            if row != v.row:
                return
            left = v.col
            right = v.col + v.length - 1
            if col < left:
                self._start_move_animation(v.id, 0, -1, max_steps=left - col)
            elif col > right:
                self._start_move_animation(v.id, 0, 1, max_steps=col - right)
        else:
            if col != v.col:
                return
            top = v.row
            bottom = v.row + v.length - 1
            if row < top:
                self._start_move_animation(v.id, -1, 0, max_steps=top - row)
            elif row > bottom:
                self._start_move_animation(v.id, 1, 0, max_steps=row - bottom)

    def _start_move_animation(
        self, vehicle_id: str, dr: int, dc: int, max_steps: int | None = None
    ) -> None:
        if self._move_anim is not None:
            return
        steps = self._state.max_steps_in_direction(vehicle_id, dr, dc, max_steps)
        if steps <= 0:
            return
        signed_steps = steps * (dr + dc)
        distance_px = abs(signed_steps) * C.CELL_SIZE
        duration_ms = max(
            C.MOVE_MIN_DURATION_MS,
            int(1000 * distance_px / C.MOVE_SPEED_PX_PER_SEC),
        )
        self._move_anim = MoveAnimation(
            vehicle_id=vehicle_id,
            distance=signed_steps,
            elapsed_ms=0,
            duration_ms=duration_ms,
        )

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
        time_str = f"time: {minutes:02d}:{seconds:02d}"
        
        # Draw time (left)
        time_surf = self._font_ui.render(time_str, True, C.COLOR_TITLE)
        time_rect = time_surf.get_rect(
            bottomleft=(16, C.WINDOW_HEIGHT - 12)
        )
        self._screen.blit(time_surf, time_rect)

        # Draw steps (right)
        steps_surf = self._font_ui.render(f"step: {self._steps}", True, C.COLOR_TITLE)
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

    def _current_slide_offset(self, vehicle: Vehicle) -> tuple[float, float]:
        if self._move_anim is None or self._move_anim.vehicle_id != vehicle.id:
            return (0.0, 0.0)

        anim = self._move_anim
        # Smoothstep easing gives responsive start/end without stutter.
        t = anim.elapsed_ms / anim.duration_ms
        eased = t * t * (3.0 - 2.0 * t)
        delta = anim.distance * C.CELL_SIZE * eased
        if vehicle.horizontal:
            return (delta, 0.0)
        return (0.0, delta)

    def _vehicle_draw_rect(self, vehicle: Vehicle) -> pygame.Rect:
        cells = vehicle.cells()
        rects = [self._cell_rect_pixels(r, c) for r, c in cells]
        union = rects[0].copy()
        for r in rects[1:]:
            union.union_ip(r)
        body = union.inflate(-2 * C.VEHICLE_INSET, -2 * C.VEHICLE_INSET)
        dx, dy = self._current_slide_offset(vehicle)
        body.x += round(dx)
        body.y += round(dy)
        return body

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
            if v.id in self._removed_cars:
                continue

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
            if self._powerup_activity:
                if not v.is_target:
                    pygame.draw.rect(
                        self._screen,
                        C.COLOR_POWERUP_OUTLINE,
                        body,
                        width=10,
                        border_radius=10,
                    )
                    pygame.draw.rect(
                    self._screen,
                    (255,255,255), #白色内边
                    body.inflate(6,6),
                    width=2,
                    border_radius=10,
                    )
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
        step_surf = self._font_ui.render(f"step: {self._steps}", True, C.COLOR_WIN_TEXT)
        time_surf = self._font_ui.render(
            f"time: {minutes:02d}:{seconds:02d}", True, C.COLOR_WIN_TEXT
        )
        stars = self._get_win_stars()
        time_limit = self._time_star_limit_seconds(self._level_index)
        time_target_surf = self._font_ui.render(
            f"time target: <= {time_limit}s", True, C.COLOR_WIN_TEXT
        )
        best_steps = self._best_steps_by_level.get(self._level_index)
        best_steps_str = (
            f"best step: {best_steps}" if best_steps is not None else "best step: -"
        )
        best_steps_surf = self._font_ui.render(best_steps_str, True, C.COLOR_WIN_TEXT)
        score_surf = self._font_ui.render(
            f"score: {stars.total}/3 stars", True, C.COLOR_WIN_TEXT
        )

        last = self._level_index == level_count() - 1
        line1 = self._font_win.render("You Win!", True, C.COLOR_WIN_TEXT)
        panel_content_width = max(
            line1.get_width(),
            step_surf.get_width(),
            time_surf.get_width(),
            time_target_surf.get_width(),
            best_steps_surf.get_width(),
            score_surf.get_width(),
            240,
        )
        if last:
            line2 = self._font_ui.render(
                "All levels completed!", True, C.COLOR_WIN_TEXT
            )
            panel_w = max(panel_content_width, line2.get_width()) + 80
            panel_h = (
                line1.get_height()
                + 24
                + 40
                + 12
                + step_surf.get_height()
                + 6
                + time_surf.get_height()
                + 8
                + time_target_surf.get_height()
                + 8
                + best_steps_surf.get_height()
                + 8
                + score_surf.get_height()
                + 14
                + line2.get_height()
                + 28
            )
        else:
            line2 = None
            panel_w = panel_content_width + 80
            panel_h = (
                line1.get_height()
                + 24
                + 40
                + 12
                + step_surf.get_height()
                + 6
                + time_surf.get_height()
                + 8
                + time_target_surf.get_height()
                + 8
                + best_steps_surf.get_height()
                + 8
                + score_surf.get_height()
                + 28
            )

        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (C.WINDOW_WIDTH // 2, C.WINDOW_HEIGHT // 2)
        pygame.draw.rect(self._screen, C.COLOR_WIN_PANEL, panel, border_radius=12)
        pygame.draw.rect(
            self._screen, C.COLOR_EXIT_HIGHLIGHT, panel, width=3, border_radius=12
        )

        y = panel.top + 24
        r1 = line1.get_rect(centerx=panel.centerx, top=y)
        self._screen.blit(line1, r1)

        self._draw_star_row(
            center_x=panel.centerx,
            top=r1.bottom + 12,
            stars_on=(stars.clear, stars.time, stars.best_steps),
        )

        r_step = step_surf.get_rect(centerx=panel.centerx, top=r1.bottom + 64)
        self._screen.blit(step_surf, r_step)
        r_time = time_surf.get_rect(centerx=panel.centerx, top=r_step.bottom + 6)
        self._screen.blit(time_surf, r_time)
        r_time_target = time_target_surf.get_rect(
            centerx=panel.centerx, top=r_time.bottom + 8
        )
        self._screen.blit(time_target_surf, r_time_target)
        r_best = best_steps_surf.get_rect(centerx=panel.centerx, top=r_time_target.bottom + 8)
        self._screen.blit(best_steps_surf, r_best)
        r_score = score_surf.get_rect(centerx=panel.centerx, top=r_best.bottom + 8)
        self._screen.blit(score_surf, r_score)

        if line2 is not None:
            r2 = line2.get_rect(
                centerx=panel.centerx, top=r_score.bottom + 14,
            )
            self._screen.blit(line2, r2)

    def _draw_star_row(
        self, center_x: int, top: int, stars_on: tuple[bool, bool, bool]
    ) -> None:
        star_radius = 12
        spacing = 42
        start_x = center_x - spacing
        for idx, is_on in enumerate(stars_on):
            cx = start_x + idx * spacing
            self._draw_star(cx, top + 16, star_radius, is_on)

    def _draw_star(self, cx: int, cy: int, outer_radius: int, is_on: bool) -> None:
        inner_radius = max(outer_radius * 0.45, 1.0)
        points: list[tuple[int, int]] = []
        for i in range(10):
            angle = -pi / 2 + i * pi / 5
            radius = outer_radius if i % 2 == 0 else inner_radius
            points.append((round(cx + radius * cos(angle)), round(cy + radius * sin(angle))))

        if is_on:
            pygame.draw.polygon(self._screen, C.COLOR_STAR_ON, points)
            pygame.draw.polygon(self._screen, C.COLOR_EXIT_HIGHLIGHT, points, 2)
        else:
            pygame.draw.polygon(self._screen, C.COLOR_STAR_OFF_FILL, points)
            pygame.draw.polygon(self._screen, C.COLOR_STAR_OFF_BORDER, points, 2)

    def _draw(self) -> None:
        if self._state_name == "MENU":
            mouse = pygame.mouse.get_pos()
            self._menu.draw(self._screen, mouse)
            return

        self._screen.fill(C.COLOR_BG)
        self._draw_title()
        mouse = pygame.mouse.get_pos()
        self._control_bar.draw(
            self._screen,
            mouse,
            self._level_index,
            level_count(),
            self._powerup_remain
        )
        self._board.draw(self._screen, self._board_bg)
        self._draw_exit_portal()
        self._draw_vehicles()
        self._draw_hud()
        if self._won:
            self._draw_win_overlay()