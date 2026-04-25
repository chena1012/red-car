"""Global constants: Window, Board, Exit, Colors, FPS, UI dimensions."""
import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
BOARD_BG_PATH = os.path.join(IMAGES_DIR, "board_bg.png")

# --- Board ---
CELL_SIZE = 90  # Cell size in pixels
GRID_ROWS = 6
GRID_COLS = 6

# Classic Rush Hour: Exit on the right side of the board, middle row (index 2)
EXIT_ROW = 2

# Exit portal width on the right
EXIT_PORTAL_WIDTH = 56

# --- Window Layout ---
BOARD_MARGIN = 24
BOTTOM_MARGIN = 24

# Title bar + control buttons height
TITLE_BAR_HEIGHT = 50
CONTROL_BAR_HEIGHT = 46
TOP_SECTION_HEIGHT = TITLE_BAR_HEIGHT + CONTROL_BAR_HEIGHT

BOARD_PIXEL_W = GRID_COLS * CELL_SIZE
BOARD_PIXEL_H = GRID_ROWS * CELL_SIZE

WINDOW_WIDTH = BOARD_MARGIN + BOARD_PIXEL_W + EXIT_PORTAL_WIDTH + BOARD_MARGIN
WINDOW_HEIGHT = TOP_SECTION_HEIGHT + BOARD_PIXEL_H + BOTTOM_MARGIN

FPS = 60

# --- Colors (R, G, B) ---
COLOR_BG = (40, 44, 52)
COLOR_BOARD = (67, 76, 94)
COLOR_GRID_LINE = (216, 222, 233)
COLOR_TITLE = (236, 239, 244)

COLOR_EXIT_PORTAL = (30, 35, 45)
COLOR_EXIT_HIGHLIGHT = (234, 179, 8)
COLOR_TARGET_OUTLINE = (250, 204, 21)
COLOR_SELECTION = (96, 165, 250)

COLOR_WIN_OVERLAY = (15, 18, 24, 200)
COLOR_WIN_TEXT = (241, 245, 249)
COLOR_WIN_PANEL = (51, 65, 85)
COLOR_STAR_ON = (250, 204, 21)
COLOR_STAR_OFF_FILL = (71, 85, 105)
COLOR_STAR_OFF_BORDER = (148, 163, 184)

# Buttons
BUTTON_HEIGHT = 34
BUTTON_PAD_X = 14
BUTTON_RADIUS = 6
COLOR_BUTTON_FILL = (55, 65, 81)
COLOR_BUTTON_FILL_HOVER = (71, 85, 105)
COLOR_BUTTON_BORDER = (148, 163, 184)
COLOR_BUTTON_TEXT = (241, 245, 249)

# Vehicle inset from cell boundary
VEHICLE_INSET = 6

# Movement animation
MOVE_SPEED_PX_PER_SEC = 420
MOVE_MIN_DURATION_MS = 120

# --- Audio ---
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

SFX_CLICK = os.path.join(SOUNDS_DIR, "click.wav")
SFX_SELECT = os.path.join(SOUNDS_DIR, "select.wav")
SFX_MOVE = os.path.join(SOUNDS_DIR, "move.wav")
SFX_WIN = os.path.join(SOUNDS_DIR, "win.wav")
BGM_PATH = os.path.join(SOUNDS_DIR, "bgm.mp3")

# --- Volume Control (全局统一调节) ---
VOLUME_MUSIC = 0.25    # 背景音乐总音量
VOLUME_SFX_MASTER = 0.7# 所有音效总音量
VOLUME_CLICK = 1.0
VOLUME_SELECT = 0.9
VOLUME_MOVE = 0.8
VOLUME_WIN = 1.0