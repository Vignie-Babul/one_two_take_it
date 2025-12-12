from collections import OrderedDict
from collections.abc import Iterator
from typing import Generic, TypeVar


T = TypeVar('T')


class ObjectOrderedSet(Generic[T]):
	def __init__(
		self,
		*items: T,
		draw_name: str = 'draw',
		update_name: str = 'update',
	) -> None:

		self._items = OrderedDict.fromkeys(items)
		self._deleted_items = OrderedDict()

		self._draw_name = draw_name
		self._update_name = update_name

	def __repr__(self) -> str:
		items_repr = ", ".join(map(repr, self._items))
		return f'{self.__class__.__name__}({items_repr})'

	def __iter__(self) -> Iterator[T]:
		return iter(self._items.keys())

	def __len__(self) -> int:
		return len(self._items)

	def _delete_items(self) -> None:
		if self._deleted_items:
			for i in self._deleted_items:
				del self._items[i]

			self._deleted_items.clear()

	def add(self, item: T) -> None:
		self._items[item] = None

	def clear(self) -> None:
		self._items.clear()

	def remove(self, item: T) -> None:
		del self._items[item]

	def draw(self, *args, **kwargs) -> None:
		"""calling `draw` method from every stored item in collection"""

		for obj in self._items:
			method = getattr(obj, self._draw_name, None)
			if callable(method):
				method(*args, **kwargs)

	def update(self, *args, **kwargs) -> None:
		"""calling `update` method from every stored item in collection.

		Deletes item from collection, when method returns `False`
		"""

		for obj in self._items:
			method = getattr(obj, self._update_name, None)
			if not callable(method):
				continue

			result = method(*args, **kwargs)
			if result is False:
				self._deleted_items[obj] = None

		self._delete_items()
