"""简单矩形按钮：Pygame 绘制与点击区域检测。"""

from __future__ import annotations

import pygame

from game import constants as C


class Button:
    """统一圆角矩形 + 居中文字；可选根据鼠标位置显示悬停底色。"""

    def __init__(
        self,
        rect: pygame.Rect | tuple[int, int, int, int],
        label: str,
        font: pygame.font.Font,
    ) -> None:
        self.rect = pygame.Rect(rect)
        self._label = label
        self._font = font

    def draw(
        self,
        surface: pygame.Surface,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        hovered = mouse_pos is not None and self.rect.collidepoint(mouse_pos)
        fill = C.COLOR_BUTTON_FILL_HOVER if hovered else C.COLOR_BUTTON_FILL
        pygame.draw.rect(surface, fill, self.rect, border_radius=C.BUTTON_RADIUS)
        pygame.draw.rect(
            surface,
            C.COLOR_BUTTON_BORDER,
            self.rect,
            width=2,
            border_radius=C.BUTTON_RADIUS,
        )
        text = self._font.render(self._label, True, C.COLOR_BUTTON_TEXT)
        tr = text.get_rect(center=self.rect.center)
        surface.blit(text, tr)

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)
