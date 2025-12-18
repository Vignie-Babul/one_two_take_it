import pygame

from src.ui import AccentButton, Container, NeutralButton, Text


FOG_BASE = '#595969'
FOG_DARK = '#3a3a46'
FOG_LIGHT = '#8a8a9e'
FOG_ACCENT = '#6e6e7d'
FOG_TEXT = '#e8e8f0'


class MainMenu:
	def __init__(self, screen_size: tuple[int, int] = (1280, 720)) -> None:
		self.screen_size = screen_size
		self.screen = None
		self.clock = pygame.time.Clock()
		self.start_game = False
		self.quit_game = False
		self.container = None

	def _on_start(self) -> None:
		self.start_game = True

	def _on_quit(self) -> None:
		self.quit_game = True

	def run(self) -> str:
		self.screen = pygame.display.set_mode(self.screen_size, pygame.FULLSCREEN)
		pygame.display.set_caption('Раз, два, взяли')

		cx = self.screen_size[0] // 2
		cy = self.screen_size[1] // 2

		title = Text(
			text='РАЗ, ДВА, ВЗЯЛИ',
			pos=(cx - 350, cy - 250),
			size=(700, 140),
			background=FOG_DARK,
			foreground=FOG_TEXT,
			font_size=72,
			round_=16,
			border_width=4,
			border_color=FOG_LIGHT
		)

		start_button = AccentButton(
			text='НАЧАТЬ',
			pos=(cx - 250, cy + 0),
			size=(500, 90),
			command=self._on_start,
			font_size=40,
			background=FOG_ACCENT,
			foreground=FOG_TEXT,
			dark_color='#00000040',
			light_color='#ffffff20',
			border_color=FOG_LIGHT
		)

		quit_button = NeutralButton(
			text='ВЫХОД',
			pos=(cx - 250, cy + 110),
			size=(500, 90),
			command=self._on_quit,
			font_size=40,
			background=FOG_BASE,
			foreground=FOG_TEXT,
			dark_color='#00000040',
			light_color='#ffffff15',
			border_color=FOG_ACCENT
		)

		self.container = Container()
		self.container.add(title, start_button, quit_button)

		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return 'quit'
				if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					return 'quit'

				self.container.update(event)

			self.screen.fill('#1a1a1a')
			self.container.draw(self.screen)
			pygame.display.flip()
			self.clock.tick(60)

			if self.start_game:
				return 'start'
			if self.quit_game:
				return 'quit'


class PauseMenu:
	def __init__(self, screen_size: tuple[int, int]) -> None:
		self.screen_size = screen_size
		self.action = None

		cx = screen_size[0] // 2
		cy = screen_size[1] // 2

		self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)

		fog_rgba = (89, 89, 105, 230)
		self.overlay.fill(fog_rgba)

		self.title = Text(
			text='ПАУЗА',
			pos=(cx - 180, cy - 220),
			size=(360, 120),
			background=FOG_DARK,
			foreground=FOG_TEXT,
			font_size=68,
			round_=16,
			border_width=4,
			border_color=FOG_LIGHT
		)

		self.resume_button = AccentButton(
			text='ПРОДОЛЖИТЬ',
			pos=(cx - 250, cy - 60),
			size=(500, 80),
			command=self._on_resume,
			font_size=32,
			background=FOG_ACCENT,
			foreground=FOG_TEXT,
			dark_color='#00000040',
			light_color='#ffffff20',
			border_color=FOG_LIGHT
		)

		self.restart_button = NeutralButton(
			text='ЗАНОВО',
			pos=(cx - 250, cy + 30),
			size=(500, 80),
			command=self._on_restart,
			font_size=32,
			background=FOG_BASE,
			foreground=FOG_TEXT,
			dark_color='#00000040',
			light_color='#ffffff15',
			border_color=FOG_ACCENT
		)

		self.menu_button = NeutralButton(
			text='В МЕНЮ',
			pos=(cx - 250, cy + 120),
			size=(500, 80),
			command=self._on_menu,
			font_size=32,
			background=FOG_DARK,
			foreground=FOG_TEXT,
			dark_color='#00000040',
			light_color='#ffffff10',
			border_color=FOG_BASE
		)

		self.container = Container()
		self.container.add(self.title, self.resume_button, self.restart_button, self.menu_button)

	def _on_resume(self) -> None:
		self.action = 'resume'

	def _on_restart(self) -> None:
		self.action = 'restart'

	def _on_menu(self) -> None:
		self.action = 'menu'

	def handle_event(self, event: pygame.event.Event) -> None:
		self.container.update(event)

	def draw(self, surface: pygame.Surface) -> None:
		surface.blit(self.overlay, (0, 0))
		self.container.draw(surface)

	def get_action(self) -> str | None:
		action = self.action
		self.action = None
		return action
