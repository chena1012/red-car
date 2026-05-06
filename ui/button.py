"""Simple rectangular button: Pygame drawing and hit detection."""

from __future__ import annotations

import pygame

from game import constants as C


class Button:
    """Rounded rectangle button with centered text and hover effect.
    Handles rendering, color customization, and mouse collision detection.
    """

    def __init__(
        self,
        rect: pygame.Rect | tuple[int, int, int, int],
        label: str,
        font: pygame.font.Font,
        border_radius: int = C.BUTTON_RADIUS
    ) -> None:
        """Initialize a rectangular UI button.
        
        Args:
            rect: Button position and size (x, y, width, height)
            label: Text displayed on the button
            font: Font used for button text rendering
            border_radius: Radius for rounded button corners
        """
        self.rect = pygame.Rect(rect)
        self._label = label
        self._font = font
        # Default button color scheme from constants
        self.fill_color = C.COLOR_BUTTON_FILL
        self.hover_color = C.COLOR_BUTTON_FILL_HOVER
        self.border_color = C.COLOR_BUTTON_BORDER
        self.text_color = C.COLOR_BUTTON_TEXT
        self.border_radius = border_radius
        
    def set_colors(self, fill=None, hover=None, border=None, text=None):
        """Customize button colors with optional parameters.
        
        Args:
            fill: Background color for normal state
            hover: Background color for mouse hover state
            border: Border color of the button
            text: Text color of the button label
        """
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
        """Render the button on the target surface with hover effect.
        
        Args:
            surface: Pygame surface to draw the button on
            mouse_pos: Current mouse coordinates for hover detection
        """
        hovered = mouse_pos is not None and self.rect.collidepoint(mouse_pos)
        # Set background color based on hover state
        fill = self.hover_color if hovered else self.fill_color
        # Draw button background
        pygame.draw.rect(surface, fill, self.rect,
                         border_radius=self.border_radius)
        # Draw button border
        pygame.draw.rect(
            surface,
            self.border_color,
            self.rect,
            width=2,
            border_radius= self.border_radius,
        )
    
        # Render and center button text
        text = self._font.render(self._label, True, self.text_color)
        tr = text.get_rect(center=self.rect.center)
        surface.blit(text, tr)

    def contains(self, pos: tuple[int, int]) -> bool:
        """Check if the given position is inside the button area.
        
        Args:
            pos: Coordinates to check (x, y)
        Returns:
            True if position collides with the button
        """
        return self.rect.collidepoint(pos)


class CircleButton:
    """Circular button with centered text, hover effect, and completion badge.
    Supports image icons, custom colors, and level completion indicators.
    """

    def __init__(
        self,
        center: tuple[int, int],
        radius: int,
        label: str,
        font: pygame.font.Font,
    ) -> None:
        """Initialize a circular UI button.
        
        Args:
            center: Center coordinates of the circle (x, y)
            radius: Radius of the circular button
            label: Text displayed on the button
            font: Font used for button text rendering
        """
        self.center = center
        self.radius = radius
        self._label = label
        self._font = font
        # Default button color scheme
        self.fill_color = C.COLOR_BUTTON_FILL
        self.hover_color = C.COLOR_BUTTON_FILL_HOVER
        self.border_color = C.COLOR_BUTTON_BORDER
        self.text_color = C.COLOR_BUTTON_TEXT
        self.image: pygame.Surface | None = None

    def set_image(self, image: pygame.Surface | None) -> None:
        """Set an optional image icon for the button.
        
        Args:
            image: Pygame surface to display as button icon
        """
        self.image = image

    def set_colors(self, fill=None, hover=None, border=None, text=None):
        """Customize circular button colors with optional parameters.
        
        Args:
            fill: Background color for normal state
            hover: Background color for mouse hover state
            border: Border color of the button
            text: Text color of the button label
        """
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
        """Render the circular button with optional image and completion badge.
        
        Args:
            surface: Pygame surface to draw the button on
            mouse_pos: Current mouse coordinates for hover detection
            cleared: Flag to draw level completion checkmark badge
        """
        hovered = mouse_pos is not None and self.contains(mouse_pos)
        
        if self.image is not None:
            # Draw custom image centered on the button
            img_rect = self.image.get_rect(center=self.center)
            surface.blit(self.image, img_rect)
        else:
            # Default peach color scheme for text-based circular buttons
            fill = (250, 216, 140) if hovered else (250, 216, 140)
            border = (249, 207, 119)

            # Draw circular button background
            pygame.draw.circle(surface, fill, self.center, self.radius)
            # Draw circular button border
            pygame.draw.circle(surface, border, self.center, self.radius, width=2)
            
            # Render and center button text
            text_color = (207, 135, 70)
            text = self._font.render(self._label, True, text_color)
            tr = text.get_rect(center=self.center)
            surface.blit(text, tr)

        # Draw green completion badge with checkmark if level is cleared
        if cleared:
            badge_r = max(10, self.radius // 4)
            badge_center = (
                self.center[0] + int(self.radius * 0.65),
                self.center[1] - int(self.radius * 0.65),
            )
            # Green badge background
            pygame.draw.circle(surface, (80, 200, 120), badge_center, badge_r)
            # White badge border
            pygame.draw.circle(surface, (255, 255, 255), badge_center, badge_r, 2)
            
            # Draw custom checkmark (avoids font/encoding issues with special characters)
            v_size = badge_r * 0.6
            p1 = (badge_center[0] - v_size * 0.5, badge_center[1])
            p2 = (badge_center[0] - v_size * 0.1, badge_center[1] + v_size * 0.4)
            p3 = (badge_center[0] + v_size * 0.5, badge_center[1] - v_size * 0.4)
            pygame.draw.lines(surface, (255, 255, 255), False, [p1, p2, p3], 2)

    def contains(self, pos: tuple[int, int]) -> bool:
        """Check if the given position is inside the circular button using distance calculation.
        
        Args:
            pos: Coordinates to check (x, y)
        Returns:
            True if position is within the circle radius
        """
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return dx * dx + dy * dy <= self.radius * self.radius