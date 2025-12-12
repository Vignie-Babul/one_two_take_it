import sys
import pygame

from .physic import PhysicsWorld
from .models import ObjectOrderedSet
from .bag_debris import create_bag_debris
from .platform import Platform


def render_fps_counter(master, clock, pos=(4, 4)) -> None:
    fps = round(clock.get_fps())
    font = pygame.font.SysFont('', 20)
    surface = font.render(f'FPS: {fps}', True, '#f2f2f2', None)
    master.blit(surface, pos)


class Game:
    def __init__(
        self,
        player,
        platform_group: pygame.sprite.Group,
        title: str = 'PyGame',
        size: tuple[int | float, int | float] = (1280, 720),
        bg: str = '#000000',
        fps: int = 60,
        show_fps: bool = True,
        gravity: tuple[int | float, int | float] = (0, -50),
        physics_ppm: int = 20,
        enable_boundaries: bool = True,
        boundary_color: str = '#ff0000',
    ) -> None:
        self.size = size
        self._bg = bg
        self._fps = fps
        self._show_fps = show_fps
        self._enable_boundaries = enable_boundaries
        self._boundary_color = boundary_color
        
        self._player = player
        self._platform_group = platform_group
        
        self._screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self._clock = pygame.time.Clock()
        self._is_game_loop = False
        self._is_game_over = False
        
        self.physics_world = PhysicsWorld(
            gravity=gravity,
            ppm=physics_ppm,
            screen_height=size[1]
        )
        
        self._boundary_group = pygame.sprite.Group()
        self._boundaries = []
        
        self._debris_particles = None
        self._debris_spawned = False
        
        if self._enable_boundaries:
            self._create_boundaries()

    def _create_boundaries(self) -> None:
        for boundary in self._boundaries:
            boundary.destroy()
        
        self._boundaries.clear()
        self._boundary_group.empty()
        
        boundary_thickness = 50
        
        left_boundary = Platform(
            physics_world=self.physics_world,
            position=(-boundary_thickness // 2, self.size[1] // 2),
            size=(boundary_thickness, self.size[1] + 200),
            color=self._boundary_color
        )
        self._boundary_group.add(left_boundary)
        self._boundaries.append(left_boundary)
        
        right_boundary = Platform(
            physics_world=self.physics_world,
            position=(self.size[0] + boundary_thickness // 2, self.size[1] // 2),
            size=(boundary_thickness, self.size[1] + 200),
            color=self._boundary_color
        )
        self._boundary_group.add(right_boundary)
        self._boundaries.append(right_boundary)
        
        top_boundary = Platform(
            physics_world=self.physics_world,
            position=(self.size[0] // 2, -boundary_thickness // 2),
            size=(self.size[0] + 200, boundary_thickness),
            color=self._boundary_color
        )
        self._boundary_group.add(top_boundary)
        self._boundaries.append(top_boundary)

    def _handle_resize(self, new_width: int, new_height: int) -> None:
        self.size = (new_width, new_height)
        self._screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.physics_world.screen_height = new_height
        
        if self._enable_boundaries:
            self._create_boundaries()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self._is_game_loop = False
                
                case pygame.KEYDOWN:
                    self._handle_key(event, True)
                
                case pygame.KEYUP:
                    self._handle_key(event, False)
                
                case pygame.VIDEORESIZE:
                    self._handle_resize(event.w, event.h)

    def _handle_key(self, event: pygame.event.Event, state: bool) -> None:
        match event.key:
            case pygame.K_ESCAPE:
                if state:
                    self._is_game_loop = False
            
            case pygame.K_LEFT | pygame.K_a:
                self._player.move_key('left', state)
            case pygame.K_RIGHT | pygame.K_d:
                self._player.move_key('right', state)
            case pygame.K_SPACE:
                self._player.move_key('jump_left', state)
            case pygame.K_UP:
                self._player.move_key('jump_right', state)
            case pygame.K_r:
                if state and self._is_game_over:
                    self._player.respawn()
                    self._is_game_over = False
                    self._debris_particles = None
                    self._debris_spawned = False
            case _:
                if hasattr(event, 'unicode'):
                    match event.unicode.lower():
                        case 'ф':
                            self._player.move_key('left', state)
                        case 'в':
                            self._player.move_key('right', state)
                        case 'к':
                            if state and self._is_game_over:
                                self._player.respawn()
                                self._is_game_over = False
                                self._debris_particles = None
                                self._debris_spawned = False

    def update(self) -> None:
        self.physics_world.step(1.0 / self._fps)
        
        if self._debris_particles is not None:
            self._debris_particles.update()
            if len(self._debris_particles) == 0:
                self._debris_particles = None
        
        if self._player.check_bounds(self.size[0], self.size[1]):
            self._is_game_over = True
        
        if self._player.is_game_over():
            self._is_game_over = True
            
            if self._player.should_spawn_debris() and not self._debris_spawned:
                bag_pos = self._player.get_bag_screen_position()
                bag_size = self._player.get_bag_size()
                left_vel, right_vel = self._player.get_parts_velocities()
                
                debris_list = create_bag_debris(bag_pos, bag_size, self.size, left_vel, right_vel)
                self._debris_particles = ObjectOrderedSet(*debris_list)
                self._debris_spawned = True
        
        self._player.update()
        self._platform_group.update()

    def render(self) -> None:
        self._screen.fill(self._bg)
        
        if self._enable_boundaries:
            self._boundary_group.draw(self._screen)
        
        self._platform_group.draw(self._screen)
        self._player.draw(self._screen)
        
        if self._debris_particles is not None:
            debris_sorted = sorted(self._debris_particles, key=lambda obj: obj.depth)
            for debris in debris_sorted:
                debris.draw(self._screen)
        
        if self._is_game_over:
            font = pygame.font.SysFont('', 48)
            text = font.render('GAME OVER - Press R to restart', True, '#ff0000')
            text_rect = text.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
            self._screen.blit(text, text_rect)
        
        if self._show_fps:
            render_fps_counter(self._screen, self._clock)
        
        pygame.display.flip()

    def quit(self) -> None:
        pygame.quit()
        sys.exit()

    def run(self) -> None:
        self._is_game_loop = True
        while self._is_game_loop:
            self.render()
            self.update()
            self.handle_events()
            self._clock.tick(self._fps)
        
        self.quit()
