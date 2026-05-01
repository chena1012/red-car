import pygame
import os
from game import constants as C


class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(32)

        # BGM 专用通道 0
        self._bgm_channel = pygame.mixer.Channel(0)
        self._bgm_sound = None

        if os.path.exists(C.BGM_PATH):
            self._bgm_sound = pygame.mixer.Sound(C.BGM_PATH)
            self._bgm_sound.set_volume(C.VOLUME_MUSIC)

        # 音效
        self.sfx_click = None
        self.sfx_select = None
        self.sfx_remove = None
        self.sfx_move = None
        self.sfx_win = None
        self.sfx_error = None
        self.sfx_undo = None
        self.sfx_fail = None
        self.load_all_sfx()

    def load_all_sfx(self):
        self.sfx_click = self._load_sound(C.SFX_CLICK, C.VOLUME_CLICK)
        self.sfx_select = self._load_sound(C.SFX_SELECT, C.VOLUME_SELECT)
        self.sfx_remove = self._load_sound(C.SFX_REMOVE, C.VOLUME_MOVE)
        self.sfx_move = self._load_sound(C.SFX_MOVE, C.VOLUME_MOVE)
        self.sfx_win = self._load_sound(C.SFX_WIN, C.VOLUME_WIN)
        self.sfx_error = self._load_sound(C.SFX_ERROR, C.VOLUME_CLICK) # 使用 click 的音量作为参考
        self.sfx_undo = self._load_sound(C.SFX_UNDO, C.VOLUME_CLICK)
        self.sfx_fail = self._load_sound(C.SFX_FAIL, C.VOLUME_FAIL)

    def _load_sound(self, path, vol):
        if not os.path.exists(path):
            return None
        snd = pygame.mixer.Sound(path)
        snd.set_volume(C.VOLUME_SFX_MASTER * vol)
        return snd

    # --------------------------
    # BGM 控制
    # --------------------------
    def play_bgm(self):
        if self._bgm_sound:
            self._bgm_channel.play(self._bgm_sound, loops=-1)

    def restart_bgm(self):
        if self._bgm_sound:
            self._bgm_channel.stop()
            self._bgm_channel.play(self._bgm_sound, loops=-1)

    # --------------------------
    # 音效：允许任意重叠
    # --------------------------
    def play_click(self):
        if self.sfx_click:
            self.sfx_click.play()

    def play_select(self):
        if self.sfx_select:
            self.sfx_select.play()

    def play_move(self):
        if self.sfx_move:
            self.sfx_move.play()

    def play_win(self):
        if self.sfx_win:
            self.sfx_win.play()

    def play_error(self):
        if self.sfx_error:
            self.sfx_error.play()

    def play_undo(self):
        if self.sfx_undo:
            self.sfx_undo.play()

    def play_remove(self):
        if self.sfx_remove:
            self.sfx_remove.play()

    def play_fail(self):
        if self.sfx_fail:
            self.sfx_fail.play()


audio = AudioManager()
