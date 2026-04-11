"""关卡数据：硬编码多关车辆的初始参数（不从文件读取）。"""

from __future__ import annotations

from .state import GameState
from .vehicle import Vehicle

# 每关：字典列表，键与 Vehicle.__init__ 一致，可直接 Vehicle(**d)
_LEVEL_SPECS: list[list[dict]] = [
    # 关卡 0：仅红车，用于演示布局与出口
    [
        {
            "id": "red",
            "row": 2,
            "col": 0,
            "length": 2,
            "horizontal": True,
            "color": (220, 38, 38),
            "is_target": True,
        },
    ],
    # 关卡 1：红车 + 一辆竖车挡路
    [
        {
            "id": "red",
            "row": 2,
            "col": 0,
            "length": 2,
            "horizontal": True,
            "color": (220, 38, 38),
            "is_target": True,
        },
        {
            "id": "v1",
            "row": 0,
            "col": 3,
            "length": 2,
            "horizontal": False,
            "color": (59, 130, 246),
            "is_target": False,
        },
    ],
    # 关卡 2：多一辆横向车，稍挤
    [
        {
            "id": "red",
            "row": 2,
            "col": 0,
            "length": 2,
            "horizontal": True,
            "color": (220, 38, 38),
            "is_target": True,
        },
        {
            "id": "v1",
            "row": 0,
            "col": 2,
            "length": 2,
            "horizontal": False,
            "color": (59, 130, 246),
            "is_target": False,
        },
        {
            "id": "h1",
            "row": 4,
            "col": 1,
            "length": 2,
            "horizontal": True,
            "color": (34, 197, 94),
            "is_target": False,
        },
    ],
    # 关卡 3：更长车辆 + 更多阻挡
    [
        {
            "id": "red",
            "row": 2,
            "col": 1,
            "length": 2,
            "horizontal": True,
            "color": (220, 38, 38),
            "is_target": True,
        },
        {
            "id": "v_long",
            "row": 0,
            "col": 0,
            "length": 3,
            "horizontal": False,
            "color": (99, 102, 241),
            "is_target": False,
        },
        {
            "id": "h1",
            "row": 3,
            "col": 3,
            "length": 2,
            "horizontal": True,
            "color": (34, 197, 94),
            "is_target": False,
        },
        {
            "id": "v2",
            "row": 4,
            "col": 5,
            "length": 2,
            "horizontal": False,
            "color": (244, 114, 182),
            "is_target": False,
        },
    ],
]


def level_count() -> int:
    return len(_LEVEL_SPECS)


def make_vehicles(level_index: int) -> list[Vehicle]:
    idx = level_index % level_count()
    return [Vehicle(**spec) for spec in _LEVEL_SPECS[idx]]


def load_game_state(level_index: int) -> GameState:
    return GameState(make_vehicles(level_index))
