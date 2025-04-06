import pygame
from typing import Tuple, Callable, List, Optional

class Button:
    """Button UI component for the chess application."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, on_click: Callable = None, bg_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.on_click = on_click
        self.hovered = False
        self.text_color = (255, 255, 255)  # White text
        self.bg_color = bg_color  # Custom background color
        
        # Load button images
        try:
            self.normal_img = pygame.image.load('gui/assets/buttons/normal.png')
            self.hover_img = pygame.image.load('gui/assets/buttons/hover.png')
            
            # Scale images to match button dimensions
            self.normal_img = pygame.transform.scale(self.normal_img, (width, height))
            self.hover_img = pygame.transform.scale(self.hover_img, (width, height))
            
            self.has_images = True
        except:
            self.has_images = False
    
    def draw(self, surface: pygame.Surface):
        """Draw the button."""
        if self.has_images:
            # Draw button with image
            img = self.hover_img if self.hovered else self.normal_img
            surface.blit(img, self.rect.topleft)
        else:
            # Draw button with rectangle
            if self.bg_color:
                # Use custom background color if provided
                button_color = self.bg_color
            else:
                # Default colors
                button_color = (80, 130, 170) if self.hovered else (60, 110, 150)
            
            pygame.draw.rect(surface, button_color, self.rect, 0, 3)  # Filled rectangle with rounded corners
            pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, 3)  # Border
        
        # Render text
        text_surf = pygame.font.SysFont('Arial', 20).render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event) -> bool:
        """
        Handle pygame events for the button.
        Returns True if the button was clicked.
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        
        return False


class Label:
    """Text label UI component."""
    
    def __init__(self, x: int, y: int, text: str, font_size: int = 20, 
                 color: Tuple[int, int, int] = (240, 240, 240)):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.color = color
        
        # Font
        self.font = pygame.font.SysFont('Arial', font_size)
        
        # Render text
        self.text_surf = self.font.render(text, True, color)
        self.text_rect = self.text_surf.get_rect(topleft=(x, y))
    
    def draw(self, screen: pygame.Surface):
        """Draw the label on the screen."""
        screen.blit(self.text_surf, self.text_rect)
    
    def set_text(self, text: str):
        """Update the label text."""
        self.text = text
        self.text_surf = self.font.render(text, True, self.color)
        self.text_rect = self.text_surf.get_rect(topleft=(self.x, self.y))


class Panel:
    """UI panel for grouping components."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 bg_color: Tuple[int, int, int] = (60, 60, 60)):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.components = []
        
        # Try to load panel background
        try:
            self.bg_img = pygame.image.load('gui/assets/backgrounds/panel.png')
            self.bg_img = pygame.transform.scale(self.bg_img, (width, height))
            self.use_image = True
        except:
            self.use_image = False
    
    def draw(self, screen: pygame.Surface):
        """Draw the panel and its components on the screen."""
        if self.use_image:
            screen.blit(self.bg_img, self.rect)
        else:
            pygame.draw.rect(screen, self.bg_color, self.rect)
            pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)  # Border
        
        # Draw all components
        for component in self.components:
            component.draw(screen)
    
    def add_component(self, component):
        """Add a UI component to the panel."""
        self.components.append(component)
    
    def handle_event(self, event) -> bool:
        """
        Handle pygame events for all components.
        Returns True if any component handled the event.
        """
        for component in self.components:
            if hasattr(component, 'handle_event'):
                if component.handle_event(event):
                    return True
        
        return False


class Dropdown:
    """Dropdown selection UI component."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 options: List[str], callback: Callable[[str], None]):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.callback = callback
        self.selected_index = 0
        self.expanded = False
        
        # Calculate dropdown expanded height
        self.item_height = height
        self.expanded_height = len(options) * self.item_height
        
        # Colors
        self.bg_color = (80, 80, 80)
        self.hover_color = (100, 100, 100)
        self.text_color = (240, 240, 240)
        self.border_color = (150, 150, 150)
        
        # Font
        self.font = pygame.font.SysFont('Arial', height // 2)
        
        # Hover state for each item
        self.hover_item = -1
    
    def draw(self, screen: pygame.Surface):
        """Draw the dropdown on the screen."""
        # Draw main dropdown box
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Draw selected option
        selected_text = self.options[self.selected_index]
        text_surf = self.font.render(selected_text, True, self.text_color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surf, text_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery - 5),
            (self.rect.right - 15, self.rect.centery + 5)
        ]
        pygame.draw.polygon(screen, self.text_color, arrow_points)
        
        # Draw expanded dropdown if open
        if self.expanded:
            for i, option in enumerate(self.options):
                item_rect = pygame.Rect(
                    self.rect.x, 
                    self.rect.y + self.item_height * (i + 1),
                    self.rect.width, 
                    self.item_height
                )
                
                # Draw background with hover effect
                if i == self.hover_item:
                    pygame.draw.rect(screen, self.hover_color, item_rect)
                else:
                    pygame.draw.rect(screen, self.bg_color, item_rect)
                
                # Draw border
                pygame.draw.rect(screen, self.border_color, item_rect, 1)
                
                # Draw option text
                text_surf = self.font.render(option, True, self.text_color)
                text_rect = text_surf.get_rect(midleft=(item_rect.x + 10, item_rect.centery))
                screen.blit(text_surf, text_rect)
    
    def handle_event(self, event) -> bool:
        """
        Handle pygame events for the dropdown.
        Returns True if the dropdown handled the event.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Toggle dropdown if main box is clicked
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True
            
            # Check if clicking on an expanded option
            if self.expanded:
                for i in range(len(self.options)):
                    item_rect = pygame.Rect(
                        self.rect.x, 
                        self.rect.y + self.item_height * (i + 1),
                        self.rect.width, 
                        self.item_height
                    )
                    if item_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.expanded = False
                        self.callback(self.options[i])
                        return True
                
                # Clicking outside closes the dropdown
                self.expanded = False
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.expanded:
            # Track which item is being hovered
            self.hover_item = -1
            for i in range(len(self.options)):
                item_rect = pygame.Rect(
                    self.rect.x, 
                    self.rect.y + self.item_height * (i + 1),
                    self.rect.width, 
                    self.item_height
                )
                if item_rect.collidepoint(event.pos):
                    self.hover_item = i
                    return True
        
        return False


class MessageBox:
    """Message box for displaying alerts and notifications."""
    
    def __init__(self, screen_width: int, screen_height: int, 
                 message: str, font_size: int = 24):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.message = message
        
        # Dimensions
        self.width = min(screen_width - 100, len(message) * font_size // 2)
        self.height = 150
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Colors
        self.bg_color = (60, 60, 60, 230)  # Semi-transparent background
        self.text_color = (240, 240, 240)
        self.border_color = (150, 150, 150)
        
        # Font
        self.font = pygame.font.SysFont('Arial', font_size)
        
        # Close button
        button_width = 100
        button_height = 40
        button_x = self.x + (self.width - button_width) // 2
        button_y = self.y + self.height - button_height - 20
        self.ok_button = Button(
            button_x, button_y, button_width, button_height, 
            "OK", self.close
        )
        
        # State
        self.visible = True
    
    def draw(self, screen: pygame.Surface):
        """Draw the message box on the screen."""
        if not self.visible:
            return
        
        # Create a surface with alpha for transparency
        box_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        box_surface.fill(self.bg_color)
        
        # Draw border
        pygame.draw.rect(box_surface, self.border_color, (0, 0, self.width, self.height), 2)
        
        # Draw message text - word wrapped
        words = self.message.split(' ')
        lines = []
        line = ""
        font_width, _ = self.font.size(' ')
        for word in words:
            word_width, _ = self.font.size(word)
            if line == "":
                line = word
            elif line != "" and font_width + self.font.size(line + ' ' + word)[0] <= self.width - 40:
                line += ' ' + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        
        # Render each line
        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, self.text_color)
            text_rect = text_surf.get_rect(
                topleft=(20, 20 + i * (self.font.get_height() + 5))
            )
            box_surface.blit(text_surf, text_rect)
        
        # Blit the surface to the screen
        screen.blit(box_surface, (self.x, self.y))
        
        # Draw button
        self.ok_button.draw(screen)
    
    def handle_event(self, event) -> bool:
        """
        Handle pygame events for the message box.
        Returns True if the message box handled the event.
        """
        if not self.visible:
            return False
        
        # If ESC key is pressed, close the message box
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        
        # Handle button events
        return self.ok_button.handle_event(event)
    
    def close(self):
        """Close the message box."""
        self.visible = False 