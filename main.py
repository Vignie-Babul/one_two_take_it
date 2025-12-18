import pygame

from src.game import Game
from src.menu import MainMenu, PauseMenu
from src.platform import FinishPlatform, Platform
from src.player import Player
from src.shaders import ps1_shader
from src.sound_manager import SoundManager
from src.utils import safe_sprite_load


pygame.init()


pygame.display.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
pygame.display.quit()

textures = {
	'player_left_1': 'assets/graphic/player_left_1.png',
	'player_left_2': 'assets/graphic/player_left_2.png',
	'player_right_1': 'assets/graphic/player_right_1.png',
	'player_right_2': 'assets/graphic/player_right_2.png',
	'courier_bag': 'assets/graphic/courier_bag.png',
}

sounds = {
	'jump': 'assets/sounds/jump.wav',
	'rope_stretch': 'assets/sounds/rope_stretch.wav',
	'explosion': 'assets/sounds/explosion.wav',
	'victory': 'assets/sounds/victory.wav',
}

@ps1_shader(
	resolution_scale=0.003,
	jitter_strength=0.15,
	fog_density=0.2,
	fog_color=(0.35, 0.35, 0.43),
)
class StyledGame(Game):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._pause_menu = None
		self._paused = False


def create_game(sound_manager):
	platform_group = pygame.sprite.Group()

	game = StyledGame(
		player=None,
		platform_group=platform_group,
		title='Раз, два, взяли',
		size=(SCREEN_WIDTH, SCREEN_HEIGHT),
		bg='#1a1a1a',
		fps=60,
		show_fps=False,
		gravity=(0, -50),
		physics_ppm=20,
		use_camera=True,
		sound_manager=sound_manager,
		death_zone_y=-30,
		enable_snow=True,
		snow_density=500,
	)

	platform_group.add(Platform(game.physics_world, (80, 280), (160, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (440, 280), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (600, 280), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (760, 280), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (1080, 280), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (1320, 280), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (1560, 280), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (1800, 440), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (1960, 440), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (2200, 520), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (2440, 680), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (2200, 1080), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (1400, 1160), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (1640, 1160), (80, 80), '#404040'))
	platform_group.add(Platform(game.physics_world, (1960, 1160), (80, 80), '#404040'))
	finish_platform = FinishPlatform(game.physics_world, (760, 1240), (80, 80))
	platform_group.add(finish_platform)
	platform_group.add(Platform(game.physics_world, (1080, 1240), (80, 80), '#404040'))

	start_pos = (80.0, 200.0)
	game.set_finish_platform(finish_platform)

	left_texture_left = safe_sprite_load(textures['player_left_1'])
	left_texture_right = safe_sprite_load(textures['player_left_2'])
	right_texture_left = safe_sprite_load(textures['player_right_2'])
	right_texture_right = safe_sprite_load(textures['player_right_1'])
	bag_texture = safe_sprite_load(textures['courier_bag'])

	player = Player(
		physics_world=game.physics_world,
		position=start_pos,
		size=50,
		speed=10,
		jump_force=85,
		left_texture_left=left_texture_left,
		left_texture_right=left_texture_right,
		right_texture_left=right_texture_left,
		right_texture_right=right_texture_right,
		bag_texture=bag_texture,
		sound_manager=sound_manager,
	)

	game._player = player
	return game


def run_game(sound_manager):
	game = create_game(sound_manager)
	clock = pygame.time.Clock()
	running = True
	result = 'quit'

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				result = 'quit'

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					if game._is_game_over or game._is_victory:
						running = False
						result = 'menu'
					elif not game._paused:
						game._paused = True
						game._pause_menu = PauseMenu(game.size)
					else:
						game._paused = False
						game._pause_menu = None

				elif event.key == pygame.K_m and (game._is_game_over or game._is_victory):
					running = False
					result = 'menu'

				elif not game._paused:
					game._handle_key(event, True)

			elif event.type == pygame.KEYUP:
				if not game._paused:
					game._handle_key(event, False)

			elif event.type == pygame.VIDEORESIZE:
				game._handle_resize(event.w, event.h)
				if game._pause_menu:
					game._pause_menu = PauseMenu(game.size)

			if game._paused and game._pause_menu:
				game._pause_menu.handle_event(event)

		if game._paused and game._pause_menu:
			pause_action = game._pause_menu.get_action()
			if pause_action:
				if pause_action == 'resume':
					game._paused = False
					game._pause_menu = None
				elif pause_action == 'restart':
					running = False
					result = 'restart'
				elif pause_action == 'menu':
					running = False
					result = 'menu'

		if not game._paused:
			game.update()

		game.render()
		clock.tick(game._fps)

	if hasattr(game, '_shader_effect'):
		game._shader_effect.cleanup()

	pygame.display.quit()

	return result


def main() -> None:
	sound_manager = SoundManager()
	for name, path in sounds.items():
		sound_manager.load_sound(name, path)

	state = 'menu'

	while state != 'quit':
		if state == 'menu':
			menu = MainMenu((SCREEN_WIDTH, SCREEN_HEIGHT))
			state = menu.run()
			pygame.display.quit()
		elif state == 'start' or state == 'restart':
			state = run_game(sound_manager)

	pygame.quit()


if __name__ == '__main__':
	main()
