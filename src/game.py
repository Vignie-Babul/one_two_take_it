from __future__ import annotations

import sys

import pygame

from .physic import PhysicsWorld
from .player import Player
from .platform import Platform

pygame.init()


def render_fps_counter(master, clock, pos=(4, 4)) -> None:
    fps = round(clock.get_fps())
    font = pygame.font.SysFont('', 20)
    surface = font.render(f'FPS: {fps}', True, '#f2f2f2', None)
    master.blit(surface, pos)


class Game:
    def __init__(
        self,
        player: Player,
        player_group: pygame.sprite.Group,
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
        self._player_group = player_group
        self._platform_group = platform_group

        self._screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self._clock = pygame.time.Clock()
        self._is_game_loop = False

        self.physics_world = PhysicsWorld(
            gravity=gravity,
            ppm=physics_ppm,
            screen_height=size[1]
        )

        self._boundary_group = pygame.sprite.Group()
        self._boundaries = []
        
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
        self.physics_world.screen_height = new_height
        
        if self._enable_boundaries:
            self._create_boundaries()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self._is_game_loop = False

                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            self._is_game_loop = False
                        
                        case pygame.K_LEFT | pygame.K_a:
                            self._player.move_key('left', True)
                        case pygame.K_RIGHT | pygame.K_d:
                            self._player.move_key('right', True)
                        case pygame.K_UP | pygame.K_w:
                            self._player.move_key('up', True)
                        case pygame.K_DOWN | pygame.K_s:
                            self._player.move_key('down', True)
                        case pygame.K_SPACE:
                            self._player.move_key('jump', True)

                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_LEFT | pygame.K_a:
                            self._player.move_key('left', False)
                        case pygame.K_RIGHT | pygame.K_d:
                            self._player.move_key('right', False)
                        case pygame.K_UP | pygame.K_w:
                            self._player.move_key('up', False)
                        case pygame.K_DOWN | pygame.K_s:
                            self._player.move_key('down', False)
                        case pygame.K_SPACE:
                            self._player.move_key('jump', False)

                case pygame.VIDEORESIZE:
                    self._handle_resize(event.w, event.h)

    def update(self) -> None:
        self.physics_world.step(1.0 / self._fps)

        if self._player.check_bounds(self.size[0], self.size[1]):
            self._player.respawn()

        self._player_group.update()
        self._platform_group.update()

    def render(self) -> None:
        self._screen.fill(self._bg)

        if self._enable_boundaries:
            self._boundary_group.draw(self._screen)
        
        self._platform_group.draw(self._screen)
        self._player_group.draw(self._screen)

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
