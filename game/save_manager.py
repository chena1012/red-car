"""JSON save system: save/load current game state and unlocked progress."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import constants as C

# Version identifier for save file compatibility
SAVE_VERSION = 1


class SaveManager:
    """Manages game save/load operations using JSON format.
    Handles file I/O, version validation, and error handling for save data.
    """

    def __init__(self, save_path: Path | None = None) -> None:
        """Initialize save manager with custom or default save file path.
        
        Args:
            save_path: Custom path for save file; uses default if None
        """
        base_dir = Path(C.BASE_DIR)
        self._save_path = save_path or (base_dir / "savegame.json")

    @property
    def save_path(self) -> Path:
        """Get the path of the save file.
        
        Returns:
            Path object pointing to the save file
        """
        return self._save_path

    def save(self, payload: dict[str, Any]) -> tuple[bool, str]:
        """Write game data to JSON save file with version info.
        
        Args:
            payload: Dictionary containing all game state to save
        Returns:
            Tuple of (success boolean, status message)
        """
        data = {"version": SAVE_VERSION, **payload}
        try:
            # Create parent directories if they don't exist
            self._save_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_path.write_text(
                json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8"
            )
        except OSError:
            return False, "Save failed: cannot write save file."
        return True, "Saved successfully."

    def load(self) -> tuple[dict[str, Any] | None, str]:
        """Read and validate game data from JSON save file.
        
        Returns:
            Tuple of (save data dict or None, status message)
        """
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