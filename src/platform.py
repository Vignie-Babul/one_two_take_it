import pygame

from .physic import PhysicsBody


class Platform(PhysicsBody):
	def __init__(
		self,
		physics_world,
		position: tuple[int | float, int | float],
		size: tuple[int | float, int | float],
		color: str = '#404040'
	) -> None:
		super().__init__(
			physics_world=physics_world,
			position=position,
			size=size,
			body_type='static',
			shape_type='box',
			friction=0.5
		)

		self._color = color
		self._render()

	def _render(self) -> None:
		self.image.fill(self._color)

		pygame.draw.rect(
			self.image,
			'#606060',
			(0, 0, self.size[0], self.size[1]),
			2
		)
