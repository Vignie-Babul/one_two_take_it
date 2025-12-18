import sys

import pygame

from .bag_debris import create_bag_debris
from .camera import Camera
from .confetti import create_confetti
from .models import ObjectOrderedSet
from .platform import FinishPlatform
from .physic import PhysicsWorld
from .snow import create_snow


def render_fps_counter(master, clock, pos=(4, 4)) -> None:
	fps = round(clock.get_fps())
	font = pygame.font.SysFont('', 20)
	surface = font.render(f'FPS: {fps}', True, '#f2f2f2', None)
	master.blit(surface, pos)


class Game:
	def __init__(
		self,
		player,
		platform_group: pygame.sprite.Group,
		title: str = 'PyGame',
		size: tuple[int | float, int | float] = (1280, 720),
		bg: str = '#000000',
		fps: int = 60,
		show_fps: bool = True,
		gravity: tuple[int | float, int | float] = (0, -50),
		physics_ppm: int = 20,
		boundary_color: str = '#ff0000',
		use_camera: bool = True,
		sound_manager = None,
		death_zone_y: int = -1000,
		enable_snow: bool = False,
		snow_density: int = 100,
	) -> None:
		self.size = size
		self._bg = bg
		self._fps = fps
		self._show_fps = show_fps
		self._boundary_color = boundary_color
		self._use_camera = use_camera
		self._player = player
		self._platform_group = platform_group
		self._sound_manager = sound_manager
		self._enable_snow = enable_snow
		self._snow_density = snow_density

		self._screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
		pygame.display.set_caption(title)
		self._clock = pygame.time.Clock()
		self._is_game_loop = False
		self._is_game_over = False
		self._is_victory = False

		self.physics_world = PhysicsWorld(
			gravity=gravity,
			ppm=physics_ppm,
			screen_height=size[1]
		)

		self._debris_particles = None
		self._debris_spawned = False
		self._confetti_particles = None
		self._confetti_spawned = False
		self._victory_sound_played = False
		self._victory_time = 0
		self._last_bag_screen_position = None
		self._death_zone_world_y = death_zone_y
		self._finish_platform = None
		self._snow_particles = None

		if self._use_camera:
			self._camera = Camera(self.size[0], self.size[1])
		else:
			self._camera = None

		if self._enable_snow:
			self._spawn_snow()

	def _spawn_snow(self):
		from .snow import create_snow
		cam_offset = self._camera.get_offset() if self._camera else (0, 0)
		self._snow_particles = create_snow(self._snow_density, self.size[0], self.size[1], cam_offset)

	def set_finish_platform(self, finish_platform: FinishPlatform) -> None:
		self._finish_platform = finish_platform

	def _check_player_death(self) -> bool:
		left_world_y = self._player._left_part.body.position.y
		right_world_y = self._player._right_part.body.position.y
		bag_world_y = self._player._bag.body.position.y

		return (left_world_y < self._death_zone_world_y or
				right_world_y < self._death_zone_world_y or
				bag_world_y < self._death_zone_world_y)

	def _handle_resize(self, new_width: int, new_height: int) -> None:
		self.size = (new_width, new_height)
		self._screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
		self.physics_world.screen_height = new_height

		if self._camera is not None:
			self._camera.update_screen_size(new_width, new_height)

		for sprite in self._platform_group:
			if hasattr(sprite, '_update_sprite_position'):
				sprite._update_sprite_position()

	def handle_events(self) -> None:
		for event in pygame.event.get():
			match event.type:
				case pygame.QUIT:
					self._is_game_loop = False
				case pygame.KEYDOWN:
					self._handle_key(event, True)
				case pygame.KEYUP:
					self._handle_key(event, False)
				case pygame.VIDEORESIZE:
					self._handle_resize(event.w, event.h)

	def _handle_key(self, event: pygame.event.Event, state: bool) -> None:
		match event.key:
			case pygame.K_ESCAPE:
				if state:
					self._is_game_loop = False
			case pygame.K_LEFT | pygame.K_a:
				self._player.move_key('left', state)
			case pygame.K_RIGHT | pygame.K_d:
				self._player.move_key('right', state)
			case pygame.K_SPACE:
				self._player.move_key('jump_left', state)
			case pygame.K_UP:
				self._player.move_key('jump_right', state)
			case pygame.K_r:
				if state and (self._is_game_over or self._is_victory):
					self._player.respawn()
					self._is_game_over = False
					self._is_victory = False
					self._debris_particles = None
					self._debris_spawned = False
					self._confetti_particles = None
					self._confetti_spawned = False
					self._victory_sound_played = False
					if self._finish_platform:
						self._finish_platform.reset()
			case _:
				if hasattr(event, 'unicode'):
					match event.unicode.lower():
						case 'ф':
							self._player.move_key('left', state)
						case 'в':
							self._player.move_key('right', state)
						case 'к':
							if state and (self._is_game_over or self._is_victory):
								self._player.respawn()
								self._is_game_over = False
								self._is_victory = False
								self._debris_particles = None
								self._debris_spawned = False
								self._confetti_particles = None
								self._confetti_spawned = False
								self._victory_sound_played = False
								if self._finish_platform:
									self._finish_platform.reset()

	def update(self) -> None:
		self.physics_world.step(1.0 / self._fps)

		current_time = pygame.time.get_ticks() / 1000.0

		if self._debris_particles is not None:
			self._debris_particles.update()
			if len(self._debris_particles) == 0:
				self._debris_particles = None

		if self._confetti_particles is not None:
			self._confetti_particles.update()
			if len(self._confetti_particles) == 0:
				self._confetti_particles = None

		if (self._snow_particles is not None
			and len(self._snow_particles) < self._snow_density // 2):
				if self._camera is not None:
					cam_pos = self._camera.get_offset()
				else:
					cam_pos = (0, 0)
				new_snow = create_snow(cam_pos, self.size, self._snow_density // 10)
				for snowflake in new_snow:
					self._snow_particles.add(snowflake)

		if (not self._is_victory and self._finish_platform and not self._player.is_game_over()
			and self._finish_platform.check_player_on_platform(self._player)):
			self._is_victory = True
			self._victory_time = current_time
			self._player.set_finished()
			if self._sound_manager and not self._victory_sound_played:
				self._sound_manager.play_sound('victory')
				self._victory_sound_played = True

		if not self._is_victory and self._player.is_game_over():
			self._is_game_over = True

		if not self._is_game_over and not self._is_victory and self._check_player_death():
			self._player.force_tear()

		if self._player.should_spawn_debris() and not self._debris_spawned:
			bag_pos = self._player.get_bag_screen_position()
			bag_size = self._player.get_bag_size()
			left_vel, right_vel = self._player.get_parts_velocities()
			debris_list = create_bag_debris(bag_pos, bag_size, self.size, left_vel, right_vel)
			self._debris_particles = ObjectOrderedSet(*debris_list)
			self._debris_spawned = True

		if (self._is_victory and not self._confetti_spawned
			and current_time - self._victory_time >= 1.6):
			bag_pos = self._player.get_bag_screen_position()
			confetti_list = create_confetti(bag_pos, self.size)
			self._confetti_particles = ObjectOrderedSet(*confetti_list)
			self._confetti_spawned = True

		self._player.update(current_time)
		self._platform_group.update()

		if self._camera is not None:
			bag_screen_pos = self._player.get_bag_screen_position()

			if not self._player.is_game_over():
				self._last_bag_screen_position = bag_screen_pos

			target_pos = bag_screen_pos if not self._player.is_game_over() else self._last_bag_screen_position

			if target_pos is not None:
				self._camera.update(target_pos[0], target_pos[1])

	def render(self) -> None:
		self._screen.fill(self._bg)

		if self._snow_particles is not None:
			cam_offset = self._camera.get_offset() if self._camera is not None else (0, 0)
			for snowflake in self._snow_particles:
				snow_x = int(snowflake.x - cam_offset[0])
				snow_y = int(snowflake.y - cam_offset[1])
				if 0 <= snow_x < self.size[0] and 0 <= snow_y < self.size[1]:
					self._screen.set_at((snow_x, snow_y), '#ffffff')

		for platform in self._platform_group:
			if self._camera is not None:
				self._screen.blit(platform.image, self._camera.apply(platform.rect))
			else:
				self._screen.blit(platform.image, platform.rect)

		if self._camera is not None:
			left_rect = self._camera.apply(self._player._left_part.rect)
			right_rect = self._camera.apply(self._player._right_part.rect)
			bag_rect = self._camera.apply(self._player._bag.rect)
			self._screen.blit(self._player._left_part.image, left_rect)
			self._screen.blit(self._player._bag.image, bag_rect)
			self._screen.blit(self._player._right_part.image, right_rect)
		else:
			self._screen.blit(self._player._left_part.image, self._player._left_part.rect)
			self._screen.blit(self._player._bag.image, self._player._bag.rect)
			self._screen.blit(self._player._right_part.image, self._player._right_part.rect)

		if self._debris_particles is not None:
			debris_sorted = sorted(self._debris_particles, key=lambda obj: obj.depth)
			for debris in debris_sorted:
				if self._camera is not None:
					debris_rect = pygame.Rect(
						int(debris._x - debris._width / 2),
						int(debris._y - debris._height / 2),
						debris._width,
						debris._height
					)
					adjusted_rect = self._camera.apply(debris_rect)
					self._screen.blit(debris._surface, adjusted_rect.topleft)
				else:
					self._screen.blit(
						debris._surface,
						(
							int(debris._x - debris._width / 2),
							int(debris._y - debris._height / 2)
						)
					)

		if self._confetti_particles is not None:
			confetti_sorted = sorted(self._confetti_particles, key=lambda obj: obj.depth)
			for confetto in confetti_sorted:
				if self._camera is not None:
					confetto_rect = pygame.Rect(
						int(confetto._x - confetto._width / 2),
						int(confetto._y - confetto._height / 2),
						confetto._width,
						confetto._height
					)
					adjusted_rect = self._camera.apply(confetto_rect)
					self._screen.blit(confetto._surface, adjusted_rect.topleft)
				else:
					self._screen.blit(
						confetto._surface,
						(
							int(confetto._x - confetto._width / 2),
							int(confetto._y - confetto._height / 2)
						)
					)

		if self._is_game_over:
			font = pygame.font.SysFont('', 48)
			text = font.render('GAME OVER - Press R to restart', True, '#ff0000')
			text_rect = text.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
			self._screen.blit(text, text_rect)

		if self._is_victory:
			font = pygame.font.SysFont('', 48)
			text = font.render('VICTORY! - Press R to restart', True, '#00ff00')
			text_rect = text.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
			self._screen.blit(text, text_rect)

		if self._show_fps:
			render_fps_counter(self._screen, self._clock)

		pygame.display.flip()

	def quit(self) -> None:
		pygame.quit()
		sys.exit()

	def run(self) -> None:
		self._is_game_loop = True
		while self._is_game_loop:
			self.render()
			self.update()
			self.handle_events()
			self._clock.tick(self._fps)
		self.quit()
