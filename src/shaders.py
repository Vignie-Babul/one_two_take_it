from array import array
from collections.abc import Callable

import pygame
import moderngl


class PS1ShaderEffect:
	def __init__(
		self,
		screen_size: tuple[int, int],
		resolution_scale: float = 0.5,
		jitter_strength: float = 1.0,
		fog_density: float = 0.3,
		fog_color: tuple[float, float, float] = (0.35, 0.35, 0.43),
	) -> None:
		self.screen_size = screen_size
		self.resolution_scale = resolution_scale
		self.jitter_strength = jitter_strength
		self.fog_density = fog_density
		self.fog_color = fog_color

		self.ctx = moderngl.create_context()

		self.quad_buffer = self.ctx.buffer(data=array('f', [
			-1.0, 1.0, 0.0, 0.0,
			1.0, 1.0, 1.0, 0.0,
			-1.0, -1.0, 0.0, 1.0,
			1.0, -1.0, 1.0, 1.0,
		]))

		self.vert_shader = '''
		#version 330 core

		in vec2 vert;
		in vec2 text_cord;
		out vec2 uvs;

		void main() {
			uvs = text_cord;
			gl_Position = vec4(vert, 0.0, 1.0);
		}
		'''

		self.frag_shader = '''
		#version 330 core

		uniform sampler2D text;
		uniform float time;
		uniform float jitter_strength;
		uniform float fog_density;
		uniform vec3 fog_color;
		uniform float pixel_scale;

		in vec2 uvs;
		out vec4 f_color;

		float random(vec2 co) {
			return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
		}

		void main() {
			vec2 uv = uvs;

			float jitter_x = (random(vec2(time * 0.1, 0.0)) - 0.5) * jitter_strength * 0.003;
			float jitter_y = (random(vec2(0.0, time * 0.1)) - 0.5) * jitter_strength * 0.003;
			uv += vec2(jitter_x, jitter_y);

			vec2 pixel_uv = floor(uv / pixel_scale) * pixel_scale;

			vec4 color = texture(text, pixel_uv);

			color.rgb = mix(color.rgb, fog_color, fog_density);

			color.rgb = floor(color.rgb * 32.0) / 32.0;

			f_color = color;
		}
		'''

		self.program = self.ctx.program(
			vertex_shader=self.vert_shader,
			fragment_shader=self.frag_shader
		)

		self.render_object = self.ctx.vertex_array(
			self.program,
			[(self.quad_buffer, '2f 2f', 'vert', 'text_cord')]
		)

		self.frame_count = 0

	def surf_to_texture(self, surf: pygame.Surface) -> moderngl.Texture:
		text = self.ctx.texture(surf.get_size(), 4)
		text.filter = (moderngl.NEAREST, moderngl.NEAREST)
		text.swizzle = 'BGRA'
		text.write(surf.get_view('1'))
		return text

	def process_frame(self, surface: pygame.Surface) -> None:
		self.frame_count += 1

		frame_text = self.surf_to_texture(surface)
		frame_text.use(0)

		self.program['text'] = 0
		self.program['time'] = self.frame_count
		self.program['jitter_strength'] = self.jitter_strength
		self.program['fog_density'] = self.fog_density
		self.program['fog_color'] = self.fog_color
		self.program['pixel_scale'] = self.resolution_scale

		self.render_object.render(mode=moderngl.TRIANGLE_STRIP)

		frame_text.release()

	def get_screen_size(self) -> tuple[int, int]:
		return (self.ctx.screen.width, self.ctx.screen.height)

	def cleanup(self):
		self.quad_buffer.release()
		self.render_object.release()
		self.program.release()
		self.ctx.release()


def ps1_shader(
	resolution_scale: float = 0.003,
	jitter_strength: float = 0.3,
	fog_density: float = 0.2,
	fog_color: tuple[float, float, float] = (0.35, 0.35, 0.43),
) -> Callable:
	def decorator(cls):
		original_init = cls.__init__
		original_quit = cls.quit

		def new_init(self, *args, **kwargs):
			original_init(self, *args, **kwargs)

			pygame.display.quit()
			pygame.display.init()

			info = pygame.display.Info()
			self.size = (info.current_w, info.current_h)

			flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN

			self._screen = pygame.display.set_mode(
				self.size, 
				flags,
				vsync=1
			)
			pygame.display.set_caption(kwargs.get('title', 'PyGame'))

			self._display = pygame.Surface(self.size)

			self._shader_effect = PS1ShaderEffect(
				screen_size=self.size,
				resolution_scale=resolution_scale,
				jitter_strength=jitter_strength,
				fog_density=fog_density,
				fog_color=fog_color,
			)
			self._shader_enabled = True

			if kwargs.get('enable_snow', False) and kwargs.get('snow_density'):
				from .snow import create_snow
				cam_offset = self._camera.get_offset() if self._camera else (0, 0)
				self._snow_particles = create_snow(kwargs['snow_density'], self.size[0], self.size[1], cam_offset)

			if self._camera is not None:
				self._camera.update_screen_size(self.size[0], self.size[1])

		def new_handle_resize(self, new_width: int, new_height: int) -> None:
			self.size = (new_width, new_height)

			flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN

			self._screen = pygame.display.set_mode(
				self.size,
				flags,
				vsync=1
			)
			self._display = pygame.Surface(self.size)
			self.physics_world.screen_height = new_height

			if self._camera is not None:
				self._camera.update_screen_size(new_width, new_height)

			for sprite in self._platform_group:
				if hasattr(sprite, '_update_sprite_position'):
					sprite._update_sprite_position()

		def new_render(self):
			actual_size = self._shader_effect.get_screen_size()

			if self._display.get_size() != actual_size:
				self._display = pygame.Surface(actual_size)

			self._display.fill(self._bg)

			for platform in self._platform_group:
				if self._camera is not None:
					self._display.blit(platform.image, self._camera.apply(platform.rect))
				else:
					self._display.blit(platform.image, platform.rect)

			if self._camera is not None:
				left_rect = self._camera.apply(self._player._left_part.rect)
				right_rect = self._camera.apply(self._player._right_part.rect)
				bag_rect = self._camera.apply(self._player._bag.rect)
				self._display.blit(self._player._left_part.image, left_rect)
				self._display.blit(self._player._bag.image, bag_rect)
				self._display.blit(self._player._right_part.image, right_rect)
			else:
				self._display.blit(self._player._left_part.image, self._player._left_part.rect)
				self._display.blit(self._player._bag.image, self._player._bag.rect)
				self._display.blit(self._player._right_part.image, self._player._right_part.rect)

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
						self._display.blit(debris._surface, adjusted_rect.topleft)
					else:
						self._display.blit(
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
						self._display.blit(confetto._surface, adjusted_rect.topleft)
					else:
						self._display.blit(
							confetto._surface,
							(
								int(confetto._x - confetto._width / 2),
								int(confetto._y - confetto._height / 2)
							)
						)

			use_shader = self._shader_enabled and not (hasattr(self, '_paused') and self._paused)

			if use_shader:
				self._shader_effect.process_frame(self._display)
				self._shader_effect.ctx.finish()

				buffer_data = self._shader_effect.ctx.screen.read(components=4)
				result_surface = pygame.image.fromstring(buffer_data, actual_size, 'RGBA', True)

				temp_screen = pygame.Surface(actual_size)
				temp_screen.blit(result_surface, (0, 0))
			else:
				temp_screen = self._display.copy()

			if self._snow_particles is not None:
				from .snow import update_snow
				cam_offset = self._camera.get_offset() if self._camera is not None else (0, 0)
				update_snow(self._snow_particles, cam_offset, actual_size[0], actual_size[1])

				for snowflake in self._snow_particles:
					snow_x = int(snowflake.x - cam_offset[0])
					snow_y = int(snowflake.y - cam_offset[1])
					if 0 <= snow_x < actual_size[0] and 0 <= snow_y < actual_size[1]:
						temp_screen.set_at((snow_x, snow_y), '#ffffff')

				cam_offset = self._camera.get_offset() if self._camera is not None else (0, 0)
				for snowflake in self._snow_particles:
					snow_x = int(snowflake.x - cam_offset[0])
					snow_y = int(snowflake.y - cam_offset[1])
					if 0 <= snow_x < actual_size[0] and 0 <= snow_y < actual_size[1]:
						temp_screen.set_at((snow_x, snow_y), '#ffffff')

			if hasattr(self, '_paused') and self._paused and hasattr(self, '_pause_menu') and self._pause_menu:
				self._pause_menu.draw(temp_screen)

			if self._is_game_over:
				font = pygame.font.SysFont('', 56)
				text = font.render('ПРОИГРЫШ - Нажми R или ESC/M для меню', True, '#ff0000')
				text_rect = text.get_rect(center=(actual_size[0] // 2, actual_size[1] // 2))
				temp_screen.blit(text, text_rect)

			if self._is_victory:
				font = pygame.font.SysFont('', 56)
				text = font.render('ПОБЕДА! - Нажми R или ESC/M для меню', True, '#00ff00')
				text_rect = text.get_rect(center=(actual_size[0] // 2, actual_size[1] // 2))
				temp_screen.blit(text, text_rect)

			if self._show_fps:
				from .game import render_fps_counter
				render_fps_counter(temp_screen, self._clock)

			final_text = self._shader_effect.surf_to_texture(temp_screen)
			final_text.use(0)
			self._shader_effect.program['text'] = 0
			self._shader_effect.program['time'] = 0
			self._shader_effect.program['jitter_strength'] = 0.0
			self._shader_effect.program['pixel_scale'] = 0.001
			self._shader_effect.render_object.render(mode=moderngl.TRIANGLE_STRIP)
			final_text.release()

			pygame.display.flip()

		def new_quit(self):
			self._shader_effect.cleanup()
			original_quit(self)

		cls.__init__ = new_init
		cls.render = new_render
		cls.quit = new_quit
		cls._handle_resize = new_handle_resize

		return cls

	return decorator
