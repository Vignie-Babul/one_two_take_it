from Box2D import b2Vec2, b2DistanceJointDef, b2PolygonShape, b2FixtureDef
import pygame

from .physic import PhysicsBody


class PlayerPart(PhysicsBody):
	def __init__(
		self,
		physics_world,
		position: tuple[int | float, int | float],
		size: tuple[int | float, int | float],
		texture: pygame.Surface | None = None,
		color: str = '#00ff00',
	) -> None:
		super().__init__(
			physics_world=physics_world,
			position=position,
			size=size,
			body_type='dynamic',
			shape_type='box',
			density=1.0,
			friction=0.0,
			restitution=0.0
		)

		self._texture = texture
		self._color = color
		self.body.fixedRotation = True
		self.body.bullet = True

		self._render()

	def _render(self) -> None:
		if self._texture is not None:
			self.image = pygame.transform.scale(self._texture, self.size)
		else:
			self.image = pygame.Surface(self.size, pygame.SRCALPHA)
			self.image.fill(self._color)


class CourierBag(PhysicsBody):
	def __init__(
		self,
		physics_world,
		position: tuple[int | float, int | float],
		size: tuple[int | float, int | float],
		texture: pygame.Surface | None = None,
		color: str = '#8B4513',
		max_distance: float = 2.5,
	) -> None:
		super().__init__(
			physics_world=physics_world,
			position=position,
			size=size,
			body_type='dynamic',
			shape_type='box',
			density=0.5,
			friction=0.2,
			restitution=0.1
		)

		self._texture = texture
		self._color = color
		self._max_distance = max_distance
		self._is_torn = False

		self.body.fixedRotation = False
		self.body.bullet = True
		
		self._render()

	def _render(self) -> None:
		if self._texture is not None:
			self._surface = pygame.transform.scale(self._texture, self.size)
			self.image = self._surface.copy()
		else:
			self._surface = pygame.Surface(self.size, pygame.SRCALPHA)
			self._surface.fill(self._color)
			self.image = self._surface.copy()

	def check_tear(self, left_pos: b2Vec2, right_pos: b2Vec2) -> bool:
		distance = (right_pos - left_pos).length

		if distance > self._max_distance:
			self._is_torn = True
			return True

		return False

	def start_tear_animation(self) -> None:
		self._is_tearing = True
		self._tear_scale = 1.0
		self._tear_alpha = 255

	def update_tear_animation(self) -> bool:
		if not hasattr(self, '_is_tearing') or not self._is_tearing:
			return False

		self._tear_scale -= 0.15
		self._tear_alpha -= 25

		if self._tear_scale <= 0 or self._tear_alpha <= 0:
			self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
			self.rect = self.image.get_rect(center=self.rect.center)
			return True

		if self._tear_scale <= 0.05:
			self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
			self.rect = self.image.get_rect(center=self.rect.center)
			return False

		if self._texture is not None:
			original_image = pygame.transform.scale(self._texture, self.size)
		else:
			original_image = pygame.Surface(self.size, pygame.SRCALPHA)
			original_image.fill(self._color)

		new_size = (
			max(1, int(self.size[0] * self._tear_scale)),
			max(1, int(self.size[1] * self._tear_scale))
		)
		scaled = pygame.transform.scale(original_image, new_size)
		scaled.set_alpha(int(self._tear_alpha))
		self.image = scaled
		self.rect = self.image.get_rect(center=self.rect.center)

		return False

	def reset(self) -> None:
		self._is_torn = False
		self._is_tearing = False
		self._render()
		self.rect = self.image.get_rect()
	
		for fixture in self.body.fixtures:
			self.body.DestroyFixture(fixture)
	
		size_meters = (
			self.physics_world.pixels_to_meters(self.size[0]) / 2,
			self.physics_world.pixels_to_meters(self.size[1]) / 2
		)
	
		shape = b2PolygonShape(box=size_meters)
		fixture_def = b2FixtureDef(
			shape=shape,
			density=0.5,
			friction=0.2,
			restitution=0.1
		)
		self.body.CreateFixture(fixture_def)
	
	@property
	def is_torn(self) -> bool:
		return self._is_torn


class Player(pygame.sprite.Sprite):
	def __init__(
		self,
		physics_world,
		position: tuple[int | float, int | float],
		size: int | float = 50,
		speed: int | float = 10,
		jump_force: int | float = 150,
		left_texture: pygame.Surface | None = None,
		right_texture: pygame.Surface | None = None,
		bag_texture: pygame.Surface | None = None,
	) -> None:
		super().__init__()
	
		self._physics_world = physics_world
		self._initial_position = position
		self._size = size
		self._speed = speed
		self._jump_force = jump_force
	
		part_width = int(size * 0.4)
		part_height = int(size * 1.2)
		bag_size = int(size * 0.65)
		gap = 8
	
		left_x = position[0] - part_width // 2 - gap - bag_size // 2
		right_x = position[0] + part_width // 2 + gap + bag_size // 2
	
		self._left_part = PlayerPart(
			physics_world=physics_world,
			position=(left_x, position[1]),
			size=(part_width, part_height),
			texture=left_texture,
			color='#00ff00'
		)
	
		self._right_part = PlayerPart(
			physics_world=physics_world,
			position=(right_x, position[1]),
			size=(part_width, part_height),
			texture=right_texture,
			color='#00ff00'
		)
	
		self._bag = CourierBag(
			physics_world=physics_world,
			position=(position[0], position[1]),
			size=(bag_size, bag_size),
			texture=bag_texture,
			color='#8B4513',
			max_distance=physics_world.pixels_to_meters(size * 2.0)
		)
	
		self._left_joint = None
		self._right_joint = None
		self._create_joints()
	
		self._left_keys = {'left': False, 'jump': False}
		self._right_keys = {'right': False, 'jump': False}
	
		self._left_on_ground = False
		self._right_on_ground = False
		self._left_jumps = 0
		self._right_jumps = 0
		self._max_jumps = 2

		self._spawn_locked = True
		self._spawn_lock_frames = 30

		self._bag_tear_animation_done = False

		self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
		self.rect = self.image.get_rect()

	def _create_joints(self) -> None:
		if self._left_joint is not None:
			self._physics_world.world.DestroyJoint(self._left_joint)
		if self._right_joint is not None:
			self._physics_world.world.DestroyJoint(self._right_joint)

		left_joint_def = b2DistanceJointDef()
		left_joint_def.bodyA = self._left_part.body
		left_joint_def.bodyB = self._bag.body
		left_joint_def.localAnchorA = b2Vec2(0, 0)
		left_joint_def.localAnchorB = b2Vec2(0, 0)
		left_joint_def.length = (self._left_part.body.position - self._bag.body.position).length
		left_joint_def.collideConnected = True
		left_joint_def.dampingRatio = 0.5
		left_joint_def.frequencyHz = 2.0
		self._left_joint = self._physics_world.world.CreateJoint(left_joint_def)

		right_joint_def = b2DistanceJointDef()
		right_joint_def.bodyA = self._right_part.body
		right_joint_def.bodyB = self._bag.body
		right_joint_def.localAnchorA = b2Vec2(0, 0)
		right_joint_def.localAnchorB = b2Vec2(0, 0)
		right_joint_def.length = (self._right_part.body.position - self._bag.body.position).length
		right_joint_def.collideConnected = True
		right_joint_def.dampingRatio = 0.5
		right_joint_def.frequencyHz = 2.0
		self._right_joint = self._physics_world.world.CreateJoint(right_joint_def)

	def _destroy_joints(self) -> None:
		if self._left_joint is not None:
			self._physics_world.world.DestroyJoint(self._left_joint)
			self._left_joint = None
		if self._right_joint is not None:
			self._physics_world.world.DestroyJoint(self._right_joint)
			self._right_joint = None

	def _check_ground(self, body, is_left: bool) -> bool:
		ground_contacts = 0

		for contact_edge in body.contacts:
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
					body_center_x = body.position.x
					x_diff = abs(contact_center_x - body_center_x)
					body_half_width = self._physics_world.pixels_to_meters(self._size * 0.4) / 2
					if x_diff < body_half_width * 0.8:
						return True
				else:
					return True

		return ground_contacts > 0

	def _move_left_part(self) -> None:
		if self._spawn_locked:
			return
		vel_left = self._left_part.body.linearVelocity
		vel_right = self._right_part.body.linearVelocity
		self._left_part.body.linearVelocity = b2Vec2(-self._speed, vel_left.y)
		self._right_part.body.linearVelocity = b2Vec2(-self._speed, vel_right.y)

	def _move_right_part(self) -> None:
		if self._spawn_locked:
			return
		vel_left = self._left_part.body.linearVelocity
		vel_right = self._right_part.body.linearVelocity
		self._left_part.body.linearVelocity = b2Vec2(self._speed, vel_left.y)
		self._right_part.body.linearVelocity = b2Vec2(self._speed, vel_right.y)

	def _stop_left_part(self) -> None:
		if self._spawn_locked:
			return
		vel_left = self._left_part.body.linearVelocity
		vel_right = self._right_part.body.linearVelocity
		self._left_part.body.linearVelocity = b2Vec2(0, vel_left.y)
		self._right_part.body.linearVelocity = b2Vec2(0, vel_right.y)

	def _stop_right_part(self) -> None:
		if self._spawn_locked:
			return
		vel_left = self._left_part.body.linearVelocity
		vel_right = self._right_part.body.linearVelocity
		self._left_part.body.linearVelocity = b2Vec2(0, vel_left.y)
		self._right_part.body.linearVelocity = b2Vec2(0, vel_right.y)

	def _jump_part(self, body, jumps_remaining: int) -> int:
		if self._spawn_locked or jumps_remaining <= 0:
			return jumps_remaining

		vel = body.linearVelocity
		body.linearVelocity = b2Vec2(vel.x, 0)
		body.ApplyLinearImpulse(b2Vec2(0, self._jump_force), body.worldCenter, True)
		return jumps_remaining - 1

	def _update_spawn_lock(self) -> None:
		if self._spawn_locked:
			self._spawn_lock_frames -= 1
			if self._spawn_lock_frames <= 0:
				left_vel = self._left_part.body.linearVelocity
				right_vel = self._right_part.body.linearVelocity
				if abs(left_vel.y) < 0.5 and abs(right_vel.y) < 0.5:
					self._spawn_locked = False
					self._left_jumps = self._max_jumps
					self._right_jumps = self._max_jumps

	def move_key(self, key: str, state: bool) -> None:
		if key == 'left':
			self._left_keys['left'] = state
		elif key == 'right':
			self._right_keys['right'] = state
		elif key == 'jump_left':
			self._left_keys['jump'] = state
		elif key == 'jump_right':
			self._right_keys['jump'] = state

	def check_bounds(self, screen_width: int, screen_height: int) -> bool:
		left_pos = self._physics_world.world_to_screen(
			(
				self._left_part.body.position.x, 
				self._left_part.body.position.y
			)
		)
		right_pos = self._physics_world.world_to_screen(
			(
				self._right_part.body.position.x, self._right_part.body.position.y
			)
		)
		bag_pos = self._physics_world.world_to_screen(
			(
				self._bag.body.position.x, self._bag.body.position.y
			)
		)

		margin = 200
		return (left_pos[1] > screen_height + margin or 
				right_pos[1] > screen_height + margin or 
				bag_pos[1] > screen_height + margin)

	def is_game_over(self) -> bool:
		return self._bag.is_torn

	def get_bag_screen_position(self) -> tuple[float, float]:
		return self._physics_world.world_to_screen(
			(self._bag.body.position.x, self._bag.body.position.y)
		)

	def get_bag_size(self) -> tuple[int, int]:
		return self._bag.size

	def should_spawn_debris(self) -> bool:
		return self._bag_tear_animation_done

	def get_parts_velocities(self) -> tuple[tuple[float, float], tuple[float, float]]:
		left_vel = self._left_part.body.linearVelocity
		right_vel = self._right_part.body.linearVelocity
		return ((left_vel.x, left_vel.y), (right_vel.x, right_vel.y))

	def respawn(self) -> None:
		part_width = int(self._size * 0.4)
		bag_size = int(self._size * 0.65)
		gap = 8

		left_x = self._initial_position[0] - part_width // 2 - gap - bag_size // 2
		right_x = self._initial_position[0] + part_width // 2 + gap + bag_size // 2

		self._bag.reset()

		self._left_part.body.position = b2Vec2(
			*self._physics_world.screen_to_world(
				(
					left_x,
					self._initial_position[1]
				)
			)
		)
		self._left_part.body.linearVelocity = b2Vec2(0, 0)
		self._left_part.body.angularVelocity = 0

		self._right_part.body.position = b2Vec2(
			*self._physics_world.screen_to_world(
				(
					right_x, 
					self._initial_position[1]
				)
			)
		)
		self._right_part.body.linearVelocity = b2Vec2(0, 0)
		self._right_part.body.angularVelocity = 0

		self._bag.body.position = b2Vec2(
			*self._physics_world.screen_to_world(
				self._initial_position
			)
		)
		self._bag.body.linearVelocity = b2Vec2(0, 0)
		self._bag.body.angularVelocity = 0

		self._left_part._update_sprite_position()
		self._right_part._update_sprite_position()
		self._bag._update_sprite_position()

		self._create_joints()

		self._spawn_locked = True
		self._spawn_lock_frames = 30
		self._left_jumps = 0
		self._right_jumps = 0
		self._left_on_ground = False
		self._right_on_ground = False
		self._bag_tear_animation_done = False

	def update(self) -> None:
		self._update_spawn_lock()

		if self._bag.is_torn and not self._bag_tear_animation_done:
			if not hasattr(self._bag, '_is_tearing') or not self._bag._is_tearing:
				self._bag.start_tear_animation()
				self._destroy_joints()

			if self._bag.update_tear_animation():
				self._bag_tear_animation_done = True

		if not self._spawn_locked:
			left_on_ground = self._check_ground(self._left_part.body, True)
			right_on_ground = self._check_ground(self._right_part.body, False)

			if left_on_ground and not self._left_on_ground:
				self._left_jumps = self._max_jumps
			elif (not left_on_ground
					and self._left_on_ground
					and self._left_jumps == self._max_jumps):
				self._left_jumps = self._max_jumps - 1

			if right_on_ground and not self._right_on_ground:
				self._right_jumps = self._max_jumps
			elif (not right_on_ground
					and self._right_on_ground
					and self._right_jumps == self._max_jumps):
				self._right_jumps = self._max_jumps - 1

			self._left_on_ground = left_on_ground
			self._right_on_ground = right_on_ground

			left_wants_move = self._left_keys['left']
			right_wants_move = self._right_keys['right']

			if left_wants_move and right_wants_move:
				self._bag._is_torn = True
				self._stop_left_part()
			elif left_wants_move:
				self._move_left_part()
			elif right_wants_move:
				self._move_right_part()
			else:
				self._stop_left_part()

			if self._left_keys['jump']:
				self._left_jumps = self._jump_part(self._left_part.body, self._left_jumps)
				self._left_keys['jump'] = False

			if self._right_keys['jump']:
				self._right_jumps = self._jump_part(self._right_part.body, self._right_jumps)
				self._right_keys['jump'] = False

		self._bag.check_tear(self._left_part.body.position, self._right_part.body.position)

		self._left_part.update()
		self._right_part.update()
		self._bag.update()

	def draw(self, surface: pygame.Surface) -> None:
		surface.blit(self._left_part.image, self._left_part.rect)
		surface.blit(self._right_part.image, self._right_part.rect)
		surface.blit(self._bag.image, self._bag.rect)
