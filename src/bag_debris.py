import random
import math

import pygame


class BagDebris:
	def __init__(
		self,
		x: float,
		y: float,
		color: str,
		width: int,
		height: int,
		angle_deg: float,
		velocity: float,
		gravity: float = 0.5,
		fade_speed: float = 2.0,
		damping: float = 0.97,
		z_velocity: float = 0.0,
		rotation_speed: float = 0.0,
	) -> None:
		self._x = x
		self._y = y
		self._z = 1.0
		self._color = pygame.Color(color)
		self._base_width = width
		self._base_height = height
		self._width = width
		self._height = height
		self._alpha = 255
		self._fade_speed = fade_speed
		self._gravity = gravity
		self._damping = damping
		self._z_velocity = z_velocity
		self._z_damping = 0.98

		self._rotation = random.uniform(0, 360)
		self._rotation_speed = rotation_speed

		angle_rad = math.radians(angle_deg)
		initial_velocity = velocity * 2.0
		self._velocity_x = initial_velocity * math.cos(angle_rad)
		self._velocity_y = -initial_velocity * math.sin(angle_rad)

		self._base_surface = pygame.Surface((width, height), pygame.SRCALPHA)
		self._base_surface.fill(self._color)
		self._surface = self._base_surface.copy()
		self._update_surface()

	def _update_surface(self) -> None:
		scale = self._z
		self._width = max(1, int(self._base_width * scale))
		self._height = max(1, int(self._base_height * scale))

		scaled = pygame.transform.scale(self._base_surface, (self._width, self._height))

		if abs(self._rotation_speed) > 0.01:
			rotated = pygame.transform.rotate(scaled, self._rotation)
			self._surface = rotated.copy()
		else:
			self._surface = scaled.copy()

		self._surface.set_alpha(int(self._alpha))

	def update(self) -> bool:
		self._velocity_y += self._gravity

		self._velocity_x *= self._damping
		self._velocity_y *= self._damping
		self._z_velocity *= self._z_damping

		self._x += self._velocity_x
		self._y += self._velocity_y
		self._z += self._z_velocity

		self._rotation += self._rotation_speed
		self._rotation_speed *= 0.99

		if self._z < 0.1:
			self._z = 0.1
		elif self._z > 2.5:
			self._z = 2.5

		self._alpha -= self._fade_speed

		if self._alpha <= 0:
			return False

		self._update_surface()
		return True

	def draw(self, surface: pygame.Surface) -> None:
		if self._alpha > 0:
			draw_x = int(self._x - self._surface.get_width() / 2)
			draw_y = int(self._y - self._surface.get_height() / 2)
			surface.blit(self._surface, (draw_x, draw_y))

	@property
	def depth(self) -> float:
		return self._z


def create_bag_debris(
	bag_position: tuple[float, float],
	bag_size: tuple[int, int],
	screen_size: tuple[int, int],
	left_velocity: tuple[float, float] = (0, 0),
	right_velocity: tuple[float, float] = (0, 0),
) -> list[BagDebris]:
	debris_list = []

	bag_area = bag_size[0] * bag_size[1]
	target_area = bag_area * 0.3

	color_pool = (
		['#000000'] * 45 +
		['#f5d355'] * 45 +
		['#de5434'] * 6 +
		['#ffffff'] * 4
	)

	bag_scale = min(bag_size[0], bag_size[1]) / 33.0

	velocity_diff_x = right_velocity[0] - left_velocity[0]

	if abs(velocity_diff_x) < 0.1:
		angle_bias = 0
	else:
		angle_bias = velocity_diff_x * 5

	current_area = 0
	debris_count = 0
	max_debris = 100

	while current_area < target_area and debris_count < max_debris:
		scale = random.uniform(0.5, 1.5) * bag_scale
		width = int(1 * scale)
		height = int(3 * scale)

		current_area += width * height
		debris_count += 1

		offset_x = random.uniform(-bag_size[0] * 0.3, bag_size[0] * 0.3)
		offset_y = random.uniform(-bag_size[1] * 0.3, bag_size[1] * 0.3)

		x = bag_position[0] + offset_x
		y = bag_position[1] + offset_y

		base_angle = 90 + angle_bias
		angle_variation = random.uniform(-30, 30)
		angle = base_angle + angle_variation

		velocity = random.uniform(2, 5)

		z_velocity = random.uniform(-0.015, 0.025)

		rotation_speed = random.uniform(-8, 8)

		color = random.choice(color_pool)
		damping = random.uniform(0.96, 0.98)

		debris = BagDebris(
			x=x,
			y=y,
			color=color,
			width=width,
			height=height,
			angle_deg=angle,
			velocity=velocity,
			gravity=0.12,
			fade_speed=255 / (60 * 2.5),
			damping=damping,
			z_velocity=z_velocity,
			rotation_speed=rotation_speed
		)

		debris_list.append(debris)

	return debris_list
