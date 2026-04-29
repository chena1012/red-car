"""JSON 存档管理：保存/读取当前局面与解锁进度。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import constants as C

SAVE_VERSION = 1


class SaveManager:
    def __init__(self, save_path: Path | None = None) -> None:
        base_dir = Path(C.BASE_DIR)
        self._save_path = save_path or (base_dir / "savegame.json")

    @property
    def save_path(self) -> Path:
        return self._save_path

    def save(self, payload: dict[str, Any]) -> tuple[bool, str]:
        data = {"version": SAVE_VERSION, **payload}
        try:
            self._save_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_path.write_text(
                json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8"
            )
        except OSError:
            return False, "Save failed: cannot write save file."
        return True, "Saved successfully."

    def load(self) -> tuple[dict[str, Any] | None, str]:
        if not self._save_path.exists():
            return None, "No save file found."
        try:
            raw = self._save_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError):
            return None, "Save file is corrupted or unreadable."
        if not isinstance(data, dict):
            return None, "Invalid save format."
        if int(data.get("version", -1)) != SAVE_VERSION:
            return None, "Incompatible save version."
        return data, "Loaded successfully."
