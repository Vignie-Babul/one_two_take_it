import math
import random

import pygame


class Confetti:
	def __init__(
		self,
		x: float,
		y: float,
		color: str,
		width: int,
		height: int,
		angle_deg: float,
		velocity: float,
		gravity: float = 0.3,
		fade_speed: float = 1.5,
		damping: float = 0.98,
		rotation_speed: float = 0.0,
	) -> None:
		self._x = x
		self._y = y
		self._color = pygame.Color(color)
		self._base_width = width
		self._base_height = height
		self._width = width
		self._height = height
		self._alpha = 255
		self._fade_speed = fade_speed
		self._gravity = gravity
		self._damping = damping
		self._rotation = random.uniform(0, 360)
		self._rotation_speed = rotation_speed
		
		angle_rad = math.radians(angle_deg)
		initial_velocity = velocity
		self._velocity_x = initial_velocity * math.cos(angle_rad)
		self._velocity_y = -initial_velocity * math.sin(angle_rad)
		
		self._base_surface = pygame.Surface((width, height), pygame.SRCALPHA)
		self._base_surface.fill(self._color)
		self._surface = self._base_surface.copy()
		self._update_surface()

	def _update_surface(self) -> None:
		if abs(self._rotation_speed) > 0.01:
			rotated = pygame.transform.rotate(self._base_surface, self._rotation)
			self._surface = rotated.copy()
		else:
			self._surface = self._base_surface.copy()
		
		self._surface.set_alpha(int(self._alpha))

	def update(self) -> bool:
		self._velocity_y += self._gravity
		self._velocity_x *= self._damping
		self._velocity_y *= self._damping
		
		self._x += self._velocity_x
		self._y += self._velocity_y
		
		self._rotation += self._rotation_speed
		self._rotation_speed *= 0.99
		
		self._alpha -= self._fade_speed
		if self._alpha <= 0:
			return False
		
		self._update_surface()
		return True

	@property
	def depth(self) -> float:
		return 1.0


def create_confetti(
	position: tuple[float, float],
	screen_size: tuple[int, int],
) -> list[Confetti]:
	confetti_list = []
	
	color_pool = [
		'#FF6B6B',  # красный
		'#4ECDC4',  # бирюзовый
		'#45B7D1',  # голубой
		'#FFA07A',  # оранжевый
		'#98D8C8',  # мятный
		'#F7DC6F',  # желтый
		'#BB8FCE',  # фиолетовый
		'#85C1E2',  # светло-голубой
	]
	
	confetti_count = 80
	
	for _ in range(confetti_count):
		width = random.randint(3, 8)
		height = random.randint(8, 15)
		
		offset_x = random.uniform(-50, 50)
		offset_y = random.uniform(-50, 50)
		x = position[0] + offset_x
		y = position[1] + offset_y
		
		angle = random.uniform(60, 120)
		velocity = random.uniform(8, 15)
		
		rotation_speed = random.uniform(-15, 15)
		
		color = random.choice(color_pool)
		damping = random.uniform(0.97, 0.99)
		
		confetto = Confetti(
			x=x,
			y=y,
			color=color,
			width=width,
			height=height,
			angle_deg=angle,
			velocity=velocity,
			gravity=0.3,
			fade_speed=255 / (60 * 3),
			damping=damping,
			rotation_speed=rotation_speed,
		)
		confetti_list.append(confetto)
	
	return confetti_list
