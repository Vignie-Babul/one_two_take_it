import pygame


pygame.init()


class Player(pygame.sprite.Sprite):
	def __init__(
		self,
		position,
		size=50,
		color='#00ff00',
		speed=5
	) -> None:

		super().__init__()

		self._size = size
		self._color = color
		self._speed = speed

		self._velocity = pygame.math.Vector2(0, 0)

		self.image = pygame.Surface((size, size))
		self.image.fill(color)

		self.rect = self.image.get_rect(center=position)

	def move(self, direction) -> None:
		if direction == 'left':
			self._velocity.x = -self._speed
		elif direction == 'right':
			self._velocity.x = self._speed
		elif direction == 'up':
			self._velocity.y = -self._speed
		elif direction == 'down':
			self._velocity.y = self._speed

	def stop_horizontal(self) -> None:
		self._velocity.x = 0

	def stop_vertical(self) -> None:
		self._velocity.y = 0

	def set_color(self, color) -> None:
		self._color = color
		self.image.fill(color)

	def update(self, screen_width, screen_height) -> None:
		self.rect.x += self._velocity.x
		self.rect.y += self._velocity.y

		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.right > screen_width:
			self.rect.right = screen_width
		if self.rect.top < 0:
			self.rect.top = 0
		if self.rect.bottom > screen_height:
			self.rect.bottom = screen_height
