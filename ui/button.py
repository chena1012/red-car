"""Simple rectangular button: Pygame drawing and hit detection."""

from __future__ import annotations

import pygame

from game import constants as C


class Button:
    """Rounded rectangle button with centered text and hover effect."""

    def __init__(
        self,
        rect: pygame.Rect | tuple[int, int, int, int],
        label: str,
        font: pygame.font.Font,
        border_radius: int = C.BUTTON_RADIUS
    ) -> None:
        self.rect = pygame.Rect(rect)
        self._label = label
        self._font = font
        self.fill_color = C.COLOR_BUTTON_FILL
        self.hover_color = C.COLOR_BUTTON_FILL_HOVER
        self.border_color = C.COLOR_BUTTON_BORDER
        self.text_color = C.COLOR_BUTTON_TEXT
        self.border_radius = border_radius
        
    def set_colors(self, fill=None, hover=None, border=None, text=None):
        if fill is not None:
            self.fill_color = fill
        if hover is not None:
            self.hover_color = hover
        if border is not None:
            self.border_color = border
        if text is not None:
            self.text_color = text

    def draw(
        self,
        surface: pygame.Surface,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        hovered = mouse_pos is not None and self.rect.collidepoint(mouse_pos)
        # fill = C.COLOR_BUTTON_FILL_HOVER if hovered else C.COLOR_BUTTON_FILL
        fill = self.hover_color if hovered else self.fill_color
        pygame.draw.rect(surface, fill, self.rect,
                         border_radius=self.border_radius)
        pygame.draw.rect(
            surface,
            # C.COLOR_BUTTON_BORDER
            self.border_color,
            self.rect,
            width=2,
            border_radius= self.border_radius,
        )
    
        text = self._font.render(self._label, True,
        # C.COLOR_BUTTON_TEXT
        self.text_color)
        tr = text.get_rect(center=self.rect.center)
        surface.blit(text, tr)

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class CircleButton:
    """Circular button with centered text and hover effect."""

    def __init__(
        self,
        center: tuple[int, int],
        radius: int,
        label: str,
        font: pygame.font.Font,
    ) -> None:
        self.center = center
        self.radius = radius
        self._label = label
        self._font = font
        self.fill_color = C.COLOR_BUTTON_FILL
        self.hover_color = C.COLOR_BUTTON_FILL_HOVER
        self.border_color = C.COLOR_BUTTON_BORDER
        self.text_color = C.COLOR_BUTTON_TEXT
        self.image: pygame.Surface | None = None

    def set_image(self, image: pygame.Surface | None) -> None:
        self.image = image

    def set_colors(self, fill=None, hover=None, border=None, text=None):
        if fill is not None:
            self.fill_color = fill
        if hover is not None:
            self.hover_color = hover
        if border is not None:
            self.border_color = border
        if text is not None:
            self.text_color = text

    def draw(
        self,
        surface: pygame.Surface,
        mouse_pos: tuple[int, int] | None = None,
        cleared: bool = False,
    ) -> None:
        hovered = mouse_pos is not None and self.contains(mouse_pos)
        
        if self.image is not None:
            # If image exists, draw image. Scale it to fit the circle if needed.
            img_rect = self.image.get_rect(center=self.center)
            surface.blit(self.image, img_rect)
        else:
            # Peach-pink color like the Start button
            fill = (250, 216, 140) if hovered else (250, 216, 140)
            border = (249, 207, 119)

            # Draw background circle
            pygame.draw.circle(surface, fill, self.center, self.radius)

            # Draw border circle
            pygame.draw.circle(surface, border, self.center, self.radius, width=2)
            # Draw text

            text_color = (207, 135, 70)
            text = self._font.render(self._label, True, text_color)
            tr = text.get_rect(center=self.center)
            surface.blit(text, tr)

        if cleared:
            badge_r = max(10, self.radius // 4)
            badge_center = (
                self.center[0] + int(self.radius * 0.65),
                self.center[1] - int(self.radius * 0.65),
            )
            # Green badge
            pygame.draw.circle(surface, (80, 200, 120), badge_center, badge_r)
            # White border
            pygame.draw.circle(surface, (255, 255, 255), badge_center, badge_r, 2)
            
            # Draw a simple white "V" shape instead of "✓" character to avoid encoding issues
            # Calculate points for the checkmark
            v_size = badge_r * 0.6
            p1 = (badge_center[0] - v_size * 0.5, badge_center[1])
            p2 = (badge_center[0] - v_size * 0.1, badge_center[1] + v_size * 0.4)
            p3 = (badge_center[0] + v_size * 0.5, badge_center[1] - v_size * 0.4)
            pygame.draw.lines(surface, (255, 255, 255), False, [p1, p2, p3], 2)

    def contains(self, pos: tuple[int, int]) -> bool:
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return dx * dx + dy * dy <= self.radius * self.radius
