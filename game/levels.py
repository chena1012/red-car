"""Level data: hardcoded initial configurations for vehicles in each game level."""

from __future__ import annotations

from .state import GameState
from .vehicle import Vehicle

# Hardcoded level definitions: list of levels, each level is a list of vehicle config dicts
# Keys in each dict exactly match the parameters of Vehicle.__init__
_LEVEL_SPECS: list[list[dict]] = [
    # Level 1
    [
        {"id": "R", "row": 2, "col": 1, "length": 2, "horizontal": True,
            "color": (220, 50, 47), "is_target": True},
        {"id": "A", "row": 0, "col": 0, "length": 2, "horizontal": False,
            "color": (38, 139, 210), "is_target": False},
        {"id": "B", "row": 0, "col": 3, "length": 3, "horizontal": False,
            "color": (133, 153, 0), "is_target": False},
        {"id": "C", "row": 1, "col": 4, "length": 2, "horizontal": True,
            "color": (181, 137, 0), "is_target": False},
        {"id": "D", "row": 3, "col": 0, "length": 3, "horizontal": False,
            "color": (108, 113, 196), "is_target": False},
        {"id": "E", "row": 4, "col": 2, "length": 2, "horizontal": True,
            "color": (42, 161, 152), "is_target": False},
        {"id": "F", "row": 3, "col": 5, "length": 3, "horizontal": False,
            "color": (203, 75, 22), "is_target": False},
    ],
    # Level 2
    [
        {"id": "R", "row": 2, "col": 1, "length": 2, "horizontal": True,
            "color": (220, 50, 47), "is_target": True},
        {"id": "A", "row": 0, "col": 0, "length": 3, "horizontal": False,
            "color": (38, 139, 210), "is_target": False},
        {"id": "B", "row": 0, "col": 3, "length": 3, "horizontal": True,
            "color": (133, 153, 0), "is_target": False},
        {"id": "C", "row": 1, "col": 3, "length": 2, "horizontal": False,
            "color": (181, 137, 0), "is_target": False},
        {"id": "D", "row": 1, "col": 5, "length": 3, "horizontal": False,
            "color": (108, 113, 196), "is_target": False},
        {"id": "E", "row": 3, "col": 0, "length": 2, "horizontal": True,
            "color": (42, 161, 152), "is_target": False},
        {"id": "F", "row": 3, "col": 2, "length": 2, "horizontal": False,
            "color": (203, 75, 22), "is_target": False},
        {"id": "G", "row": 4, "col": 4, "length": 2, "horizontal": True,
            "color": (203, 75, 22), "is_target": False},
    ],
    # Level 3
    [
        {"id": "R", "row": 2, "col": 1, "length": 2, "horizontal": True,
            "color": (200, 50, 50), "is_target": True},
        {"id": "A", "row": 0, "col": 2, "length": 2, "horizontal": False,
            "color": (50, 100, 200), "is_target": False},
        {"id": "B", "row": 0, "col": 3, "length": 3, "horizontal": True,
            "color": (50, 180, 100), "is_target": False},
        {"id": "C", "row": 1, "col": 0, "length": 2, "horizontal": False,
            "color": (180, 150, 50), "is_target": False},
        {"id": "D", "row": 1, "col": 3, "length": 3, "horizontal": False,
            "color": (150, 80, 180), "is_target": False},
        {"id": "E", "row": 1, "col": 4, "length": 2, "horizontal": True,
            "color": (200, 120, 80), "is_target": False},
        {"id": "F", "row": 3, "col": 1, "length": 2, "horizontal": False,
            "color": (80, 160, 180), "is_target": False},
        {"id": "G", "row": 4, "col": 0, "length": 2, "horizontal": False,
            "color": (100, 100, 200), "is_target": False},
        {"id": "H", "row": 4, "col": 2, "length": 2, "horizontal": True,
            "color": (100, 100, 200), "is_target": False},
        {"id": "I", "row": 5, "col": 1, "length": 3, "horizontal": True,
            "color": (100, 100, 200), "is_target": False},
        {"id": "J", "row": 3, "col": 4, "length": 2, "horizontal": True,
            "color": (100, 100, 200), "is_target": False},
        {"id": "K", "row": 4, "col": 5, "length": 2, "horizontal": False,
            "color": (100, 100, 200), "is_target": False}
    ],
    # Level 4
    [
        {"id": "R", "row": 2, "col": 0, "length": 2, "horizontal": True,
            "color": (200, 50, 50), "is_target": True},
        {"id": "A", "row": 0, "col": 1, "length": 2, "horizontal": False,
            "color": (50, 100, 200), "is_target": False},
        {"id": "B", "row": 0, "col": 2, "length": 3, "horizontal": False,
            "color": (50, 180, 100), "is_target": False},
        {"id": "C", "row": 0, "col": 3, "length": 2, "horizontal": True,
            "color": (180, 150, 50), "is_target": False},
        {"id": "D", "row": 3, "col": 0, "length": 2, "horizontal": False,
            "color": (150, 80, 180), "is_target": False},
        {"id": "E", "row": 3, "col": 3, "length": 2, "horizontal": True,
            "color": (200, 120, 80), "is_target": False},
        {"id": "F", "row": 5, "col": 0, "length": 3, "horizontal": True,
            "color": (80, 160, 180), "is_target": False},
        {"id": "G", "row": 3, "col": 1, "length": 2, "horizontal": True,
            "color": (100, 100, 200), "is_target": False},
        {"id": "H", "row": 4, "col": 1, "length": 2, "horizontal": True,
            "color": (220, 100, 150), "is_target": False},
        {"id": "I", "row": 4, "col": 4, "length": 2, "horizontal": False,
            "color": (147, 161, 161), "is_target": False},
        {"id": "J", "row": 4, "col": 3, "length": 2, "horizontal": False,
            "color": (120, 120, 190), "is_target": False},
        {"id": "K", "row": 3, "col": 5, "length": 3, "horizontal": False,
            "color": (147, 161, 161), "is_target": False}
    ],
]


def level_count() -> int:
    """Get the total number of available game levels.
    
    Returns:
        Total count of hardcoded levels
    """
    return len(_LEVEL_SPECS)


def make_vehicles(level_index: int) -> list[Vehicle]:
    """Create a list of Vehicle objects for the specified level.
    
    Args:
        level_index: Index of the level to generate vehicles for
    Returns:
        List of initialized Vehicle instances for the level
    """
    idx = level_index % level_count()
    return [Vehicle(**spec) for spec in _LEVEL_SPECS[idx]]


def load_game_state(level_index: int) -> GameState:
    """Load the full initial GameState for the specified level.
    
    Args:
        level_index: Index of the level to load
    Returns:
        GameState object with all vehicles for the level
    """
    return GameState(make_vehicles(level_index))