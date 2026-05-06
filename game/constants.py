"""Global constants: Window, Board, Exit, Colors, FPS, UI dimensions."""
import os

# --- File System Paths ---
# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# Root folder for all game assets
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
# Image assets root directory
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
# Background image for the game board
BOARD_BG_PATH = os.path.join(IMAGES_DIR, "board_bg.png")
# Main menu background image
MENU_BG_PATH = os.path.join(IMAGES_DIR, "menu_bg.png")
# Game play scene background
PLAY_BG_PATH = os.path.join(IMAGES_DIR, "play_bg.png")
# Info panel background images
INFO_BOX1_BG_PATH = os.path.join(IMAGES_DIR, "info_box1_bg.png")
INFO_BOX2_BG_PATH = os.path.join(IMAGES_DIR, "info_box2_bg.png")
# Directory for board tile images
BOARD_TILES_DIR = os.path.join(IMAGES_DIR, "board_tiles")
# Target red car image
TARGET_BLOCK_IMAGE = "target_car.jpg"
# Decorative frame around the game board
BOARD_FRAME_PATH = os.path.join(IMAGES_DIR, "board_frame.png")
# Level selection screen background
LEVEL_BG_PATH = os.path.join(IMAGES_DIR, "level_bg.png")
# Level selection button image
LEVEL_BUTTON_PATH = os.path.join(IMAGES_DIR, "level_button.png")
# Main game UI background
GAME_BG_PATH = os.path.join(IMAGES_DIR, "game_bg.png")
# General game button image
GAME_BUTTON_PATH = os.path.join(IMAGES_DIR, "game_button.png")
# Bone-styled UI button image
BONE_BUTTON_PATH = os.path.join(IMAGES_DIR, "bone_button.png")

# --- Game Board Core Settings ---
# Pixel size of each grid cell on the board
CELL_SIZE = 90
# 6x6 standard Rush Hour grid dimensions
GRID_ROWS = 6
GRID_COLS = 6
# Padding space around the board frame
BOARD_FRAME_PADDING = 30

# --- Vehicle Block Image Padding ---
# Padding for standard vehicle block images
BLOCK_IMAGE_PADDING = 0
# Padding for long vehicle block images
LONG_BLOCK_IMAGE_PADDING = 0

# Classic Rush Hour: Exit on the right side of the board, middle row (index 2)
# Row index of the exit portal
EXIT_ROW = 2

# Pixel width of the exit portal on the right side
EXIT_PORTAL_WIDTH = 56

# --- Main Window Layout ---
# Margin space around the game board
BOARD_MARGIN = 24
# Bottom margin of the game window
BOTTOM_MARGIN = 24
# Spacing between board and right info panel
RIGHT_PANEL_GAP = 32
# Width of the right-side information panel
RIGHT_PANEL_WIDTH = 300

# Height of title bar and control button bar
TITLE_BAR_HEIGHT = 50
CONTROL_BAR_HEIGHT = 46
# Total height of top UI section
TOP_SECTION_HEIGHT = TITLE_BAR_HEIGHT + CONTROL_BAR_HEIGHT

# Total pixel width/height of the game board
BOARD_PIXEL_W = GRID_COLS * CELL_SIZE
BOARD_PIXEL_H = GRID_ROWS * CELL_SIZE

# Final calculated game window width
WINDOW_WIDTH = (
    BOARD_MARGIN
    + BOARD_PIXEL_W
    + EXIT_PORTAL_WIDTH
    + RIGHT_PANEL_GAP
    + RIGHT_PANEL_WIDTH
    + BOARD_MARGIN
)

# Final calculated game window height
WINDOW_HEIGHT = TOP_SECTION_HEIGHT + BOARD_PIXEL_H + BOTTOM_MARGIN

# --- Right Info Panel Positioning ---
# X coordinate of the right info panel
RIGHT_PANEL_X = BOARD_MARGIN + BOARD_PIXEL_W + \
    EXIT_PORTAL_WIDTH + RIGHT_PANEL_GAP
# Y coordinate of the right info panel
RIGHT_PANEL_Y = TOP_SECTION_HEIGHT + 130

# Dimensions for info display boxes
INFO_BOX_WIDTH = 220
INFO_BOX_HEIGHT = 100
INFO_BOX_GAP = 35

# Coordinates for time display box (x, y, width, height)
TIME_BOX_RECT = (
    RIGHT_PANEL_X,
    RIGHT_PANEL_Y,
    INFO_BOX_WIDTH,
    INFO_BOX_HEIGHT,
)

# Coordinates for step count display box (x, y, width, height)
STEP_BOX_RECT = (
    RIGHT_PANEL_X,
    RIGHT_PANEL_Y + INFO_BOX_HEIGHT + INFO_BOX_GAP,
    INFO_BOX_WIDTH,
    INFO_BOX_HEIGHT,
)

# Game rendering frame rate (frames per second)
FPS = 60

# --- UI Color Palette (RGB Values) ---
# Main window background color
COLOR_BG = (40, 44, 52)
# Game board base color
COLOR_BOARD = (67, 76, 94)
# Grid line color
COLOR_GRID_LINE = (216, 222, 233)
# Title text colors
COLOR_TITLE = (236, 239, 244)
COLOR_TITLE1 = (185, 217, 112)
COLOR_TITLE2 = (102, 121, 51)

# Exit portal colors
COLOR_EXIT_PORTAL = (30, 35, 45)
COLOR_EXIT_HIGHLIGHT = (226, 244, 205)
# Target car outline color
COLOR_TARGET_OUTLINE = (250, 204, 21)
# Selected vehicle highlight color
COLOR_SELECTION = (96, 165, 250)
# Remove highlight color
COLOR_REMOVE = (255, 255, 0)

# Win screen overlay and text colors
COLOR_WIN_OVERLAY = (20, 40, 20, 40)
COLOR_WIN_TEXT = (86, 105, 52)
COLOR_WIN_PANEL = (243,254,238)
# Star rating colors (on/off states)
COLOR_STAR_ON = (250, 204, 21)
COLOR_STAR_OFF_FILL = (71, 85, 105)
COLOR_STAR_OFF_BORDER = (148, 163, 184)

# Info panel text colors
COLOR_INFO_BOX_TEXT = (241, 245, 249)
COLOR_INFO_BOX_LABEL = (203, 213, 225)

# --- UI Button Styling ---
# Standard button dimensions and styling
BUTTON_HEIGHT = 34
BUTTON_PAD_X = 14
BUTTON_RADIUS = 6
# Button fill/border/text colors (normal/hover states)
COLOR_BUTTON_FILL = (55, 65, 81)
COLOR_BUTTON_FILL_HOVER = (71, 85, 105)
COLOR_BUTTON_BORDER = (148, 163, 184)
COLOR_BUTTON_TEXT = (241, 245, 249)

# --- Game Mode Identifiers ---
# Standard classic game mode
MODE_NORMAL = "NORMAL"
# Time-limited challenge mode
MODE_LIMITED_TIME = "LIMITED_TIME"
# Step-limited challenge mode
MODE_LIMITED_STEP = "LIMITED_STEP"

# Challenge mode button dimensions
CHALLENGE_BUTTON_WIDTH = 90
CHALLENGE_BUTTON_HEIGHT = 30
CHALLENGE_BUTTON_GAP = 8

# Inset for vehicle rendering inside grid cells
VEHICLE_INSET = 1

# --- Vehicle Movement Animation ---
# Movement speed in pixels per second
MOVE_SPEED_PX_PER_SEC = 420
# Minimum animation duration in milliseconds
MOVE_MIN_DURATION_MS = 120

# --- Level Select Screen UI ---
# Pixel size of level selection buttons
LEVEL_BUTTON_SIZE = 140

# Predefined positions for level buttons (x, y)
LEVEL_BUTTON_POSITIONS = [
    (220, 440),  # Level 1
    (440, 245),  # Level 2
    (675, 420),  # Level 3
    (850, 250),  # Level 4
]

# Coordinates for back button on level select screen
LEVEL_BACK_BUTTON_RECT = (388, 560, 200, 44)

# --- Audio Assets ---
# Directory for sound effect files
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# Sound effect file paths
SFX_CLICK = os.path.join(SOUNDS_DIR, "click.wav")
SFX_SELECT = os.path.join(SOUNDS_DIR, "select.wav")
SFX_ERROR = os.path.join(SOUNDS_DIR, "error.wav")
SFX_UNDO = os.path.join(SOUNDS_DIR, "undo.wav")
SFX_MOVE = os.path.join(SOUNDS_DIR, "move.wav")
SFX_REMOVE = os.path.join(SOUNDS_DIR, "remove.wav")
SFX_WIN = os.path.join(SOUNDS_DIR, "win.wav")
SFX_FAIL = os.path.join(SOUNDS_DIR, "fail.wav")
# Background music file path
BGM_PATH = os.path.join(SOUNDS_DIR, "bgm.mp3")

# --- Global Audio Volume Control (0.0 to 1.0) ---
# Background music master volume
VOLUME_MUSIC = 0.25
# All sound effects master volume
VOLUME_SFX_MASTER = 0.7
# Individual sound effect volumes
VOLUME_CLICK = 1.0
VOLUME_SELECT = 0.9
VOLUME_MOVE = 0.8
VOLUME_WIN = 1.0
VOLUME_FAIL = 1.0