import pygame

from .physic import PhysicsBody


class Platform(PhysicsBody):
	def __init__(
		self,
		physics_world,
		position: tuple[int | float, int | float],
		size: tuple[int | float, int | float],
		color: str = '#404040',
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
		pygame.draw.rect(self.image, '#606060', (0, 0, self.size[0], self.size[1]), 2)


class FinishPlatform(Platform):
	def __init__(
		self,
		physics_world,
		position: tuple[int | float, int | float],
		size: tuple[int | float, int | float],
	) -> None:
		super().__init__(
			physics_world=physics_world,
			position=position,
			size=size,
			color='#ff0000'
		)
		self._has_triggered = False

	def check_player_on_platform(self, player) -> bool:
		if self._has_triggered:
			return False

		left_touching = False
		right_touching = False

		for contact_edge in self.body.contacts:
			contact = contact_edge.contact
			if not contact.touching:
				continue

			other_body = contact_edge.other

			if other_body == player._left_part.body:
				left_touching = True
			elif other_body == player._right_part.body:
				right_touching = True

		if left_touching and right_touching and not player.is_game_over():
			self._has_triggered = True
			return True

		return False

	def reset(self) -> None:
		self._has_triggered = False
