from __future__ import annotations

import pygame
from Box2D import b2World, b2Vec2, b2PolygonShape, b2CircleShape, b2BodyDef, b2FixtureDef


class PhysicsWorld:
	def __init__(
		self,
		gravity: tuple[int | float, int | float] = (0, -10),
		ppm: int = 20,
		screen_height: int = 720
	) -> None:
		self.world = b2World(gravity=b2Vec2(*gravity), doSleep=True)
		self.ppm = ppm
		self.screen_height = screen_height
		self.bodies = []

	def step(self, dt: float = 1.0/60.0, vel_iters: int = 8, pos_iters: int = 3) -> None:
		self.world.Step(dt, vel_iters, pos_iters)
		self.world.ClearForces()

	def pixels_to_meters(self, pixels: int | float) -> float:
		return pixels / self.ppm

	def meters_to_pixels(self, meters: float) -> float:
		return meters * self.ppm

	def screen_to_world(self, screen_pos: tuple[int | float, int | float]) -> tuple[float, float]:
		x = screen_pos[0]
		y = self.screen_height - screen_pos[1]
		return (
			self.pixels_to_meters(x),
			self.pixels_to_meters(y)
		)

	def world_to_screen(self, world_pos: tuple[float, float]) -> tuple[float, float]:
		x = self.meters_to_pixels(world_pos[0])
		y = self.screen_height - self.meters_to_pixels(world_pos[1])
		return (x, y)

	def add_body(self, body) -> None:
		self.bodies.append(body)

	def remove_body(self, body) -> None:
		if body in self.bodies:
			self.bodies.remove(body)


class PhysicsBody(pygame.sprite.Sprite):
	def __init__(
		self,
		physics_world: PhysicsWorld,
		position: tuple[int | float, int | float],
		size: tuple[int | float, int | float],
		body_type: str = 'dynamic',
		shape_type: str = 'box',
		density: float = 1.0,
		friction: float = 0.3,
		restitution: float = 0.1
	) -> None:
		super().__init__()

		self.physics_world = physics_world
		self.size = size
		self.ppm = physics_world.ppm

		pos_meters = physics_world.screen_to_world(position)

		size_meters = (
			physics_world.pixels_to_meters(size[0]) / 2,
			physics_world.pixels_to_meters(size[1]) / 2
		)

		body_def = b2BodyDef()
		body_def.position = b2Vec2(*pos_meters)

		if body_type == 'dynamic':
			body_def.type = 2
		elif body_type == 'static':
			body_def.type = 0
		elif body_type == 'kinematic':
			body_def.type = 1

		self.body = physics_world.world.CreateBody(body_def)

		if shape_type == 'box':
			shape = b2PolygonShape(box=size_meters)

			fixture_def = b2FixtureDef(
				shape=shape,
				density=density,
				friction=friction,
				restitution=restitution
			)

			self.body.CreateFixture(fixture_def)
		elif shape_type == 'circle':
			radius = min(size_meters)
			shape = b2CircleShape(radius=radius)

			fixture_def = b2FixtureDef(
				shape=shape,
				density=density,
				friction=friction,
				restitution=restitution
			)

			self.body.CreateFixture(fixture_def)

		self.image = pygame.Surface(size, pygame.SRCALPHA)
		self.rect = self.image.get_rect()

		physics_world.add_body(self)

		self._update_sprite_position()

	def _update_sprite_position(self) -> None:
		pos = self.body.position
		pixel_pos = self.physics_world.world_to_screen((pos.x, pos.y))
		self.rect.center = pixel_pos

	def apply_force(self, force: tuple[int | float, int | float]) -> None:
		self.body.ApplyForce(b2Vec2(*force), self.body.worldCenter, True)

	def apply_impulse(self, impulse: tuple[int | float, int | float]) -> None:
		self.body.ApplyLinearImpulse(b2Vec2(*impulse), self.body.worldCenter, True)

	def set_velocity(self, velocity: tuple[int | float, int | float]) -> None:
		self.body.linearVelocity = b2Vec2(*velocity)

	def get_velocity(self) -> tuple[float, float]:
		vel = self.body.linearVelocity
		return (vel.x, vel.y)

	def update(self) -> None:
		self._update_sprite_position()

	def destroy(self) -> None:
		self.physics_world.world.DestroyBody(self.body)
		self.physics_world.remove_body(self)
