import pygame

from src.game import Game
from src.player import Player


pygame.init()


def main() -> None:
	player = Player(
		position=(1280 // 2, 720 // 2),
	)
	player_group = pygame.sprite.Group()
	player_group.add(player)

	game = Game(
		player=player,
		player_group=player_group,
		title='Player Demo',
	)

	# button = Button(
	# 	position=(game.size[0] // 2 - 75, 20),
	# 	size=(150, 50),
	# 	text='Red Color',
	# 	command=lambda: player.set_color('#ff0000'),
	# 	background_color='#ff0000',
	# 	text_color='#ffffff',
	# 	border_width=2,
	# 	border_color='#ffffff',
	# 	round_=10,
	# 	font_size=20,
	# )
	# game.ui_group.add(button)

	# info_text = Text(
	# 	position=(game.size[0] // 2 - 150, 90),
	# 	text='Use WASD or Arrow Keys',
	# 	text_color='#ffffff',
	# 	background_color='#2a2a2a',
	# 	font_size=18,
	# 	round_=8,
	# 	border_width=1,
	# 	border_color='#404040',
	# 	padding=10,
	# )
	# game.ui_group.add(info_text)

	game.run()


if __name__ == '__main__':
	main()
