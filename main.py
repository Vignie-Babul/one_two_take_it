import pygame

from src.game import Game
from src.ui import Button, Text
from src.player import Player


pygame.init()


keys_pressed = {
	'right': False,
	'left': False,
	'up': False,
	'down': False,
}


def change_color(player: Player) -> None:
	player.set_color('#ff0000')


def handle_custom_events(event) -> None:
	if event.type == pygame.KEYDOWN:
		match event.key:
			case pygame.K_LEFT | pygame.K_a:
				keys_pressed['left'] = True
			case pygame.K_RIGHT | pygame.K_d:
				keys_pressed['right'] = True
			case pygame.K_UP | pygame.K_w:
				keys_pressed['up'] = True
			case pygame.K_DOWN | pygame.K_s:
				keys_pressed['down'] = True

	if event.type == pygame.KEYUP:
		match event.key:
			case pygame.K_LEFT | pygame.K_a:
				keys_pressed['left'] = False
			case pygame.K_RIGHT | pygame.K_d:
				keys_pressed['right'] = False
			case pygame.K_UP | pygame.K_w:
				keys_pressed['up'] = False
			case pygame.K_DOWN | pygame.K_s:
				keys_pressed['down'] = False

def update_game(game: Game, player: Player, player_group: pygame.sprite.Group) -> None:
	player.stop_horizontal()
	player.stop_vertical()

	if keys_pressed['left']:
		player.move('left')
	if keys_pressed['right']:
		player.move('right')
	if keys_pressed['up']:
		player.move('up')
	if keys_pressed['down']:
		player.move('down')

	player_group.update(game.width, game.height)

def render_game(game: Game, player_group: pygame.sprite.Group) -> None:
	if game.use_image_background and game.background_image:
		game.screen.blit(game.background_image, (0, 0))
	else:
		game.screen.fill(game.background_color)

	player_group.draw(game.screen)

	game.ui_group.draw(game.screen)
	game.ui_group.update()

	game.render_fps_counter()


def main() -> None:
	game = Game(title='Player Demo')
	game.on_event = handle_custom_events

	player_group = pygame.sprite.Group()
	player = Player(
		position=(game.width // 2, game.height // 2),
		size=50,
		color='#00ff00',
		speed=5,
	)
	player_group.add(player)

	game.update = lambda: update_game(game, player, player_group)
	game.render = lambda: render_game(game, player_group)

	button = Button(
		position=(game.width // 2 - 75, 20),
		size=(150, 50),
		text='Red Color',
		command=lambda: change_color(player),
		background_color='#ff0000',
		text_color='#ffffff',
		border_width=2,
		border_color='#ffffff',
		round_=10,
		font_size=20,
	)
	game.ui_group.add(button)

	info_text = Text(
		position=(game.width // 2 - 150, 90),
		text='Use WASD or Arrow Keys',
		text_color='#ffffff',
		background_color='#2a2a2a',
		font_size=18,
		round_=8,
		border_width=1,
		border_color='#404040',
		padding=10,
	)
	game.ui_group.add(info_text)

	game.run()


if __name__ == '__main__':
	main()
