import sys
import pygame


pygame.init()


class Game:
	def __init__(
		self,
		title='Window',
		width=1280,
		height=720,
		target_fps=60,
		fps_lock=True,
		fullscreen=False,
		background='#000000',
		show_fps=True,
		fps_color='#FFFFFF',
		fps_position=(10, 10),
		fps_font=None,
		fps_font_size=20
	):
		
		self.title = title
		self.width = width
		self.height = height
		self.target_fps = target_fps
		self.fps_lock = fps_lock
		self.fullscreen = fullscreen
		self.background = background
		self.show_fps = show_fps
		self.fps_color = fps_color
		self.fps_position = fps_position
		self.fps_font = fps_font
		self.fps_font_size = fps_font_size
		
		self.display_info = {'width': width, 'height': height}
		
		if self.fullscreen:
			self.screen = pygame.display.set_mode(
				(self.width, self.height),
				pygame.FULLSCREEN
			)
		else:
			self.screen = pygame.display.set_mode((width, height))
		
		pygame.display.set_caption(title)
		self.clock = pygame.time.Clock()
		self.running = False
		
		self.use_image_background = False
		self.background_image = None
		self.background_color = '#000000'
		
		if isinstance(background, str):
			if background.startswith('#'):
				self.background_color = background
				self.use_image_background = False
			else:
				self._load_background_image(background)
		else:
			self.background_color = background
			self.use_image_background = False
		
		self.fps_counter = None
		if self.show_fps:
			self._create_fps_counter()
		
		self.ui_group = pygame.sprite.Group()

	def _load_background_image(self, image_path):
		try:
			self.background_image = pygame.image.load(image_path).convert()
			self.background_image = pygame.transform.scale(
				self.background_image,
				(self.screen.get_width(), self.screen.get_height())
			)
			self.use_image_background = True
		except (FileNotFoundError, pygame.error) as e:
			print(f'Warning: Could not load background image: {image_path}')
			print(f'Error: {e}')
			self.background_color = '#000000'
			self.use_image_background = False

	def _create_fps_counter(self):
		from .ui import Text
		
		self.fps_counter = Text(
			position=self.fps_position,
			text='FPS: 0',
			text_color=self.fps_color,
			font_size=self.fps_font_size,
			padding=0
		)

	def render_fps_counter(self):
		if not self.show_fps or self.fps_counter is None:
			return
		
		fps = round(self.clock.get_fps())
		
		if self.fps_lock and fps > self.target_fps:
			fps = self.target_fps
		
		self.fps_counter.update_text(f'FPS: {fps}')
		self.screen.blit(self.fps_counter.image, self.fps_counter.rect)

	def handle_events(self):
		events = pygame.event.get()
		
		for event in events:
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.running = False
			
			self.on_event(event)

	def on_event(self, event):
		pass

	def update(self):
		pass

	def render(self):
		if self.use_image_background and self.background_image:
			self.screen.blit(self.background_image, (0, 0))
		else:
			self.screen.fill(self.background_color)
		
		self.ui_group.draw(self.screen)
		self.ui_group.update()
		
		self.render_fps_counter()

	def run(self):
		self.running = True
		while self.running:
			self.handle_events()
			self.update()
			self.render()
			pygame.display.flip()
			self.clock.tick(self.target_fps)
		
		self.quit()

	def quit(self):
		pygame.quit()
		sys.exit()
