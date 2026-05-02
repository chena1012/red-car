"""Main game class: loop, level index, input events, drawing and victory prompts."""

from __future__ import annotations
from game.audio import audio

import sys
import os
from dataclasses import dataclass
from math import cos, pi, sin

import pygame

from ui.hud import ControlBar
from ui.panels import LevelSelect, Menu, PausePanel
from ui.button import Button

from . import constants as C
from .board import Board
from .levels import level_count, load_game_state
from .save_manager import SaveManager
from .state import GameState
from .vehicle import Vehicle
from .hint import RushHourHint

audio.play_bgm()


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

audio.play_bgm()


@dataclass
class MoveAnimation:
    vehicle_id: str
    distance: int
    elapsed_ms: int
    duration_ms: int


@dataclass
class ShakeAnimation:
    vehicle_id: str
    dr: int
    dc: int
    elapsed_ms: int
    duration_ms: int


@dataclass
class UndoState:
    vehicles_data: list[dict]
    steps: int
    remaining_steps: int
    powerup_remain: int
    total_powerup_used: int
    total_removed_vehicles: int


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
        self.audio = None
        pygame.init()
        pygame.display.set_caption("Pup Rescue: lawn block")

        self._screen = pygame.display.set_mode(
            (C.WINDOW_WIDTH, C.WINDOW_HEIGHT))
        self._clock = pygame.time.Clock()

        self._board_x = C.BOARD_MARGIN
        self._board_y = C.TOP_SECTION_HEIGHT
        self._board = Board((self._board_x, self._board_y))

        self._level_index = 0
        self._state: GameState = load_game_state(self._level_index)

        self._selected_id: str | None = None
        self._powerup_active = False
        self._powerup_remain = 3
        self._steps = 0
        self._elapsed_ms = 0
        self._time_limit_ms = 0
        self._remaining_time_ms = 0
        self._step_limit = 0
        self._remaining_steps = 0
        self._won = False
        self._failed = False
        self._mode = C.MODE_NORMAL
        self._state_name = "MENU"  # "MENU" or "LEVEL_SELECT" or "PLAYING" or "PAUSED"
        self._move_anim: MoveAnimation | None = None
        self._best_steps_by_level: dict[int, int] = {}
        self._best_stars_by_level: dict[int, int] = {}
        self._unlocked_levels = 1
        self._status_text = ""
        self._status_ms_left = 0
        self._save_manager = SaveManager()
        self._total_powerup_used = 0
        self._total_removed_vehicles = 0
        self._challenge_clears: dict[str, bool] = {}
        self._shake_anim: ShakeAnimation | None = None
        self._undo_stack: list[UndoState] = []
        self._load_game_metadata()
        self._state_name = "MENU"

        self._font_title = pygame.font.Font(None, 50)
        self._font_title.set_bold(True)
        self._font_ui = pygame.font.Font(None, 18)
        self._status_font = pygame.font.Font(None, 40)
        self._status_font.set_bold(True)
        self._level_status_font = pygame.font.Font(None, 40)
        self._level_status_font.set_bold(True)
        self._font_btn = pygame.font.Font(None, 17)
        self._font_win = pygame.font.Font(None, 48)
        self._font_win.set_bold(True)
        self._font_menu_title = pygame.font.Font(None, 56)
        self._font_menu_title.set_bold(True)
        self._font_menu_btn = pygame.font.Font(None, 24)
        self._font_hud_label = pygame.font.Font(
            "C:/Windows/Fonts/consolab.ttf",
            24
        )
        self._font_hud_value = pygame.font.Font(
            "C:/Windows/Fonts/consolab.ttf", 36)

        self._control_bar = ControlBar(C.WINDOW_WIDTH, self._font_btn)
        self._menu = Menu(
            C.WINDOW_WIDTH, C.WINDOW_HEIGHT,
            self._font_menu_title, self._font_menu_btn
        )
        self._level_select = LevelSelect(
            C.WINDOW_WIDTH, C.WINDOW_HEIGHT, self._font_menu_title, self._font_menu_btn
        )
        self._pause_panel = PausePanel(
            C.WINDOW_WIDTH, C.WINDOW_HEIGHT, self._font_menu_title, self._font_menu_btn
        )
        self._result_buttons: dict[str, Button] = {}

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
        self._board_frame = pygame.image.load(C.BOARD_FRAME_PATH).convert_alpha()
        self._board_frame = pygame.transform.smoothscale(
            self._board_frame,
            (
                C.BOARD_PIXEL_W + C.BOARD_FRAME_PADDING * 2,
                C.BOARD_PIXEL_H + C.BOARD_FRAME_PADDING * 2,
            )
        )


        self._game_bg = pygame.image.load(C.GAME_BG_PATH).convert()
        self._game_bg = pygame.transform.smoothscale(
            self._game_bg,
            (C.WINDOW_WIDTH, C.WINDOW_HEIGHT)
        )
        self._info_box1_bg = pygame.image.load(
            C.INFO_BOX1_BG_PATH).convert_alpha()
        self._info_box1_bg = pygame.transform.smoothscale(
            self._info_box1_bg,
            (C.INFO_BOX_WIDTH, C.INFO_BOX_HEIGHT)
        )

        self._info_box2_bg = pygame.image.load(
            C.INFO_BOX2_BG_PATH).convert_alpha()
        self._info_box2_bg = pygame.transform.smoothscale(
            self._info_box2_bg,
            (C.INFO_BOX_WIDTH, C.INFO_BOX_HEIGHT)
        )

        self._block_image_files: dict[int, list[str]
                                      ] = self._load_block_image_files()
        self._block_image_cache: dict[tuple[int, bool,
                                            tuple[int, int], str], pygame.Surface] = {}

        audio.play_bgm()

    def run(self) -> None:
        running = True
        while running:
            dt = self._clock.tick(C.FPS)
            if self._state_name == "PLAYING" and not self._won and not self._failed:
                self._elapsed_ms += dt

            running = self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit(0)

    def _load_level(self, index: int, mode: str = C.MODE_NORMAL) -> None:
        """Switch to a level and reset steps, victory status and selection."""
        self._mode = mode
        self._failed = False
        audio.restart_bgm()  # 新关卡从头放BGM
        audio.load_all_sfx()
        n = level_count()
        max_level = max(min(self._unlocked_levels, n) - 1, 0)
        self._level_index = max(0, min(index, max_level))
        self._state = load_game_state(self._level_index)
        self._steps = 0
        self._elapsed_ms = 0
        self._won = False
        self._selected_id = None
        self._move_anim = None
        self._powerup_active = False
        self._powerup_remain = 3
        self._undo_stack.clear()
        self._initialize_mode_limits()

    def _reset_current_level(self) -> None:
        """Reset the current level layout."""
        audio.restart_bgm()  # 新关卡从头放BGM
        audio.load_all_sfx()
        self._state = load_game_state(self._level_index)
        self._steps = 0
        self._elapsed_ms = 0
        self._won = False
        self._failed = False
        self._selected_id = None
        self._move_anim = None
        self._powerup_active = False
        self._powerup_remain = 3
        self._result_buttons.clear()
        self._undo_stack.clear()
        self._initialize_mode_limits()

    def _set_status(self, text: str, duration_ms: int = 2200, color=C.COLOR_TITLE2) -> None:
        self._status_text = text
        self._status_ms_left = duration_ms
        self._status_color = color

    def _build_save_payload(self) -> dict:
        return {
            "level_index": self._level_index,
            "steps": self._steps,
            "elapsed_ms": self._elapsed_ms,
            "won": self._won,
            "failed": self._failed,
            "mode": self._mode,
            "time_limit_ms": self._time_limit_ms,
            "remaining_time_ms": self._remaining_time_ms,
            "step_limit": self._step_limit,
            "remaining_steps": self._remaining_steps,
            "unlocked_levels": self._unlocked_levels,
            "selected_id": self._selected_id,
            "powerup_remain": self._powerup_remain,
            "vehicles": self._state.export_vehicles(),
            "best_steps_by_level": {
                str(k): int(v) for k, v in self._best_steps_by_level.items()
            },
            "best_stars_by_level": {
                str(k): int(v) for k, v in self._best_stars_by_level.items()
            },
            "total_powerup_used": self._total_powerup_used,
            "total_removed_vehicles": self._total_removed_vehicles,
            "challenge_clears": dict(self._challenge_clears),
        }

    def _merge_challenge_clears_from_save(self) -> None:
        """从磁盘读取旧存档并合并 challenge_clears，确保通关记录不丢失。"""
        data, _ = self._save_manager.load()
        if not isinstance(data, dict):
            return

        raw = data.get("challenge_clears", {})
        if not isinstance(raw, dict):
            return

        for k, v in raw.items():
            if bool(v):
                self._challenge_clears[str(k)] = True

    def _save_game(self) -> bool:
        if self._move_anim is not None:
            self._set_status("Cannot save during animation.")
            return False

        # 保存前先从磁盘合并一次，防止多模式切换时内存数据覆盖了已有的磁盘记录
        self._merge_challenge_clears_from_save()

        ok, msg = self._save_manager.save(self._build_save_payload())
        self._set_status(msg)
        if ok:
            audio.play_click()
        return ok

    def _save_metadata_only_preserving_progress(self) -> bool:
        """保存全局进度（解锁关卡、最高分、挑战状态），但不覆盖已有的即时进度（如车辆位置等）。"""
        old_data, _ = self._save_manager.load()
        payload = old_data if isinstance(old_data, dict) else {}

        # 合并挑战通关状态
        old_challenge = payload.get("challenge_clears", {})
        merged_challenge = {}
        if isinstance(old_challenge, dict):
            for k, v in old_challenge.items():
                if bool(v):
                    merged_challenge[str(k)] = True

        # 合并内存中的最新记录
        for k, v in self._challenge_clears.items():
            if bool(v):
                merged_challenge[str(k)] = True

        # 更新全局元数据
        payload.update({
            "unlocked_levels": self._unlocked_levels,
            "best_steps_by_level": {
                str(k): int(v) for k, v in self._best_steps_by_level.items()
            },
            "best_stars_by_level": {
                str(k): int(v) for k, v in self._best_stars_by_level.items()
            },
            "total_powerup_used": self._total_powerup_used,
            "total_removed_vehicles": self._total_removed_vehicles,
            "challenge_clears": merged_challenge,
        })

        ok, _ = self._save_manager.save(payload)
        return ok

    def _save_without_progress(self) -> bool:
        """保存元数据并明确清除当前关卡的即时进度存档。"""
        payload = self._build_save_payload()
        payload["level_index"] = -1
        ok, _ = self._save_manager.save(payload)
        return ok

    def _load_game_metadata(self) -> None:
        """只加载全局元数据（如解锁进度、最高分），不加载具体关卡状态。"""
        data, msg = self._save_manager.load()
        if data is None:
            return

        n = level_count()
        self._unlocked_levels = max(
            1, min(int(data.get("unlocked_levels", 1)), n))

        # 加载最高分和星星
        raw_best = data.get("best_steps_by_level", {})
        if isinstance(raw_best, dict):
            for k, v in raw_best.items():
                ik, iv = int(k), int(v)
                if 0 <= ik < n and iv >= 0:
                    self._best_steps_by_level[ik] = iv

        raw_stars = data.get("best_stars_by_level", {})
        if isinstance(raw_stars, dict):
            for k, v in raw_stars.items():
                ik, iv = int(k), int(v)
                if 0 <= ik < n and 0 <= iv <= 3:
                    self._best_stars_by_level[ik] = iv

        self._total_powerup_used = int(data.get("total_powerup_used", 0))
        self._total_removed_vehicles = int(
            data.get("total_removed_vehicles", 0))

        # 加载挑战模式通关状态
        raw_challenge = data.get("challenge_clears", {})
        if isinstance(raw_challenge, dict):
            self._challenge_clears = {
                str(k): bool(v) for k, v in raw_challenge.items()
            }
        else:
            self._challenge_clears = {}

    def _load_game(self) -> None:
        if self._move_anim is not None:
            self._set_status("Cannot load during animation.")
            return
        data, msg = self._save_manager.load()
        if data is None:
            self._set_status(msg)
            return
        if not self._apply_save_data(data):
            self._set_status("Invalid save data. Restore failed.")
            return
        self._set_status("Loaded successfully.")
        audio.play_click()

    def _apply_save_data(self, data: dict) -> bool:
        n = level_count()
        try:
            unlocked = int(data.get("unlocked_levels", 1))
            unlocked = max(1, min(unlocked, n))
            level_idx = int(data["level_index"])
            if level_idx < 0 or level_idx >= unlocked:
                return False

            # 如果有车辆数据，使用它创建状态，否则加载关卡
            if "vehicles" in data:
                state = GameState([])
                if not state.apply_vehicles(list(data["vehicles"])):
                    return False
            else:
                state = load_game_state(level_idx)

            self._unlocked_levels = unlocked
            self._level_index = level_idx
            self._state = state
            self._steps = max(0, int(data.get("steps", 0)))
            self._elapsed_ms = max(0, int(data.get("elapsed_ms", 0)))
            self._won = bool(data.get("won", False))
            self._failed = bool(data.get("failed", False))

            # Mode handling with validation
            mode = str(data.get("mode", C.MODE_NORMAL))
            if mode not in (C.MODE_NORMAL, C.MODE_LIMITED_TIME, C.MODE_LIMITED_STEP):
                mode = C.MODE_NORMAL
            self._mode = mode

            self._powerup_remain = max(0, int(data.get("powerup_remain", 3)))

            # Limits restoration: prefer saved values if they exist
            if "time_limit_ms" in data:
                self._time_limit_ms = int(data["time_limit_ms"])
            if "remaining_time_ms" in data:
                self._remaining_time_ms = int(data["remaining_time_ms"])
            if "step_limit" in data:
                self._step_limit = int(data["step_limit"])
            if "remaining_steps" in data:
                self._remaining_steps = int(data["remaining_steps"])

            selected_id = data.get("selected_id")
            self._selected_id = selected_id if isinstance(
                selected_id, str) else None
            if self._selected_id is not None and self._state.get_vehicle(self._selected_id) is None:
                self._selected_id = None

            raw_best = data.get("best_steps_by_level", {})
            parsed_best: dict[int, int] = {}
            if isinstance(raw_best, dict):
                for k, v in raw_best.items():
                    ik = int(k)
                    iv = int(v)
                    if 0 <= ik < n and iv >= 0:
                        parsed_best[ik] = iv
            self._best_steps_by_level = parsed_best

            raw_stars = data.get("best_stars_by_level", {})
            parsed_stars: dict[int, int] = {}
            if isinstance(raw_stars, dict):
                for k, v in raw_stars.items():
                    ik = int(k)
                    iv = int(v)
                    if 0 <= ik < n and 0 <= iv <= 3:
                        parsed_stars[ik] = iv
            self._best_stars_by_level = parsed_stars

            # 加载全局统计和挑战进度
            self._total_powerup_used = int(
                data.get("total_powerup_used", self._total_powerup_used))
            self._total_removed_vehicles = int(
                data.get("total_removed_vehicles", self._total_removed_vehicles))
            raw_challenge = data.get("challenge_clears", {})
            if isinstance(raw_challenge, dict):
                self._challenge_clears = {
                    str(k): bool(v) for k, v in raw_challenge.items()
                }

            self._move_anim = None
            self._state_name = "PLAYING"
            return True
        except (KeyError, TypeError, ValueError):
            return False

    def _time_star_limit_seconds(self, level_index: int) -> int:
        # Harder levels get a bit more time budget.
        level_seconds = [35, 45, 55, 70]
        if 0 <= level_index < len(level_seconds):
            return level_seconds[level_index]
        return 70

    def _limited_time_seconds(self, level_index: int) -> int:
        limits = [30, 40, 50, 60]
        if 0 <= level_index < len(limits):
            return limits[level_index]
        return 60

    def _limited_step_count(self, level_index: int) -> int:
        limits = [18, 24, 30, 36]
        if 0 <= level_index < len(limits):
            return limits[level_index]
        return 36

    def _initialize_mode_limits(self) -> None:
        if self._mode == C.MODE_LIMITED_TIME:
            self._time_limit_ms = self._limited_time_seconds(
                self._level_index) * 1000
            self._remaining_time_ms = self._time_limit_ms
            self._step_limit = 0
            self._remaining_steps = 0
        elif self._mode == C.MODE_LIMITED_STEP:
            self._step_limit = self._limited_step_count(self._level_index)
            self._remaining_steps = self._step_limit
            self._time_limit_ms = 0
            self._remaining_time_ms = 0
        else:
            self._time_limit_ms = 0
            self._remaining_time_ms = 0
            self._step_limit = 0
            self._remaining_steps = 0

    def _challenge_time_limit_seconds(self, level_index: int) -> int:
        return self._limited_time_seconds(level_index)

    def _challenge_key(self, level_index: int, mode: str) -> str:
        return f"{level_index}:{mode}"

    def _mark_challenge_clear(self) -> None:
        if self._mode == C.MODE_NORMAL:
            return
        key = self._challenge_key(self._level_index, self._mode)
        self._challenge_clears[key] = True
        self._save_metadata_only_preserving_progress()

    def _challenge_step_limit(self, level_index: int) -> int:
        return self._limited_step_count(level_index)

    def _set_mode(self, mode: str) -> None:
        if mode not in (C.MODE_NORMAL, C.MODE_LIMITED_TIME, C.MODE_LIMITED_STEP):
            mode = C.MODE_NORMAL
        self._mode = mode
        self._failed = False
        self._initialize_mode_limits()

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

    def _check_challenge_limits(self) -> None:
        if self._state_name != "PLAYING" or self._won or self._failed or self._mode == C.MODE_NORMAL:
            return

        if self._mode == C.MODE_LIMITED_TIME:
            if self._remaining_time_ms <= 0:
                self._failed = True
                self._result_buttons.clear()
                self._set_status("Time Up! Press Reset to try again.")
                audio.play_fail()

        if self._mode == C.MODE_LIMITED_STEP:
            if self._remaining_steps <= 0 and not self._won:
                self._failed = True
                self._result_buttons.clear()
                self._set_status("No Steps Left! Press Reset to try again.")
                audio.play_fail()

    def _go_next_level(self) -> None:
        if self._level_index + 1 >= self._unlocked_levels:
            self._set_status("Next level is locked.")
            return
        self._load_level(self._level_index + 1)

    def _go_previous_level(self) -> None:
        if self._level_index - 1 < 0:
            self._set_status("Already at the first level.")
            return
        self._load_level(self._level_index - 1)

    def _result_go_previous_level(self) -> None:
        """从结果面板跳转到上一关，清理胜利/失败状态。"""
        self._won = False
        self._failed = False
        self._selected_id = None
        self._move_anim = None
        self._powerup_active = False
        self._go_previous_level()

    def _result_go_next_level(self) -> None:
        """从结果面板跳转到下一关，清理胜利/失败状态。"""
        self._won = False
        self._failed = False
        self._selected_id = None
        self._move_anim = None
        self._powerup_active = False
        self._go_next_level()

    def _try_restore_save_for(self, level_index: int, mode: str) -> None:
        """尝试从存档中恢复特定关卡和模式的即时进度。"""
        data, _ = self._save_manager.load()
        if not data:
            return

        try:
            saved_level = int(data.get("level_index", -1))
            saved_mode = str(data.get("mode", C.MODE_NORMAL))
        except (TypeError, ValueError):
            return

        if saved_level == level_index and saved_mode == mode:
            self._apply_save_data(data)

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._state_name == "MENU":
                    action = self._menu.action_at(event.pos)
                    if action == "start":
                        self._state_name = "LEVEL_SELECT"
                    elif action == "exit":
                        return False
                elif self._state_name == "LEVEL_SELECT":
                    action = self._level_select.action_at(
                        event.pos, self._unlocked_levels, self._best_stars_by_level)
                    if isinstance(action, tuple):
                        if action[0] == "level":
                            _, level_index = action
                            self._load_level(level_index, C.MODE_NORMAL)
                            self._try_restore_save_for(
                                level_index, C.MODE_NORMAL)
                        elif action[0] == "mode":
                            _, level_index, mode = action
                            self._load_level(level_index, mode)
                            self._try_restore_save_for(level_index, mode)
                        self._state_name = "PLAYING"
                    elif action == "back":
                        self._state_name = "MENU"
                    elif action == "locked":
                        self._set_status("This level is locked.")
                elif self._state_name == "PAUSED":
                    action = self._pause_panel.action_at(event.pos)
                    if action == "continue":
                        self._state_name = "PLAYING"
                    elif action == "save_exit":
                        if self._save_game():
                            self._state_name = "LEVEL_SELECT"
                            self._selected_id = None
                            self._move_anim = None
                    elif action == "exit_no_save":
                        self._state_name = "LEVEL_SELECT"
                        self._selected_id = None
                        self._move_anim = None
                        self._powerup_active = False
                elif self._state_name == "PLAYING":
                    self._on_mouse_down(event.pos)
            elif event.type == pygame.KEYDOWN:
                if self._state_name == "PLAYING":
                    if event.key == pygame.K_ESCAPE:
                        self._state_name = "PAUSED"
                        continue
                    self._on_key_down(event.key)
                elif self._state_name == "MENU" and event.key == pygame.K_RETURN:
                    self._state_name = "LEVEL_SELECT"
                elif self._state_name == "LEVEL_SELECT" and event.key == pygame.K_ESCAPE:
                    self._state_name = "MENU"
                elif self._state_name == "PAUSED" and event.key == pygame.K_ESCAPE:
                    self._state_name = "PLAYING"
        return True

    def _ensure_result_buttons(self) -> None:
        """Ensure result overlay buttons exist before handling click events."""
        if self._result_buttons:
            return

        if self._won:
            if self._mode == C.MODE_NORMAL:
                button_specs = [
                    ("prev", "Prev"),
                    ("reset", "Reset"),
                    ("next", "Next"),
                    ("exit", "Exit"),
                ]
            else:
                button_specs = [
                    ("reset", "Reset"),
                    ("exit", "Exit"),
                ]
        elif self._failed:
            button_specs = [
                ("reset", "Reset"),
                ("exit", "Exit"),
            ]
        else:
            return

        btn_w = 110
        btn_h = 40
        gap = 10
        total_btns_w = len(button_specs) * btn_w + (len(button_specs) - 1) * gap

        start_x = C.WINDOW_WIDTH // 2 - total_btns_w // 2
        y_btns = C.WINDOW_HEIGHT // 2 + 115

        for i, (key, label) in enumerate(button_specs):
            bx = start_x + i * (btn_w + gap)
            self._result_buttons[key] = Button(
                (bx, y_btns, btn_w, btn_h),
                label,
                self._font_btn,
            )

    def _on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self._won or self._failed:
            self._ensure_result_buttons()
            for key, btn in self._result_buttons.items():
                if btn.contains(pos):
                    audio.play_click()
                    if key == "reset":
                        self._reset_current_level()
                    elif key == "exit":
                        self._state_name = "LEVEL_SELECT"
                        self._selected_id = None
                        self._move_anim = None
                        self._won = False
                        self._failed = False
                        self._result_buttons.clear()
                    elif key == "prev":
                        self._result_go_previous_level()
                    elif key == "next":
                        self._result_go_next_level()
                    return
            # 胜利或失败状态下，如果没点中面板按钮，直接拦截所有点击
            return

        action = self._control_bar.action_at(pos)
        if action == "reset":
            self._reset_current_level()
            return
        if action == "undo":
            self._undo()
            return
        if action == "next":
            self._go_next_level()
            return
        if action == "prev":
            self._go_previous_level()
            return
        if action == "pause":
            if not self._won:
                self._state_name = "PAUSED"
            return
        if action == "powerup":
            if self._powerup_remain > 0:
                if self._powerup_active:
                    self._powerup_active = False
                    self._selected_id = None
                else:
                    self._powerup_active = True
                    self._selected_id = None
            return
        
        if action == "hint":
            hint = RushHourHint.get_hint(self._state)
            self._set_status(hint, duration_ms=3000)
            audio.play_click()

            # 自动高亮要移动的车
            if "Move " in hint:
                parts = hint.split()
                if len(parts) >= 3:
                    car_id = parts[1]
                    self._selected_id = car_id
            return

        if self._failed or self._won:
            return

        cell = self._screen_pos_to_cell(pos)
        if cell is None:
            self._selected_id = None
            return
        row, col = cell
        v = self._state.occupant_at(row, col)

        if self._won:
            return

        if self._move_anim is not None:
            return

        if self._powerup_active and v is not None and not v.is_target:
            self._push_undo() # 在移除车辆前记录状态
            self._state.remove_vehicle(v.id)
            self._powerup_active = False
            self._powerup_remain -= 1   # 消耗一次
            self._total_powerup_used += 1
            self._total_removed_vehicles += 1
            audio.play_remove()
            return

        if v is not None:
            self._selected_id = v.id
            audio.play_select()
            return

        if self._selected_id is not None:
            self._try_click_move_to_cell(row, col)

        self._selected_id = v.id if v else None

    def _on_key_down(self, key: int) -> None:
        if self._won or self._failed or self._selected_id is None or self._move_anim is not None:
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
        elif key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            self._undo()
            return
        else:
            return

        self._start_move_animation(self._selected_id, dr, dc, max_steps=1)

    def _update(self, dt: int) -> None:
        if self._status_ms_left > 0:
            self._status_ms_left = max(0, self._status_ms_left - dt)
            if self._status_ms_left == 0:
                self._status_text = ""

        if self._state_name == "PLAYING" and not self._won and not self._failed and self._mode == C.MODE_LIMITED_TIME:
            self._remaining_time_ms = max(0, self._remaining_time_ms - dt)

        self._check_challenge_limits()

        if self._shake_anim is not None:
            self._shake_anim.elapsed_ms += dt
            if self._shake_anim.elapsed_ms >= self._shake_anim.duration_ms:
                self._shake_anim = None

        if self._move_anim is None:
            return

        anim = self._move_anim
        anim.elapsed_ms = min(anim.elapsed_ms + dt, anim.duration_ms)
        if anim.elapsed_ms >= anim.duration_ms:
            v = self._state.get_vehicle(anim.vehicle_id)
            if v is not None:
                v.move(anim.distance)
                self._steps += 1
                if self._mode == C.MODE_LIMITED_STEP:
                    self._remaining_steps = max(0, self._remaining_steps - 1)
                audio.play_move()
            self._move_anim = None
            if self._state.is_won():
                self._won = True
                self._result_buttons.clear()
                audio.play_win()
                if self._mode == C.MODE_NORMAL:
                    if self._is_new_best_steps():
                        self._best_steps_by_level[self._level_index] = self._steps
                    stars_total = self._get_win_stars().total
                    prev = self._best_stars_by_level.get(self._level_index, 0)
                    self._best_stars_by_level[self._level_index] = max(
                        prev, stars_total)
                    self._unlocked_levels = min(
                        level_count(), max(self._unlocked_levels, self._level_index + 2)
                    )
                    self._save_without_progress()  # 胜利后保存元数据，不保留本关车辆位置
                else:
                    self._mark_challenge_clear()
                    self._set_status("Challenge completed!")

    def _try_click_move_to_cell(self, row: int, col: int) -> None:
        if self._selected_id is None:
            return
        v = self._state.get_vehicle(self._selected_id)
        if v is None:
            self._selected_id = None
            return

        dr, dc = 0, 0
        if v.horizontal:
            if row != v.row:
                self._show_invalid_move(v.id, 1 if row < v.row else -1, 0)
                return
            left = v.col
            right = v.col + v.length - 1
            if col < left:
                dr, dc = 0, -1
                max_steps = left - col
            elif col > right:
                dr, dc = 0, 1
                max_steps = col - right
            else:
                return
        else:
            if col != v.col:
                self._show_invalid_move(v.id, 0, 1 if col < v.col else -1)
                return
            top = v.row
            bottom = v.row + v.length - 1
            if row < top:
                dr, dc = -1, 0
                max_steps = top - row
            elif row > bottom:
                dr, dc = 1, 0
                max_steps = row - bottom
            else:
                return

        self._start_move_animation(v.id, dr, dc, max_steps=max_steps)

    def _start_move_animation(
        self, vehicle_id: str, dr: int, dc: int, max_steps: int | None = None
    ) -> None:
        if self._move_anim is not None:
            return
        if self._won or self._failed:
            return

        v = self._state.get_vehicle(vehicle_id)
        if v is None:
            return

        dr_orig, dc_orig = dr, dc

        # 方向锁定（完全正确）
        if v.horizontal:
            dr = 0  # 横向车：只能左右
            if dc_orig == 0 and dr_orig != 0: # 如果是横向车却尝试上下移动
                self._show_invalid_move(vehicle_id, dr_orig, dc_orig)
                return
            dr = 0
            dc = dc_orig
        else:
            if dc_orig != 0 or dr_orig not in (-1, 1):
                self._show_invalid_move(vehicle_id, dr_orig, dc_orig)
                return
            dr = dr_orig
            dc = 0

        moved = 0
        max_move = max_steps if max_steps is not None else 999

        for _ in range(max_move):
            next_r = v.row + dr * (moved + 1)
            next_c = v.col + dc * (moved + 1)
            safe = True

            # 先收集这辆车要移动到的所有格子
            cells = []
            for i in range(v.length):
                r = next_r + (0 if v.horizontal else i)
                c = next_c + (i if v.horizontal else 0)
                cells.append((r, c))

            # 检查边界
            for (r, c) in cells:
                if r < 0 or r >= C.GRID_ROWS:
                    safe = False
                if c < 0:
                    safe = False
                if c >= C.GRID_COLS and not (v.is_target and r == C.EXIT_ROW):
                    safe = False

            # 检查碰撞（独立检查！不会卡左移！）
            if safe:
                for other in self._state.vehicles:
                    if other.id == v.id:
                        continue
                    for (r, c) in cells:
                        if (r, c) in other.cells():
                            safe = False
                            break
                    if not safe:
                        break

            if safe:
                moved += 1
            else:
                break

        if moved <= 0:
            self._show_invalid_move(vehicle_id, dr, dc)
            return

        # 在执行合法移动前，记录撤销状态
        self._push_undo()

        steps = self._state.max_steps_in_direction(
            vehicle_id, dr, dc, max_steps)
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
            "Pup Rescue: lawn block", True, C.COLOR_TITLE2
        )
        text_rect = text_surf.get_rect(
            center=(C.WINDOW_WIDTH // 2, C.TITLE_BAR_HEIGHT // 2+20)
        )
        self._screen.blit(text_surf, text_rect)

    def _draw_hud(self) -> None:
        # 1. Prepare Time Info
        if self._mode == C.MODE_LIMITED_TIME:
            total_seconds = self._remaining_time_ms // 1000
            time_label = "Time Left"
        else:
            total_seconds = self._elapsed_ms // 1000
            time_label = "Time"

        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        # 2. Prepare Step Info
        if self._mode == C.MODE_LIMITED_STEP:
            step_label = "Steps Left"
            step_val_text = str(self._remaining_steps)
        else:
            step_label = "Step"
            step_val_text = str(self._steps)

        # 3. Draw Boxes
        time_rect = pygame.Rect(C.TIME_BOX_RECT)
        step_rect = pygame.Rect(C.STEP_BOX_RECT)

        # --- Draw Time Box ---
        self._screen.blit(self._info_box1_bg, time_rect.topleft)

        # Draw Label(s)
        time_label_surf = self._font_hud_label.render(
            time_label, True, C.COLOR_TITLE2
        )
        time_label_rect = time_label_surf.get_rect(
            center=(time_rect.centerx + 30, time_rect.y + 36)
        )
        self._screen.blit(time_label_surf, time_label_rect)

        # Draw Value
        time_val_surf = self._font_hud_value.render(
            time_str, True, C.COLOR_TITLE1)
        time_val_rect = time_val_surf.get_rect(
            center=(time_rect.centerx + 30, time_rect.y + 75))
        self._screen.blit(time_val_surf, time_val_rect)

        # --- Draw Step Box ---
        self._screen.blit(self._info_box2_bg, step_rect.topleft)

        # Draw Label(s)
        step_label_surf = self._font_hud_label.render(
            step_label, True, C.COLOR_TITLE2
        )
        step_label_rect = step_label_surf.get_rect(
            center=(step_rect.centerx + 25, step_rect.y + 36)
        )
        self._screen.blit(step_label_surf, step_label_rect)

        # Draw Value
        step_val_surf = self._font_hud_value.render(
            step_val_text, True, C.COLOR_TITLE1)
        step_val_rect = step_val_surf.get_rect(
            center=(step_rect.centerx + 25, step_rect.y + 75))
        self._screen.blit(step_val_surf, step_val_rect)

    def _show_invalid_move(self, vehicle_id: str | None = None, dr: int = 0, dc: int = 0) -> None:
        audio.play_error()
        if vehicle_id is not None and self._move_anim is None:
            self._shake_anim = ShakeAnimation(
                vehicle_id=vehicle_id,
                dr=dr,
                dc=dc,
                elapsed_ms=0,
                duration_ms=220,
            )

    def _push_undo(self) -> None:
        """记录当前状态到撤销栈。"""
        state = UndoState(
            vehicles_data=self._state.export_vehicles(),
            steps=self._steps,
            remaining_steps=self._remaining_steps,
            powerup_remain=self._powerup_remain,
            total_powerup_used=self._total_powerup_used,
            total_removed_vehicles=self._total_removed_vehicles
        )
        self._undo_stack.append(state)
        # 限制撤销步数，防止内存占用过大（可选，例如最近 50 步）
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

    def _undo(self) -> None:
        """执行撤销操作。"""
        if not self._undo_stack or self._move_anim is not None or self._won or self._failed:
            return

        state = self._undo_stack.pop()
        self._state.apply_vehicles(state.vehicles_data)
        self._steps = state.steps
        self._remaining_steps = state.remaining_steps
        self._powerup_remain = state.powerup_remain
        self._total_powerup_used = state.total_powerup_used
        self._total_removed_vehicles = state.total_removed_vehicles
        
        audio.play_undo()

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
        portal = pygame.Rect(portal_x, portal_y,
                             C.EXIT_PORTAL_WIDTH, C.CELL_SIZE)

        pygame.draw.rect(self._screen, C.COLOR_EXIT_PORTAL, portal)
        pygame.draw.rect(self._screen, C.COLOR_EXIT_HIGHLIGHT, portal, 4)

        cy = portal_y + C.CELL_SIZE // 2
        tip = (portal_x + C.EXIT_PORTAL_WIDTH - 6, cy)
        left = (portal_x + 10, cy - 14)
        right = (portal_x + 10, cy + 14)
        pygame.draw.polygon(
            self._screen, C.COLOR_EXIT_HIGHLIGHT, (tip, left, right))

    def _draw_board_frame(self) -> None:
        """Draw decorative frame around the 6x6 board."""
        frame_x = self._board_x - C.BOARD_FRAME_PADDING
        frame_y = self._board_y - C.BOARD_FRAME_PADDING

        self._screen.blit(
            self._board_frame,
            (frame_x, frame_y)
        )


    def _draw_vehicles(self) -> None:
        for v in self._state.vehicles:
            body = self._vehicle_draw_rect(v)

            # Apply shake offset if this vehicle is shaking
            if self._shake_anim is not None and self._shake_anim.vehicle_id == v.id:
                progress = self._shake_anim.elapsed_ms / self._shake_anim.duration_ms
                # sin(progress * pi * 3) gives a back-and-forth shake effect
                offset = sin(progress * pi * 3) * 8
                body.x += self._shake_anim.dc * offset
                body.y += self._shake_anim.dr * offset

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
            if self._powerup_active:
                # 小红车（目标车）不高亮，其他全部高亮
                if not v.is_target:
                    pygame.draw.rect(
                        self._screen,
                        C.COLOR_POWERUP,
                        body.inflate(10, 10),
                        width=5,
                        border_radius=10,
                    )

    def _load_block_image_files(self) -> dict[int, list[str]]:
        """Load grass block images from the board_tiles folder automatically."""
        files_by_length = {
            2: [],
            3: [],
        }

        if not os.path.isdir(C.BOARD_TILES_DIR):
            print(
                f"Warning: block image folder not found: {C.BOARD_TILES_DIR}")
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
        overlay = pygame.Surface((w, h-y0), pygame.SRCALPHA)
        overlay.fill(C.COLOR_WIN_OVERLAY)
        self._screen.blit(overlay, (0, y0))

        # Prepare stats text
        total_seconds = self._elapsed_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        is_normal = self._mode == C.MODE_NORMAL
        title_text = "YOU WIN!" if is_normal else "Challenge Completed!"
        line1 = self._font_win.render(title_text, True, C.COLOR_WIN_TEXT)

        # Content surfaces list
        content_surfs = [line1]

        step_surf = None
        if self._mode != C.MODE_LIMITED_TIME:
            step_surf = self._font_hud_label.render(
                f"step: {self._steps}", True, C.COLOR_WIN_TEXT)
            content_surfs.append(step_surf)

        time_surf = None
        if self._mode != C.MODE_LIMITED_STEP:
            time_surf = self._font_hud_label.render(
                f"time: {minutes:02d}:{seconds:02d}", True, C.COLOR_WIN_TEXT
            )
            content_surfs.append(time_surf)

        if is_normal:
            stars = self._get_win_stars()
            time_limit = self._time_star_limit_seconds(self._level_index)
            time_target_surf = self._font_ui.render(
                f"time target: <= {time_limit}s", True, C.COLOR_WIN_TEXT
            )
            best_steps = self._best_steps_by_level.get(self._level_index)
            best_steps_str = (
                f"best step: {best_steps}" if best_steps is not None else "best step: -"
            )
            best_steps_surf = self._font_ui.render(
                best_steps_str, True, C.COLOR_WIN_TEXT)
            score_surf = self._font_ui.render(
                f"score: {stars.total}/3 stars", True, C.COLOR_WIN_TEXT
            )
            content_surfs.extend(
                [time_target_surf, best_steps_surf, score_surf])

            last = self._level_index == level_count() - 1
            if last:
                line2 = self._font_ui.render(
                    "All levels completed!", True, C.COLOR_WIN_TEXT)
                content_surfs.append(line2)
            else:
                line2 = None
            
            button_specs = [
                ("prev", "Prev"),
                ("reset", "Reset"),
                ("next", "Next"),
                ("exit", "Exit"),
            ]
        else:
            stars = None
            line2 = None
            button_specs = [
                ("reset", "Reset"),
                ("exit", "Exit"),
            ]

        # Calculate layout
        btn_w = 110
        btn_h = 40
        gap = 10
        total_btns_w = len(button_specs) * btn_w + (len(button_specs) - 1) * gap
        
        panel_content_width = max([s.get_width() for s in content_surfs] + [total_btns_w, 240])
        panel_w = panel_content_width + 80

        # Calculate height based on content
        panel_h = 24 + line1.get_height() + 20  # Top part

        if is_normal:
            panel_h += 40 + 12  # Star row
            panel_h += step_surf.get_height() + 6 + time_surf.get_height() + 8
            panel_h += time_target_surf.get_height() + 8 + best_steps_surf.get_height() + \
                8 + score_surf.get_height() + 14
            if line2:
                panel_h += line2.get_height() + 14
        else:
            panel_h += 20  # Small gap
            step_h = step_surf.get_height() if step_surf else 0
            time_h = time_surf.get_height() if time_surf else 0
            panel_h += step_h + 10 + time_h + 20

        panel_h += btn_h + 30  # Buttons part

        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (C.WINDOW_WIDTH // 2, C.WINDOW_HEIGHT // 2)
        pygame.draw.rect(self._screen, C.COLOR_WIN_PANEL,
                         panel, border_radius=12)
        pygame.draw.rect(self._screen, (98,64,60),
                         panel, width=15, border_radius=12)

        y = panel.top + 24
        r1 = line1.get_rect(centerx=panel.centerx, top=y)
        self._screen.blit(line1, r1)
        y = r1.bottom + 12

        if is_normal:
            self._draw_star_row(
                center_x=panel.centerx,
                top=y,
                stars_on=(stars.clear, stars.time, stars.best_steps),
            )
            y += 52

            r_step = step_surf.get_rect(centerx=panel.centerx, top=y)
            self._screen.blit(step_surf, r_step)
            y = r_step.bottom + 6

            r_time = time_surf.get_rect(centerx=panel.centerx, top=y)
            self._screen.blit(time_surf, r_time)
            y = r_time.bottom + 8

            r_time_target = time_target_surf.get_rect(
                centerx=panel.centerx, top=y)
            self._screen.blit(time_target_surf, r_time_target)
            y = r_time_target.bottom + 8

            r_best = best_steps_surf.get_rect(centerx=panel.centerx, top=y)
            self._screen.blit(best_steps_surf, r_best)
            y = r_best.bottom + 8

            r_score = score_surf.get_rect(centerx=panel.centerx, top=y)
            self._screen.blit(score_surf, r_score)
            y = r_score.bottom + 14

            if line2:
                r2 = line2.get_rect(centerx=panel.centerx, top=y)
                self._screen.blit(line2, r2)
                y = r2.bottom + 14
        else:
            y += 10
            if step_surf:
                r_step = step_surf.get_rect(centerx=panel.centerx, top=y)
                self._screen.blit(step_surf, r_step)
                y = r_step.bottom + 10

            if time_surf:
                r_time = time_surf.get_rect(centerx=panel.centerx, top=y)
                self._screen.blit(time_surf, r_time)
                y = r_time.bottom + 20

        # Draw Buttons
        start_x = panel.centerx - total_btns_w // 2
        y_btns = C.WINDOW_HEIGHT // 2 + 115
        
        if not self._result_buttons:
            for i, (key, label) in enumerate(button_specs):
                bx = start_x + i * (btn_w + gap)
                self._result_buttons[key] = Button(
                    (bx, y_btns-30, btn_w, btn_h),
                    label,
                    self._font_btn
                )

                if key == "prev":
                    self._result_buttons[key].set_colors((20,160,60),(20,160,60),(40,23,20),(1,2,0))   # 红色
                elif key == "reset":
                    self._result_buttons[key].set_colors((245,206,83),(245,206,83),(40,23,20),(1,2,0))   # 绿色
                elif key == "next":
                    self._result_buttons[key].set_colors((240,117,46),(240,117,46),(40,23,20),(1,2,0))   # 蓝色
                elif key == "exit":
                    self._result_buttons[key].set_colors((200, 200, 200),(200, 200, 200),(40,23,20),(1,2,0))   # 灰色

        mouse = pygame.mouse.get_pos()
        for btn in self._result_buttons.values():
            btn.draw(self._screen, mouse)

    def _draw_fail_overlay(self) -> None:
        """Translucent layer for failure state."""

        w, h = self._screen.get_size()
        y0 = C.TOP_SECTION_HEIGHT
        overlay = pygame.Surface((w, h - y0), pygame.SRCALPHA)
        overlay.fill(C.COLOR_WIN_OVERLAY)
        self._screen.blit(overlay, (0, y0))

        # Title
        line1 = self._font_win.render("You Fail!", True, C.COLOR_WIN_TEXT)

        # Stats based on mode
        reason_str = ""
        stats_to_draw = []

        if self._mode == C.MODE_LIMITED_TIME:
            reason_str = "Reason: Time Up"
            stats_to_draw.append("time left: 00:00")
        elif self._mode == C.MODE_LIMITED_STEP:
            reason_str = "Reason: No Steps Left"
            stats_to_draw.append("steps left: 0")

        reason_surf = self._font_ui.render(reason_str, True, C.COLOR_WIN_TEXT)
        stat_surfs = [self._font_hud_label.render(
            s, True, C.COLOR_WIN_TEXT) for s in stats_to_draw]
        footer_surf = self._font_ui.render(
            "Press Reset to try again.", True, C.COLOR_WIN_TEXT)

        button_specs = [
            ("reset", "Reset"),
            ("exit", "Exit"),
        ]

        btn_w = 110
        btn_h = 40
        gap = 10
        total_btns_w = len(button_specs) * btn_w + (len(button_specs) - 1) * gap

        panel_content_width = max(
            [line1.get_width(), reason_surf.get_width(), footer_surf.get_width(), 240, total_btns_w] +
            [s.get_width() for s in stat_surfs]
        )

        panel_w = panel_content_width + 80
        
        stats_height = sum(s.get_height() for s in stat_surfs) + \
            (len(stat_surfs) - 1) * 6 if stat_surfs else 0

        panel_h = (
            line1.get_height()
            + 24  # top margin
            + 40  # star row space
            + 12  # gap
            + stats_height
            + (10 if stat_surfs else 0)  # gap after stats
            + reason_surf.get_height()
            + 10  # gap
            + footer_surf.get_height()
            + 20  # gap before buttons
            + btn_h  # buttons
            + 28  # bottom margin
        )

        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (C.WINDOW_WIDTH // 2, C.WINDOW_HEIGHT // 2)
        pygame.draw.rect(self._screen, C.COLOR_WIN_PANEL,
                         panel, border_radius=12)
        pygame.draw.rect(self._screen, C.COLOR_EXIT_HIGHLIGHT,
                         panel, width=3, border_radius=12)

        y = panel.top + 24
        r1 = line1.get_rect(centerx=panel.centerx, top=y)
        self._screen.blit(line1, r1)

        # Draw 0 stars
        self._draw_star_row(
            center_x=panel.centerx,
            top=r1.bottom + 12,
            stars_on=(False, False, False),
        )

        y = r1.bottom + 64
        for s in stat_surfs:
            r_stat = s.get_rect(centerx=panel.centerx, top=y)
            self._screen.blit(s, r_stat)
            y = r_stat.bottom + 6

        r_reason = reason_surf.get_rect(centerx=panel.centerx, top=y + 2)
        self._screen.blit(reason_surf, r_reason)

        r_footer = footer_surf.get_rect(
            centerx=panel.centerx, top=r_reason.bottom + 10)
        self._screen.blit(footer_surf, r_footer)

        # Draw Buttons
        start_x = panel.centerx - total_btns_w // 2
        y_btns = C.WINDOW_HEIGHT // 2 + 70
        
        if not self._result_buttons:
            for i, (key, label) in enumerate(button_specs):
                bx = start_x + i * (btn_w + gap)
                self._result_buttons[key] = Button(
                    (bx, y_btns, btn_w, btn_h),
                    label,
                    self._font_btn
                )
                if key == "exit":
                    self._result_buttons[key].set_colors((20,160,60),(20,160,60),(40,23,20),(1,2,0))   # 红色
                elif key == "reset":
                    self._result_buttons[key].set_colors((245,206,83),(245,206,83),(40,23,20),(1,2,0))  
                
        mouse = pygame.mouse.get_pos()
        for btn in self._result_buttons.values():
            btn.draw(self._screen, mouse)

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
            points.append((round(cx + radius * cos(angle)),
                          round(cy + radius * sin(angle))))

        if is_on:
            pygame.draw.polygon(self._screen, C.COLOR_STAR_ON, points)
            pygame.draw.polygon(
                self._screen, C.COLOR_EXIT_HIGHLIGHT, points, 2)
        else:
            pygame.draw.polygon(self._screen, C.COLOR_STAR_OFF_FILL, points)
            pygame.draw.polygon(
                self._screen, C.COLOR_STAR_OFF_BORDER, points, 2)

    def _draw(self) -> None:
        mouse = pygame.mouse.get_pos()

        # 当弹出暂停、胜利或失败面板时，背景按钮（控制栏等）应当不响应鼠标悬停
        bg_mouse = mouse
        if self._state_name == "PAUSED" or self._won or self._failed:
            bg_mouse = None

        if self._state_name == "MENU":
            self._screen.blit(self._menu_bg, (0, 0))
            self._menu.draw(self._screen, bg_mouse)
            return

        if self._state_name == "LEVEL_SELECT":
            self._level_select.draw(
                self._screen,
                bg_mouse,
                level_total=level_count(),
                unlocked_count=self._unlocked_levels,
                stars_by_level=self._best_stars_by_level,
                challenge_clears=self._challenge_clears,
            )
            return

        if self._state_name == "PLAYING" or self._state_name == "PAUSED":
            self._screen.blit(self._game_bg, (0, 0))
            self._board.draw(self._screen, self._board_bg)
            self._draw_exit_portal()
            self._draw_board_frame()
            self._draw_vehicles()
            self._draw_hud()
            self._draw_title()
            self._control_bar.draw(
                self._screen,
                bg_mouse,
                self._level_index,
                level_count(),
                self._powerup_remain
            )

        if self._state_name == "PAUSED":
            self._pause_panel.draw(self._screen, mouse)
            return

        if self._won:
            self._draw_win_overlay()
        elif self._failed:
            self._draw_fail_overlay()

        if self._status_text and self._status_ms_left > 0:
            surf = self._status_font.render(self._status_text, True, (0,0,0))
            rect = surf.get_rect(center=(C.WINDOW_WIDTH//2, C.WINDOW_HEIGHT - 40))
            self._screen.blit(surf, rect)
