from collections.abc import Callable

import pygame


pygame.init()


class UI:
	def __init__(self, **kwargs) -> None:
		self._kwargs = kwargs
		self.defaults = {
			'background': '#000000',
			'foreground': '#f2f2f2',
			'round_': 8,
			'smoothscale': 8,
			'border_width': 1,
			'font_name': None,
			'font_size': 20,
		}
		self._set_default_args()

	def _set_default_args(self) -> None:
		for arg, value in self._kwargs.items():
			if arg not in self.defaults:
				continue
			private_name = f'_{arg}'
			if value is None:
				setattr(self, private_name, self.defaults[arg])
			else:
				setattr(self, private_name, value)

		for arg, default in self.defaults.items():
			private_name = f'_{arg}'
			if not hasattr(self, private_name):
				setattr(self, private_name, default)


class Button(UI):
	def __init__(
		self,
		text: str,
		pos: tuple[float, float],
		size: tuple[int, int],
		command: Callable | None = None,
		background: str | None = '#f2f2f2',
		foreground: str | None = '#000000',
		round_: int | None = None,
		smoothscale: int | None = None,
		dark_color: str | None = '#00000030',
		light_color: str | None = '#ffffff15',
		border_width: int = None,
		border_color: str | None = '#000000',
		font_name: str | None = None,
		font_size: int | None = None,
	) -> None:
		super().__init__(
			background=background,
			foreground=foreground,
			round_=round_,
			smoothscale=smoothscale,
			border_width=border_width,
			font_name=font_name,
			font_size=font_size,
		)

		self._text = text
		self._pos = pos
		self._size = size
		self._command = command
		self._dark_color = dark_color
		self._light_color = light_color
		self._border_color = border_color
		self._rect = pygame.Rect(*pos, *size)
		self._colors = (
			self._background,
			self._dark_color,
			self._light_color,
		)

		self._is_hovered = False
		self._is_pressed = False
		self._create_high_surfaces()
		self._create_surfaces()
		self._blit_text()

	def _make_high_surface(self) -> pygame.Surface:
		return pygame.Surface(
			(
				self._size[0] * self._smoothscale,
				self._size[1] * self._smoothscale,
			),
			pygame.SRCALPHA,
		)

	def _fill_high_surfaces(self, high_surface: pygame.Surface, color: str) -> None:
		high_surface_rect = high_surface.get_rect()
		smoothscaled_round = self._round_ * self._smoothscale
		if color is not None:
			pygame.draw.rect(
				high_surface,
				color,
				high_surface_rect,
				border_radius=smoothscaled_round,
			)

		is_border_valid = (
			(self._border_width is not None and self._border_width > 0)
			and (self._border_color is not None)
		)
		is_surface_original = high_surface is self._high_original
		if is_border_valid and is_surface_original:
			pygame.draw.rect(
				high_surface,
				self._border_color,
				high_surface_rect,
				width=self._border_width * self._smoothscale,
				border_radius=smoothscaled_round,
			)

	def _create_high_surfaces(self) -> None:
		self._high_surfaces = [
			self._make_high_surface() for _ in range(3)
		]
		self._high_original, self._high_dark, self._high_light = self._high_surfaces
		for high_surface, color in zip(self._high_surfaces, self._colors, strict=True):
			high_surface.lock()
			try:
				self._fill_high_surfaces(high_surface, color)
			finally:
				high_surface.unlock()

	def _create_surfaces(self) -> None:
		surfaces = [
			pygame.transform.smoothscale(
				high_surface,
				self._size,
			) for high_surface in self._high_surfaces
		]
		self._original, self._dark, self._light = surfaces

	def _blit_text(self) -> None:
		if (not self._text) or (self._foreground is None):
			return
		if self._font_name is not None:
			font = pygame.font.Font(self._font_name, self._font_size)
		else:
			font = pygame.font.SysFont('', self._font_size)
		surface = font.render(self._text, True, self._foreground)
		width, height = surface.get_size()
		self._original.blit(
			surface,
			(
				self._size[0]//2 - width//2,
				self._size[1]//2 - height//2,
			)
		)

	def _execute_command(self) -> None:
		if callable(self._command):
			self._command()

	def get_rect(self) -> pygame.Rect:
		return self._rect

	def draw(self, master: pygame.Surface) -> None:
		master.blit(self._original, self._pos)
		if self._is_pressed:
			master.blit(self._dark, self._pos)
		elif self._is_hovered:
			master.blit(self._light, self._pos)

	def update(self, event: pygame.event.Event | None = None) -> bool:
		is_mouse_cursor_collide = self._rect.collidepoint(pygame.mouse.get_pos())
		if not is_mouse_cursor_collide:
			self._is_hovered = False
			self._is_pressed = False
			return False

		self._is_hovered = True

		if event is None:
			is_mouse_left_button_pressed = pygame.mouse.get_pressed()[0]
			if is_mouse_left_button_pressed:
				if not self._is_pressed:
					self._is_pressed = True
					self._execute_command()
			elif self._is_pressed:
				self._is_pressed = False
			return True

		is_mouse_left_down = (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1)
		is_mouse_left_up = (event.type == pygame.MOUSEBUTTONUP) and (event.button == 1)

		if is_mouse_left_down:
			if not self._is_pressed:
				self._is_pressed = True
		elif is_mouse_left_up and self._is_pressed:
				self._is_pressed = False
				self._execute_command()

		return True


class AccentButton(Button):
	def __init__(
		self,
		*args,
		background: str = '#fce000',
		foreground: str = '#000000',
		dark_color: str = '#00000030',
		light_color: str = '#ffffff20',
		border_color: str = '#fce000',
		**kwargs,
	) -> None:
		super().__init__(
			*args,
			background=background,
			foreground=foreground,
			dark_color=dark_color,
			light_color=light_color,
			border_color=border_color,
			**kwargs,
		)


class NeutralButton(Button):
	def __init__(
		self,
		*args,
		background: str | None = '#000000',
		foreground: str | None = '#f2f2f2',
		dark_color: str | None = '#00000030',
		light_color: str | None = '#ffffff0b',
		border_color: str | None = '#252525',
		**kwargs,
	) -> None:
		super().__init__(
			*args,
			background=background,
			foreground=foreground,
			dark_color=dark_color,
			light_color=light_color,
			border_color=border_color,
			**kwargs,
		)


class Text(UI):
	def __init__(
		self,
		text: str,
		pos: tuple[float, float],
		size: tuple[int, int],
		background: str | None = None,
		foreground: str | None = '#f2f2f2',
		round_: int | None = 0,
		smoothscale: int | None = None,
		border_width: int = 0,
		border_color: str | None = None,
		font_name: str | None = None,
		font_size: int | None = None,
	) -> None:
		super().__init__(
			background=background,
			foreground=foreground,
			round_=round_,
			smoothscale=smoothscale,
			border_width=border_width,
			font_name=font_name,
			font_size=font_size,
		)

		self._text = text
		self._pos = pos
		self._size = size
		self._border_color = border_color
		self._rect = pygame.Rect(*pos, *size)
		self._colors = (self._background,)

		self._create_high_surfaces()
		self._create_surfaces()
		self._blit_text()

	def _make_high_surface(self) -> pygame.Surface:
		return pygame.Surface(
			(
				self._size[0] * self._smoothscale,
				self._size[1] * self._smoothscale,
			),
			pygame.SRCALPHA,
		)

	def _fill_high_surfaces(self, high_surface: pygame.Surface, color: str) -> None:
		high_surface_rect = high_surface.get_rect()
		smoothscaled_round = self._round_ * self._smoothscale
		if color is not None:
			pygame.draw.rect(
				high_surface,
				color,
				high_surface_rect,
				border_radius=smoothscaled_round,
			)

		is_border_valid = (
			(self._border_width is not None and self._border_width > 0)
			and (self._border_color is not None)
		)
		is_surface_original = high_surface is self._high_original
		if is_border_valid and is_surface_original:
			pygame.draw.rect(
				high_surface,
				self._border_color,
				high_surface_rect,
				width=self._border_width * self._smoothscale,
				border_radius=smoothscaled_round,
			)

	def _create_high_surfaces(self) -> None:
		self._high_surfaces = [self._make_high_surface()]
		self._high_original = self._high_surfaces[0]
		for high_surface, color in zip(self._high_surfaces, self._colors, strict=True):
			high_surface.lock()
			try:
				self._fill_high_surfaces(high_surface, color)
			finally:
				high_surface.unlock()

	def _create_surfaces(self) -> None:
		surfaces = [
			pygame.transform.smoothscale(
				high_surface,
				self._size,
			) for high_surface in self._high_surfaces
		]
		self._original = surfaces[0]

	def _blit_text(self) -> None:
		if (not self._text) or (self._foreground is None):
			return
		if self._font_name is not None:
			font = pygame.font.Font(self._font_name, self._font_size)
		else:
			font = pygame.font.SysFont('', self._font_size)
		surface = font.render(self._text, True, self._foreground)
		width, height = surface.get_size()
		self._original.blit(
			surface,
			(
				self._size[0]//2 - width//2,
				self._size[1]//2 - height//2,
			)
		)

	def get_rect(self) -> pygame.Rect:
		return self._rect

	def draw(self, master: pygame.Surface) -> None:
		master.blit(self._original, self._pos)

	def update(self, event: pygame.event.Event | None = None) -> bool:
		return True


class Container:
	def __init__(self):
		self._elements = []

	def add(self, *elements):
		for element in elements:
			self._elements.append(element)

	def update(self, event: pygame.event.Event | None = None):
		for element in self._elements:
			element.update(event)

	def draw(self, master: pygame.Surface):
		for element in self._elements:
			element.draw(master)
