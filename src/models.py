from collections import OrderedDict
from typing import Any


class ObjectOrderedSet:
	def __init__(self, *items: Any, draw_name='draw', update_name='update') -> None:
		self._items = OrderedDict.fromkeys(items)
		self._deleted_items = OrderedDict()

		self._draw_name = draw_name
		self._update_name = update_name

	def __repr__(self) -> str:
		items_repr = ", ".join(map(repr, self._items))
		return f'{self.__class__.__name__}({items_repr})'

	def __iter__(self) -> None:
		return iter(self._items)

	def __len__(self) -> int:
		return len(self._items)

	def _delete_items(self) -> None:
		if self._deleted_items:
			for i in self._deleted_items:
				del self._items[i]

			self._deleted_items.clear()

	def add(self, item: Any) -> None:
		self._items[item] = None

	def clear(self) -> None:
		self._items.clear()

	def remove(self, item: Any) -> None:
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
			result = method(*args, **kwargs)
			if callable(method) and (result is False):
				self._deleted_items[obj] = None

		self._delete_items()
