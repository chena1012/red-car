"""Global constants: Window, Board, Exit, Colors, FPS, UI dimensions."""
import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
BOARD_BG_PATH = os.path.join(IMAGES_DIR, "board_bg.png")
MENU_BG_PATH = os.path.join(IMAGES_DIR, "menu_bg.png")
PLAY_BG_PATH = os.path.join(IMAGES_DIR, "play_bg.png")
INFO_BOX1_BG_PATH = os.path.join(IMAGES_DIR, "info_box1_bg.png")
INFO_BOX2_BG_PATH = os.path.join(IMAGES_DIR, "info_box2_bg.png")
BOARD_TILES_DIR = os.path.join(IMAGES_DIR, "board_tiles")
TARGET_BLOCK_IMAGE = "target_car.jpg"
BOARD_FRAME_PATH = os.path.join(IMAGES_DIR, "board_frame.png")
LEVEL_BG_PATH = os.path.join(IMAGES_DIR, "level_bg.png")
LEVEL_BUTTON_PATH = os.path.join(IMAGES_DIR, "level_button.png")
GAME_BG_PATH = os.path.join(IMAGES_DIR, "game_bg.png")
GAME_BUTTON_PATH = os.path.join(IMAGES_DIR, "game_button.png")
BONE_BUTTON_PATH = os.path.join(IMAGES_DIR, "bone_button.png")

# --- Board ---
CELL_SIZE = 90  # Cell size in pixels
GRID_ROWS = 6
GRID_COLS = 6
BOARD_FRAME_PADDING = 30

# --- Vehicle grass block ---
BLOCK_IMAGE_PADDING = 0
LONG_BLOCK_IMAGE_PADDING = 0

# Classic Rush Hour: Exit on the right side of the board, middle row (index 2)
EXIT_ROW = 2

# Exit portal width on the right
EXIT_PORTAL_WIDTH = 56

# --- Window Layout ---
BOARD_MARGIN = 24
BOTTOM_MARGIN = 24
RIGHT_PANEL_GAP = 32
RIGHT_PANEL_WIDTH = 300

# Title bar + control buttons height
TITLE_BAR_HEIGHT = 50
CONTROL_BAR_HEIGHT = 46
TOP_SECTION_HEIGHT = TITLE_BAR_HEIGHT + CONTROL_BAR_HEIGHT

BOARD_PIXEL_W = GRID_COLS * CELL_SIZE
BOARD_PIXEL_H = GRID_ROWS * CELL_SIZE

WINDOW_WIDTH = (
    BOARD_MARGIN
    + BOARD_PIXEL_W
    + EXIT_PORTAL_WIDTH
    + RIGHT_PANEL_GAP
    + RIGHT_PANEL_WIDTH
    + BOARD_MARGIN
)

WINDOW_HEIGHT = TOP_SECTION_HEIGHT + BOARD_PIXEL_H + BOTTOM_MARGIN

# --- Right Info Panel ---
RIGHT_PANEL_X = BOARD_MARGIN + BOARD_PIXEL_W + \
    EXIT_PORTAL_WIDTH + RIGHT_PANEL_GAP
RIGHT_PANEL_Y = TOP_SECTION_HEIGHT + 130

INFO_BOX_WIDTH = 220
INFO_BOX_HEIGHT = 100
INFO_BOX_GAP = 35

TIME_BOX_RECT = (
    RIGHT_PANEL_X,
    RIGHT_PANEL_Y,
    INFO_BOX_WIDTH,
    INFO_BOX_HEIGHT,
)

STEP_BOX_RECT = (
    RIGHT_PANEL_X,
    RIGHT_PANEL_Y + INFO_BOX_HEIGHT + INFO_BOX_GAP,
    INFO_BOX_WIDTH,
    INFO_BOX_HEIGHT,
)

FPS = 60

# --- Colors (R, G, B) ---
COLOR_BG = (40, 44, 52)
COLOR_BOARD = (67, 76, 94)
COLOR_GRID_LINE = (216, 222, 233)
COLOR_TITLE = (236, 239, 244)
COLOR_TITLE1 = (185, 217, 112)
COLOR_TITLE2 = (102, 121, 51)

COLOR_EXIT_PORTAL = (30, 35, 45)
COLOR_EXIT_HIGHLIGHT = (234, 179, 8)
COLOR_TARGET_OUTLINE = (250, 204, 21)
COLOR_SELECTION = (96, 165, 250)
COLOR_POWERUP = (255, 255, 0)

COLOR_WIN_OVERLAY = (15, 18, 24, 200)
COLOR_WIN_TEXT = (241, 245, 249)
COLOR_WIN_PANEL = (51, 65, 85)
COLOR_STAR_ON = (250, 204, 21)
COLOR_STAR_OFF_FILL = (71, 85, 105)
COLOR_STAR_OFF_BORDER = (148, 163, 184)

COLOR_INFO_BOX_TEXT = (241, 245, 249)
COLOR_INFO_BOX_LABEL = (203, 213, 225)

# Buttons
BUTTON_HEIGHT = 34
BUTTON_PAD_X = 14
BUTTON_RADIUS = 6
COLOR_BUTTON_FILL = (55, 65, 81)
COLOR_BUTTON_FILL_HOVER = (71, 85, 105)
COLOR_BUTTON_BORDER = (148, 163, 184)
COLOR_BUTTON_TEXT = (241, 245, 249)

MODE_NORMAL = "NORMAL"
MODE_LIMITED_TIME = "LIMITED_TIME"
MODE_LIMITED_STEP = "LIMITED_STEP"

CHALLENGE_BUTTON_WIDTH = 90
CHALLENGE_BUTTON_HEIGHT = 30
CHALLENGE_BUTTON_GAP = 8

# Vehicle inset from cell boundary
VEHICLE_INSET = 1

# Movement animation
MOVE_SPEED_PX_PER_SEC = 420
MOVE_MIN_DURATION_MS = 120

# --- Level Select Screen ---
LEVEL_BUTTON_SIZE = 140

LEVEL_BUTTON_POSITIONS = [
    (220, 440),  # Level 1
    (440, 245),  # Level 2
    (675, 420),  # Level 3
    (850, 250),  # Level 4
]

LEVEL_BACK_BUTTON_RECT = (388, 560, 200, 44)

# --- Audio ---
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

SFX_CLICK = os.path.join(SOUNDS_DIR, "click.wav")
SFX_SELECT = os.path.join(SOUNDS_DIR, "select.wav")
SFX_ERROR = os.path.join(SOUNDS_DIR, "error.wav")
SFX_UNDO = os.path.join(SOUNDS_DIR, "undo.wav")
SFX_MOVE = os.path.join(SOUNDS_DIR, "move.wav")
SFX_REMOVE = os.path.join(SOUNDS_DIR, "remove.wav")
SFX_WIN = os.path.join(SOUNDS_DIR, "win.wav")
SFX_FAIL = os.path.join(SOUNDS_DIR, "fail.wav")
BGM_PATH = os.path.join(SOUNDS_DIR, "bgm.mp3")

# --- Volume Control (全局统一调节) ---
VOLUME_MUSIC = 0.25    # 背景音乐总音量
VOLUME_SFX_MASTER = 0.7  # 所有音效总音量
VOLUME_CLICK = 1.0
VOLUME_SELECT = 0.9
VOLUME_MOVE = 0.8
VOLUME_WIN = 1.0
VOLUME_FAIL = 1.0
