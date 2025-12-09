import pygame


class Particle:
	def __init__(
		self,
		x: float,
		y: float,
		vector: pygame.math.Vector2,
		angle: float,
		velocity: float,
		screen_size: None | tuple[float, float] = None,
	) -> None:

		self.x = x
		self.y = y
		self._screen_size = screen_size

		self._is_graphic_use = self._screen_size is not None

		self._vec2 = vector.rotate(angle).normalize()
		self._vec2.scale_to_length(velocity)

	def __repr__(self) -> str:
		return f'{self.__class__.__name__}({self.x}, {self.y})'

	def _is_out_bounds(self) -> bool:
		_is_out_bounds_x = (self.x < 0) or (self.x > self._screen_size[0])
		_is_out_bounds_y = self.y > self._screen_size[1]
		return _is_out_bounds_x or _is_out_bounds_y

	def update(self) -> bool:
		"""return boolean value for particle deletion from container"""

		if self._is_graphic_use and self._is_out_bounds():
			return False

		self.x += self._vec2.x
		self.y += self._vec2.y
		return True

	def draw(self, master: pygame.Surface) -> None:
		pygame.draw.rect(master, '#f2f2f2', (self.x, self.y, 1, 2))
