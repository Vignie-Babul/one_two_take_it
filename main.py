from src.templates.game import Game
from src.templates.ui import Button, Text, Row, Column
from src.templates.player import Player
import pygame


class PlayerGame(Game):
    def __init__(self):
        super().__init__(
            title='Player Demo',
            width=1280,
            height=720,
            target_fps=60,
            fps_lock=True,
            fullscreen=False,
            background='#1a1a1a',
            show_fps=True,
            fps_color='#00ff00',
            fps_position=(10, 10)
        )
        
        self.player_group = pygame.sprite.Group()
        
        self._create_player()
        self._create_ui_elements()
        
        self.keys_pressed = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }
    
    def _create_player(self):
        self.player = Player(
            position=(self.width // 2, self.height // 2),
            size=50,
            color='#00ff00',
            speed=5
        )
        self.player_group.add(self.player)
    
    def _create_ui_elements(self):
        title = Text(
            position=(0, 0),
            text='Player Movement Demo',
            text_color='#ffffff',
            background_color='#050505',
            font_size=32,
            round_=10,
            border_width=2,
            border_color='#00ff00',
            padding=15
        )
        
        info = Text(
            position=(0, 0),
            text='Use WASD or Arrow Keys to move',
            text_color='#f2f2f2',
            background_color='#2a2a2a',
            font_size=18,
            round_=8,
            border_width=1,
            border_color='#404040',
            padding=10
        )
        
        self.position_text = Text(
            position=(0, 0),
            text='Position: (0, 0)',
            text_color='#ffaa00',
            font_size=16,
            padding=5
        )
        
        color_buttons = []
        colors = [
            ('Green', '#00ff00'),
            ('Red', '#ff0000'),
            ('Blue', '#0000ff'),
            ('Yellow', '#ffff00'),
            ('Purple', '#ff00ff'),
            ('Cyan', '#00ffff')
        ]
        
        for name, color in colors:
            button = Button(
                position=(0, 0),
                size=(100, 40),
                text=name,
                command=lambda c=color: self.change_player_color(c),
                background_color=color,
                text_color='#000000' if color in ['#ffff00', '#00ffff'] else '#ffffff',
                border_width=2,
                border_color='#ffffff',
                round_=8,
                font_size=16
            )
            color_buttons.append(button)
        
        buttons_row = Row(color_buttons, gap=10, screen_size=(self.width, self.height))
        buttons_row.align('bottom', offset=(0, -20))
        
        ui_column = Column([title, info, self.position_text], gap=15, screen_size=(self.width, self.height))
        ui_column.align('top', offset=(0, 20))
        
        self.ui_group.add(title)
        self.ui_group.add(info)
        self.ui_group.add(self.position_text)
        self.ui_group.add(*color_buttons)
    
    def change_player_color(self, color):
        self.player.set_color(color)
    
    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.keys_pressed['left'] = True
            if event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.keys_pressed['right'] = True
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.keys_pressed['up'] = True
            if event.key in [pygame.K_DOWN, pygame.K_s]:
                self.keys_pressed['down'] = True
        
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.keys_pressed['left'] = False
            if event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.keys_pressed['right'] = False
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.keys_pressed['up'] = False
            if event.key in [pygame.K_DOWN, pygame.K_s]:
                self.keys_pressed['down'] = False
    
    def update(self):
        self.player.stop_horizontal()
        self.player.stop_vertical()
        
        if self.keys_pressed['left']:
            self.player.move('left')
        if self.keys_pressed['right']:
            self.player.move('right')
        if self.keys_pressed['up']:
            self.player.move('up')
        if self.keys_pressed['down']:
            self.player.move('down')
        
        self.player_group.update(self.width, self.height)
        
        self.position_text.update_text(f'Position: ({self.player.rect.centerx}, {self.player.rect.centery})')
    
    def render(self):
        if self.use_image_background and self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(self.background_color)
        
        self.player_group.draw(self.screen)
        
        self.ui_group.draw(self.screen)
        self.ui_group.update()
        
        self.render_fps_counter()


if __name__ == '__main__':
    game = PlayerGame()
    game.run()
