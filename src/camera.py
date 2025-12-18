class Camera:
	def __init__(self, screen_width: int, screen_height: int) -> None:
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.x = 0
		self.y = 0

	def update(self, target_x: float, target_y: float) -> None:
		self.x = int(target_x - self.screen_width // 2)
		self.y = int(target_y - self.screen_height // 2)

	def apply(self, rect) -> None:
		return rect.move(-self.x, -self.y)

	def get_offset(self) -> tuple[int, int]:
		return (self.x, self.y)

	def update_screen_size(self, screen_width: int, screen_height: int) -> None:
		self.screen_width = screen_width
		self.screen_height = screen_height
