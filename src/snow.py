import random


class Snowflake:
	def __init__(self, x: float, y: float, velocity: float, screen_width: int):
		self.x = x
		self.y = y
		self.velocity = velocity
		self.screen_width = screen_width

	def update(self):
		self.y += self.velocity

	def should_respawn(self, camera_top: float, camera_bottom: float) -> bool:
		return self.y > camera_bottom

	def respawn(self, camera_left: float, camera_right: float, camera_top: float):
		self.x = random.uniform(camera_left, camera_right)
		self.y = camera_top - random.uniform(10, 50)


def create_snow(density: int, screen_width: int, screen_height: int, camera_offset: tuple[int, int]):
	snowflakes = []
	cam_left = camera_offset[0]
	cam_right = camera_offset[0] + screen_width
	cam_top = camera_offset[1] - 100
	cam_bottom = camera_offset[1] + screen_height

	for _ in range(density):
		x = random.uniform(cam_left, cam_right)
		y = random.uniform(cam_top, cam_bottom)
		velocity = random.uniform(0.5, 2.0)
		snowflakes.append(Snowflake(x, y, velocity, screen_width))

	return snowflakes


def update_snow(snowflakes: list, camera_offset: tuple[int, int], screen_width: int, screen_height: int):
	cam_left = camera_offset[0]
	cam_right = camera_offset[0] + screen_width
	cam_top = camera_offset[1]
	cam_bottom = camera_offset[1] + screen_height

	for snowflake in snowflakes:
		snowflake.update()

		if snowflake.should_respawn(cam_top, cam_bottom):
			snowflake.respawn(cam_left, cam_right, cam_top)
