import pygame


class UI(pygame.sprite.Sprite):
    DEFAULT_BACKGROUND_COLOR = '#050505'
    DEFAULT_TEXT_COLOR = '#f2f2f2'
    DEFAULT_BORDER_COLOR = '#f2f2f2'
    DEFAULT_FONT_NAME = None
    DEFAULT_FONT_SIZE = 20
    DEFAULT_ROUND = 14
    DEFAULT_BORDER_WIDTH = 2
    
    def __init__(self, position, size):
        super().__init__()
        self.position = position
        self.size = size
        
    def _create_surface(self):
        return pygame.Surface(
            self.size,
            pygame.SRCALPHA,
            32
        ).convert_alpha()


class Button(UI):
    def __init__(
        self,
        position,
        size,
        text='',
        command=None,
        background_color=None,
        text_color=None,
        round_=None,
        border_width=None,
        border_color=None,
        font_name=None,
        font_size=None
    ):
        super().__init__(position, size)
        
        self.text = text
        self.command = command
        
        self.background_color = background_color or self.DEFAULT_BACKGROUND_COLOR
        self.text_color = text_color or self.DEFAULT_TEXT_COLOR
        self.round_ = round_ if round_ is not None else self.DEFAULT_ROUND
        self.border_width = border_width if border_width is not None else self.DEFAULT_BORDER_WIDTH
        self.border_color = border_color or self.DEFAULT_BORDER_COLOR
        self.font_name = font_name or self.DEFAULT_FONT_NAME
        self.font_size = font_size or self.DEFAULT_FONT_SIZE
        
        self.surface = self._create_surface()
        
        pygame.draw.rect(
            self.surface,
            self.background_color,
            (0, 0, *self.size),
            0,
            self.round_
        )
        
        if self.border_width > 0:
            pygame.draw.rect(
                self.surface,
                self.border_color,
                (0, 0, *self.size),
                self.border_width,
                self.round_
            )
        
        if self.text:
            font = pygame.font.SysFont(self.font_name, self.font_size)
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
            self.surface.blit(text_surface, text_rect)
        
        self.image = self.surface
        self.rect = self.image.get_rect(center=self.position)
        
        self.ACTIVE__FLAG = False
    
    def update(self):
        if self.command is None:
            return
        
        is_collidepoint = self.rect.collidepoint(pygame.mouse.get_pos())
        
        if is_collidepoint:
            if pygame.mouse.get_pressed()[0] == 1:
                if not self.ACTIVE__FLAG:
                    self.ACTIVE__FLAG = True
                    self.command()
            elif pygame.mouse.get_pressed()[0] == 0 and self.ACTIVE__FLAG:
                self.ACTIVE__FLAG = False


class Text(UI):
    def __init__(
        self,
        position,
        text='',
        text_color=None,
        background_color=None,
        font_name=None,
        font_size=None,
        round_=None,
        border_width=None,
        border_color=None,
        padding=10
    ):
        self.text = text
        self.text_color = text_color or self.DEFAULT_TEXT_COLOR
        self.background_color = background_color
        self.font_name = font_name or self.DEFAULT_FONT_NAME
        self.font_size = font_size or self.DEFAULT_FONT_SIZE
        self.round_ = round_ if round_ is not None else 0
        self.border_width = border_width if border_width is not None else 0
        self.border_color = border_color or self.DEFAULT_BORDER_COLOR
        self.padding = padding
        
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_size = text_surface.get_size()
        
        size = (text_size[0] + padding * 2, text_size[1] + padding * 2)
        
        super().__init__(position, size)
        
        self.surface = self._create_surface()
        
        if self.background_color:
            pygame.draw.rect(
                self.surface,
                self.background_color,
                (0, 0, *self.size),
                0,
                self.round_
            )
        
        if self.border_width > 0:
            pygame.draw.rect(
                self.surface,
                self.border_color,
                (0, 0, *self.size),
                self.border_width,
                self.round_
            )
        
        text_rect = text_surface.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
        self.surface.blit(text_surface, text_rect)
        
        self.image = self.surface
        self.rect = self.image.get_rect(center=self.position)
    
    def update_text(self, new_text):
        self.text = new_text
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_size = text_surface.get_size()
        
        self.size = (text_size[0] + self.padding * 2, text_size[1] + self.padding * 2)
        self.surface = self._create_surface()
        
        if self.background_color:
            pygame.draw.rect(
                self.surface,
                self.background_color,
                (0, 0, *self.size),
                0,
                self.round_
            )
        
        if self.border_width > 0:
            pygame.draw.rect(
                self.surface,
                self.border_color,
                (0, 0, *self.size),
                self.border_width,
                self.round_
            )
        
        text_rect = text_surface.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
        self.surface.blit(text_surface, text_rect)
        
        old_center = self.rect.center
        self.image = self.surface
        self.rect = self.image.get_rect(center=old_center)


class Container:
    def __init__(self, parent=None, screen_size=None):
        self.parent = parent
        self.screen_size = screen_size
        self.children = pygame.sprite.Group()
        self.rect = None
        
    def add(self, *sprites):
        self.children.add(*sprites)
        
    def _get_parent_rect(self):
        if self.parent:
            return self.parent.rect
        elif self.screen_size:
            return pygame.Rect(0, 0, self.screen_size[0], self.screen_size[1])
        else:
            return pygame.Rect(0, 0, 1280, 720)
    
    def _calculate_bounds(self):
        if len(self.children) == 0:
            return pygame.Rect(0, 0, 0, 0)
        
        min_x = min(sprite.rect.left for sprite in self.children)
        min_y = min(sprite.rect.top for sprite in self.children)
        max_x = max(sprite.rect.right for sprite in self.children)
        max_y = max(sprite.rect.bottom for sprite in self.children)
        
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    
    def align(self, anchor='center', offset=(0, 0)):
        if len(self.children) == 0:
            return
        
        parent_rect = self._get_parent_rect()
        current_bounds = self._calculate_bounds()
        
        if anchor == 'center':
            target_x = parent_rect.centerx
            target_y = parent_rect.centery
            current_center_x = current_bounds.centerx
            current_center_y = current_bounds.centery
            dx = target_x - current_center_x + offset[0]
            dy = target_y - current_center_y + offset[1]
        elif anchor == 'topleft':
            dx = parent_rect.left - current_bounds.left + offset[0]
            dy = parent_rect.top - current_bounds.top + offset[1]
        elif anchor == 'topright':
            dx = parent_rect.right - current_bounds.right + offset[0]
            dy = parent_rect.top - current_bounds.top + offset[1]
        elif anchor == 'bottomleft':
            dx = parent_rect.left - current_bounds.left + offset[0]
            dy = parent_rect.bottom - current_bounds.bottom + offset[1]
        elif anchor == 'bottomright':
            dx = parent_rect.right - current_bounds.right + offset[0]
            dy = parent_rect.bottom - current_bounds.bottom + offset[1]
        elif anchor == 'top':
            target_x = parent_rect.centerx
            dx = target_x - current_bounds.centerx + offset[0]
            dy = parent_rect.top - current_bounds.top + offset[1]
        elif anchor == 'bottom':
            target_x = parent_rect.centerx
            dx = target_x - current_bounds.centerx + offset[0]
            dy = parent_rect.bottom - current_bounds.bottom + offset[1]
        elif anchor == 'left':
            target_y = parent_rect.centery
            dx = parent_rect.left - current_bounds.left + offset[0]
            dy = target_y - current_bounds.centery + offset[1]
        elif anchor == 'right':
            target_y = parent_rect.centery
            dx = parent_rect.right - current_bounds.right + offset[0]
            dy = target_y - current_bounds.centery + offset[1]
        else:
            dx, dy = 0, 0
        
        for sprite in self.children:
            sprite.rect.x += dx
            sprite.rect.y += dy
        
        self.rect = self._calculate_bounds()
    
    def draw(self, screen):
        self.children.draw(screen)
    
    def update(self):
        self.children.update()


class Row(Container):
    def __init__(self, elements, gap=10, parent=None, screen_size=None):
        super().__init__(parent, screen_size)
        
        current_x = 0
        for element in elements:
            element.rect.left = current_x
            element.rect.centery = 0
            current_x += element.rect.width + gap
            self.add(element)
        
        self.rect = self._calculate_bounds()


class Grid(Container):
    def __init__(self, elements, columns, gap_x=10, gap_y=10, parent=None, screen_size=None):
        super().__init__(parent, screen_size)
        
        rows = []
        for i in range(0, len(elements), columns):
            row_elements = elements[i:i+columns]
            rows.append(row_elements)
        
        current_y = 0
        for row in rows:
            current_x = 0
            max_height = 0
            for element in row:
                element.rect.left = current_x
                element.rect.top = current_y
                current_x += element.rect.width + gap_x
                max_height = max(max_height, element.rect.height)
                self.add(element)
            current_y += max_height + gap_y
        
        self.rect = self._calculate_bounds()


class Column(Container):
    def __init__(self, elements, gap=10, parent=None, screen_size=None):
        super().__init__(parent, screen_size)
        
        current_y = 0
        for element in elements:
            element.rect.top = current_y
            element.rect.centerx = 0
            current_y += element.rect.height + gap
            self.add(element)
        
        self.rect = self._calculate_bounds()


class Group(Container):
    def __init__(self, *containers, parent=None, screen_size=None):
        super().__init__(parent, screen_size)
        
        for container in containers:
            if isinstance(container, Container):
                self.children.add(*container.children)
            else:
                self.children.add(container)
        
        self.rect = self._calculate_bounds()
