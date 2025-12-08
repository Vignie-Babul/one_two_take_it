from __future__ import annotations
import sys

import pygame

from .player import Player


pygame.init()


def render_fps_counter(master, clock, pos=(4, 4)) -> None:
	fps = round(clock.get_fps())
	font = pygame.font.SysFont('', 20)
	surface = font.render(f'FPS: {fps}', True, '#f2f2f2', None)
	master.blit(surface, pos)

	# TODO: fps lock for animations
	# if self.fps_lock and fps > self.fps:
	# 	fps = self.fps


class Game:
	def __init__(
		self,
		player: Player,
		player_group: pygame.sprite.Group,
		title: str = 'PyGame',
		size: tuple[int | float, int | float] = (1280, 720),
		bg: str = '#000000',
		fps: int = 60,
		show_fps: bool = True,
	) -> None:

		self.size = size
		self._bg = bg
		self._fps = fps
		self._show_fps = show_fps
		self._player = player
		self._player_group = player_group

		self._screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption(title)
		self._clock = pygame.time.Clock()

		self._is_game_loop = False

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

	def update(self) -> None:
		self._player_group.update(self.size)

	def render(self) -> None:
		self._screen.fill(self._bg)
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
