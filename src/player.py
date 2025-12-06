import pygame


pygame.init()


class Player(pygame.sprite.Sprite):
	def __init__(
		self,
		position,
		size=(50, 50),
		color='#00ff00',
		speed=5
	) -> None:

		super().__init__()

		self._speed = speed
		self._velocity = pygame.math.Vector2(0, 0)

		self.image = pygame.Surface(size)
		self.image.fill(color)
		self.rect = self.image.get_rect(center=position)

	def move(self, direction) -> None:
		match direction:
			case 'left':
				self._velocity.x = -self._speed
			case 'right':
				self._velocity.x = self._speed
			case 'up':
				self._velocity.y = -self._speed
			case 'down':
				self._velocity.y = self._speed

	def stop_horizontal(self) -> None:
		self._velocity.x = 0

	def stop_vertical(self) -> None:
		self._velocity.y = 0

	def set_color(self, color) -> None:
		self.image.fill(color)

	def update(self, screen_size) -> None:
		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.right > screen_size[0]:
			self.rect.right = screen_size[0]
		if self.rect.top < 0:
			self.rect.top = 0
		if self.rect.bottom > screen_size[1]:
			self.rect.bottom = screen_size[1]

		self.rect.move_ip(self._velocity.x, self._velocity.y)
