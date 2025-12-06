import pygame


pygame.init()


class Player(pygame.sprite.Sprite):
	def __init__(
		self,
		position,
		size=50,
		color='#00ff00',
		speed=5
	) -> None:

		super().__init__()
		
		self.size = size
		self.color = color
		self.speed = speed

		self.velocity = pygame.math.Vector2(0, 0)
		
		self.image = pygame.Surface((size, size))
		self.image.fill(color)
		
		self.rect = self.image.get_rect(center=position)
		
	
	def move(self, direction) -> None:
		if direction == 'left':
			self.velocity.x = -self.speed
		elif direction == 'right':
			self.velocity.x = self.speed
		elif direction == 'up':
			self.velocity.y = -self.speed
		elif direction == 'down':
			self.velocity.y = self.speed
	
	def stop_horizontal(self) -> None:
		self.velocity.x = 0
	
	def stop_vertical(self) -> None:
		self.velocity.y = 0
	
	def update(self, screen_width, screen_height) -> None:
		self.rect.x += self.velocity.x
		self.rect.y += self.velocity.y
		
		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.right > screen_width:
			self.rect.right = screen_width
		if self.rect.top < 0:
			self.rect.top = 0
		if self.rect.bottom > screen_height:
			self.rect.bottom = screen_height
	
	def set_color(self, color) -> None:
		self.color = color
		self.image.fill(color)
