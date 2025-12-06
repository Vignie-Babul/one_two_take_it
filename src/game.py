import sys

import pygame

# from .utils import is_file_valid


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
		title='PyGame',
		size=(1280, 720),
		bg='#000000',
		fps=60,
		show_fps=True,
	) -> None:

		self.size = size
		self._bg = bg
		self._fps = fps
		self._show_fps = show_fps

		self._screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption(title)
		self._clock = pygame.time.Clock()

		self._is_game_loop = False

	def handle_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self._is_game_loop = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self._is_game_loop = False

			self.on_event(event)

	def on_event(self, event) -> None:
		pass

	def update(self) -> None:
		pass

	def render(self) -> None:
		self._screen.fill(self._bg)
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
