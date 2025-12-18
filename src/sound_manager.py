import pygame


class SoundManager:
	def __init__(self) -> None:
		pygame.mixer.init()
		self._sounds = {}
		self._music_volume = 0.7
		self._sfx_volume = 0.5

	def load_sound(self, name: str, path: str) -> None:
		try:
			sound = pygame.mixer.Sound(path)
			sound.set_volume(self._sfx_volume)
			self._sounds[name] = sound
		except pygame.error as e:
			print(f"Warning: Could not load sound {path}: {e}")
			self._sounds[name] = None

	def play_sound(self, name: str) -> None:
		if name in self._sounds and self._sounds[name] is not None:
			self._sounds[name].play()

	def set_sfx_volume(self, volume: float) -> None:
		self._sfx_volume = max(0.0, min(1.0, volume))
		for sound in self._sounds.values():
			if sound is not None:
				sound.set_volume(self._sfx_volume)

	def stop_all(self) -> None:
		pygame.mixer.stop()
