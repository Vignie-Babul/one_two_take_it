import pygame
from Box2D import b2Vec2, b2PolygonShape, b2FixtureDef

from .physic import PhysicsBody

pygame.init()


class Player(PhysicsBody):
	def __init__(
		self,
		physics_world,
		position: tuple[int | float, int | float],
		size: int | float = 50,
		color: str = '#00ff00',
		speed: int | float = 10,
		jump_force: int | float = 150,
	) -> None:
		self._initial_position = position
		self._initial_size = size
		self._initial_color = color
		self._initial_speed = speed
		self._initial_jump_force = jump_force

		super().__init__(
			physics_world=physics_world,
			position=position,
			size=(size * 1.8, size),
			body_type='dynamic',
			shape_type='custom',
			density=1.0,
			friction=0.0,
			restitution=0.0
		)

		self._color = color
		self._speed = speed
		self._jump_force = jump_force
		self._on_ground = False
		self._jumps_remaining = 0
		self._max_jumps = 2
		self._was_on_ground = False
		self._contact_timeout = 0
		self._spawn_locked = True
		self._spawn_lock_frames = 30
		self._max_wall_contact_frames = 5
		self._wall_contact_frames = 0

		self._keys_pressed = {
			'right': False,
			'left': False,
			'jump': False,
		}

		self.body.fixedRotation = True
		self.body.bullet = True

		self._create_custom_shape()
		self._render()

	def _create_custom_shape(self) -> None:
		rect_width = self.physics_world.pixels_to_meters(self._initial_size * 0.4)
		rect_height = self.physics_world.pixels_to_meters(self._initial_size * 1.2)

		square_size = self.physics_world.pixels_to_meters(self._initial_size * 0.65) / 2
		gap = self.physics_world.pixels_to_meters(8)

		left_rect = b2PolygonShape()
		left_rect.SetAsBox(rect_width / 2, rect_height / 2, (-rect_width / 2 - gap - square_size, 0), 0)

		right_rect = b2PolygonShape()
		right_rect.SetAsBox(rect_width / 2, rect_height / 2, (rect_width / 2 + gap + square_size, 0), 0)

		center_square = b2PolygonShape()
		center_square.SetAsBox(square_size, square_size, (0, 0), 0)

		fixture_def = b2FixtureDef(
			shape=left_rect,
			density=1.0,
			friction=0.0,
			restitution=0.0
		)
		self.body.CreateFixture(fixture_def)

		fixture_def.shape = right_rect
		self.body.CreateFixture(fixture_def)

		fixture_def.shape = center_square
		self.body.CreateFixture(fixture_def)

	def _render(self) -> None:
		self.image.fill((0, 0, 0, 0))

		rect_width = int(self._initial_size * 0.4)
		rect_height = int(self._initial_size * 1.2)
		square_size = int(self._initial_size * 0.65)
		gap = 8

		center_x = self.size[0] // 2
		center_y = self.size[1] // 2

		left_rect_x = center_x - rect_width // 2 - gap - square_size // 2
		left_rect = pygame.Rect(
			left_rect_x - rect_width // 2,
			center_y - rect_height // 2,
			rect_width,
			rect_height
		)
		pygame.draw.rect(self.image, self._color, left_rect)

		right_rect_x = center_x + rect_width // 2 + gap + square_size // 2
		right_rect = pygame.Rect(
			right_rect_x - rect_width // 2,
			center_y - rect_height // 2,
			rect_width,
			rect_height
		)
		pygame.draw.rect(self.image, self._color, right_rect)

		center_square = pygame.Rect(
			center_x - square_size // 2,
			center_y - square_size // 2,
			square_size,
			square_size
		)
		pygame.draw.rect(self.image, self._color, center_square)

	def _move_left(self) -> None:
		if self._spawn_locked:
			return
		vel = self.body.linearVelocity
		self.body.linearVelocity = b2Vec2(-self._speed, vel.y)

	def _move_right(self) -> None:
		if self._spawn_locked:
			return
		vel = self.body.linearVelocity
		self.body.linearVelocity = b2Vec2(self._speed, vel.y)

	def _stop_horizontal(self) -> None:
		if self._spawn_locked:
			return
		vel = self.body.linearVelocity
		self.body.linearVelocity = b2Vec2(0, vel.y)

	def _jump(self) -> None:
		if self._spawn_locked:
			return
		if self._jumps_remaining > 0:
			vel = self.body.linearVelocity
			self.body.linearVelocity = b2Vec2(vel.x, 0)
			self.apply_impulse((0, self._jump_force))
			self._jumps_remaining -= 1
			self._on_ground = False
			self._contact_timeout = 10

	def _check_direction(self) -> None:
		if self._keys_pressed['left']:
			self._move_left()
		elif self._keys_pressed['right']:
			self._move_right()
		else:
			self._stop_horizontal()

		if self._keys_pressed['jump']:
			self._jump()
			self._keys_pressed['jump'] = False

	def _check_ground(self) -> None:
		if self._contact_timeout > 0:
			self._contact_timeout -= 1
			return

		ground_contacts = 0
		wall_contacts = 0
		valid_ground_contact = False

		for contact_edge in self.body.contacts:
			contact = contact_edge.contact

			if not contact.touching:
				continue

			world_manifold = contact.worldManifold

			if len(world_manifold.points) < 1:
				continue

			if world_manifold.normal[1] > 0.5:
				ground_contacts += 1

				if len(world_manifold.points) >= 2:
					contact_center_x = sum(p[0] for p in world_manifold.points) / len(world_manifold.points)
					body_center_x = self.body.position.x

					x_diff = abs(contact_center_x - body_center_x)
					body_half_width = self.physics_world.pixels_to_meters(self.size[0]) / 2

					if x_diff < body_half_width * 0.8:
						valid_ground_contact = True
				else:
					valid_ground_contact = True
			elif abs(world_manifold.normal[0]) > 0.7:
				wall_contacts += 1

		if wall_contacts > 0 and ground_contacts == 0:
			self._wall_contact_frames += 1
			if self._wall_contact_frames > self._max_wall_contact_frames and self._jumps_remaining == 0:
				self._jumps_remaining = 1
		else:
			self._wall_contact_frames = 0

		if ground_contacts > 0 and valid_ground_contact:
			if not self._was_on_ground:
				self._jumps_remaining = self._max_jumps
				self._on_ground = True
				self._was_on_ground = True
				if self._spawn_locked:
					self._spawn_locked = False
		else:
			if self._was_on_ground and self._on_ground and self._jumps_remaining == self._max_jumps:
				self._jumps_remaining = self._max_jumps - 1
			self._on_ground = False
			self._was_on_ground = False

	def _update_spawn_lock(self) -> None:
		if self._spawn_locked:
			self._spawn_lock_frames -= 1
			if self._spawn_lock_frames <= 0:
				vel = self.body.linearVelocity
				if abs(vel.y) < 0.5:
					self._spawn_locked = False
					self._jumps_remaining = self._max_jumps

	def move_key(self, key: str, state: bool) -> None:
		self._keys_pressed[key] = state

	def set_color(self, color: str) -> None:
		self._color = color
		self._render()

	def check_bounds(self, screen_width: int, screen_height: int) -> bool:
		pos = self.physics_world.world_to_screen((self.body.position.x, self.body.position.y))
		margin = 200
		return pos[1] > screen_height + margin

	def respawn(self) -> None:
		self.body.position = b2Vec2(*self.physics_world.screen_to_world(self._initial_position))
		self.body.linearVelocity = b2Vec2(0, 0)
		self.body.angularVelocity = 0
		self._spawn_locked = True
		self._spawn_lock_frames = 30
		self._jumps_remaining = 0
		self._on_ground = False
		self._was_on_ground = False
		self._contact_timeout = 0
		self._wall_contact_frames = 0

	def update(self) -> None:
		super().update()
		self._update_spawn_lock()
		self._check_ground()
		self._check_direction()
