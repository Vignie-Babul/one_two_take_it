import pygame


pygame.init()


class Player(pygame.sprite.Sprite):
	def __init__(
		self,
		position: tuple[int | float, int | float],
		size: tuple[int | float, int | float] = (50, 50),
		color: str = '#00ff00',
		speed: int | float = 5
	) -> None:

		super().__init__()

		self._speed = speed
		self._velocity = pygame.math.Vector2(0, 0)

		self._keys_pressed = {
			'right': False,
			'left': False,
			'up': False,
			'down': False,
		}

		self.image = pygame.Surface(size)
		self.image.fill(color)
		self.rect = self.image.get_rect(center=position)

	def _stop_horizontal(self) -> None:
		self._velocity.x = 0

	def _stop_vertical(self) -> None:
		self._velocity.y = 0

	def _move(self, direction: str) -> None:
		match direction:
			case 'left':
				self._velocity.x = -self._speed
			case 'right':
				self._velocity.x = self._speed
			case 'up':
				self._velocity.y = -self._speed
			case 'down':
				self._velocity.y = self._speed

	def _check_direction(self) -> None:
		self._stop_horizontal()
		self._stop_vertical()

		for _key, _state in self._keys_pressed.items():
			if _state:
				self._move(_key)

	def move_key(self, key: str, state: bool) -> None:
		self._keys_pressed[key] = state

	def set_color(self, color: str) -> None:
		self.image.fill(color)

	def update(self, screen_size: tuple[int, int]) -> None:
		self._check_direction()
		self.rect.move_ip(self._velocity.x, self._velocity.y)

		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.right > screen_size[0]:
			self.rect.right = screen_size[0]
		if self.rect.top < 0:
			self.rect.top = 0
		if self.rect.bottom > screen_size[1]:
			self.rect.bottom = screen_size[1]

