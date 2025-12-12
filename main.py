import pygame

from src.game import Game
from src.player import Player
from src.platform import Platform
from src.utils import save_sprite_load


pygame.init()


textures = {
	'player_left': 'assets/graphic/player_left.png',
	'player_right': 'assets/graphic/player_right.png',
	'courier_bag': 'assets/graphic/courier_bag.png',
}


def main() -> None:
	platform_group = pygame.sprite.Group()

	game = Game(
		player=None,
		platform_group=platform_group,
		title='Courier Chaos',
		size=(1280, 720),
		bg='#1a1a1a',
		fps=60,
		show_fps=True,
		gravity=(0, -50),
		physics_ppm=20,
		enable_boundaries=True,
		boundary_color='#ff0000',
	)

	platform1 = Platform(
		physics_world=game.physics_world,
		position=(300, 250),
		size=(200, 30),
		color='#404040',
	)
	platform_group.add(platform1)

	platform2 = Platform(
		physics_world=game.physics_world,
		position=(640, 400),
		size=(600, 30),
		color='#404040',
	)
	platform_group.add(platform2)

	left_texture = save_sprite_load(textures['player_left'])
	right_texture = save_sprite_load(textures['player_right'])
	bag_texture = save_sprite_load(textures['courier_bag'])

	player = Player(
		physics_world=game.physics_world,
		position=(640, 0),
		size=50,
		speed=10,
		jump_force=150,
		left_texture=left_texture,
		right_texture=right_texture,
		bag_texture=bag_texture,
	)
	game._player = player

	game.run()


if __name__ == '__main__':
	main()
