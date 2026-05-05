"""Audio management: BGM playback and sound effect control."""
import pygame
import os
from game import constants as C


class AudioManager:
    """Manages game audio including background music and sound effects.
    Handles audio initialization, loading, playback, and volume control.
    """
    def __init__(self):
        """Initialize audio system, mixer channels, BGM and sound effects."""
        # Initialize Pygame mixer module
        pygame.mixer.init()
        # Set 32 audio channels to support multiple simultaneous sound effects
        pygame.mixer.set_num_channels(32)

        # Assign dedicated channel 0 for background music
        self._bgm_channel = pygame.mixer.Channel(0)
        self._bgm_sound = None

        # Load and initialize background music if file exists
        if os.path.exists(C.BGM_PATH):
            self._bgm_sound = pygame.mixer.Sound(C.BGM_PATH)
            self._bgm_sound.set_volume(C.VOLUME_MUSIC)

        # Initialize sound effect variables
        self.sfx_click = None
        self.sfx_select = None
        self.sfx_remove = None
        self.sfx_move = None
        self.sfx_win = None
        self.sfx_error = None
        self.sfx_undo = None
        self.sfx_fail = None
        # Load all game sound effects
        self.load_all_sfx()

    def load_all_sfx(self):
        """Load all sound effect files with configured volumes."""
        self.sfx_click = self._load_sound(C.SFX_CLICK, C.VOLUME_CLICK)
        self.sfx_select = self._load_sound(C.SFX_SELECT, C.VOLUME_SELECT)
        self.sfx_remove = self._load_sound(C.SFX_REMOVE, C.VOLUME_MOVE)
        self.sfx_move = self._load_sound(C.SFX_MOVE, C.VOLUME_MOVE)
        self.sfx_win = self._load_sound(C.SFX_WIN, C.VOLUME_WIN)
        self.sfx_error = self._load_sound(C.SFX_ERROR, C.VOLUME_CLICK)
        self.sfx_undo = self._load_sound(C.SFX_UNDO, C.VOLUME_CLICK)
        self.sfx_fail = self._load_sound(C.SFX_FAIL, C.VOLUME_FAIL)

    def _load_sound(self, path, vol):
        """Load a single sound file with volume adjustment.
        
        Args:
            path: File path to the sound effect
            vol: Base volume for the sound effect
        Returns:
            Pygame Sound object if loaded successfully, None otherwise
        """
        if not os.path.exists(path):
            return None
        snd = pygame.mixer.Sound(path)
        # Apply master SFX volume multiplier
        snd.set_volume(C.VOLUME_SFX_MASTER * vol)
        return snd

    # --------------------------
    # Background Music Control
    # --------------------------
    def play_bgm(self):
        """Play background music on loop (if loaded)."""
        if self._bgm_sound:
            self._bgm_channel.play(self._bgm_sound, loops=-1)

    def restart_bgm(self):
        """Stop and restart background music from the beginning."""
        if self._bgm_sound:
            self._bgm_channel.stop()
            self._bgm_channel.play(self._bgm_sound, loops=-1)

    # --------------------------
    # Sound Effect Playback
    # All effects support overlapping playback
    # --------------------------
    def play_click(self):
        """Play button click sound effect."""
        if self.sfx_click:
            self.sfx_click.play()

    def play_select(self):
        """Play selection sound effect."""
        if self.sfx_select:
            self.sfx_select.play()

    def play_move(self):
        """Play vehicle movement sound effect."""
        if self.sfx_move:
            self.sfx_move.play()

    def play_win(self):
        """Play level win sound effect."""
        if self.sfx_win:
            self.sfx_win.play()

    def play_error(self):
        """Play error/invalid action sound effect."""
        if self.sfx_error:
            self.sfx_error.play()

    def play_undo(self):
        """Play undo move sound effect."""
        if self.sfx_undo:
            self.sfx_undo.play()

    def play_remove(self):
        """Play vehicle remove remove sound effect."""
        if self.sfx_remove:
            self.sfx_remove.play()

    def play_fail(self):
        """Play level fail sound effect."""
        if self.sfx_fail:
            self.sfx_fail.play()


# Global singleton instance of AudioManager for game-wide use
audio = AudioManager()