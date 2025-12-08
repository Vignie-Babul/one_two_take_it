import pygame

from src.game import Game
from src.player import Player
from src.platform import Platform

pygame.init()


def main() -> None:
	player_group = pygame.sprite.Group()
	platform_group = pygame.sprite.Group()

	game = Game(
		player=None,
		player_group=player_group,
		platform_group=platform_group,
		title='Physics Demo',
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
		position=(514, 250),
		size=(200, 30),
		color='#404040'
	)
	platform_group.add(platform1)

	platform2 = Platform(
		physics_world=game.physics_world,
		position=(640, 400),
		size=(600, 30),
		color='#404040'
	)
	platform_group.add(platform2)

	player = Player(
		physics_world=game.physics_world,
		position=(640, 0),
		size=50,
		color='#00ff00',
		speed=10,
		jump_force=150,
	)
	player_group.add(player)
	game._player = player

	game.run()


if __name__ == '__main__':
	main()
