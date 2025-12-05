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
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        
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
        
        self.ACTIVE__FLAG = False
        
        self.image = None
        self.render()
    
    def render(self):
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
        self.rect = self.image.get_rect(topleft=self.position)
    
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
        
        self.image = None
        self.render()
    
    def render(self):
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
        
        self.image = self.surface
        self.rect = self.image.get_rect(topleft=self.position)
    
    def update_text(self, new_text):
        self.text = new_text
        self.render()
