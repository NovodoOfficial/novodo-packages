from typing import Any, Dict, Iterator, Optional, TypeVar, Union, overload

T = TypeVar("T", bound="DotDict")

class DotDict:
    """
    A dictionary that supports attribute-style access and key access,
    recursively converting nested dictionaries.
    """

    def __init__(self, d: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[str, Any] = {}
        if d:
            for k, v in d.items():
                if isinstance(v, dict):
                    v = DotDict(v)
                self._data[k] = v

    def __getattr__(self: T, key: str) -> Any:
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(f"\"DotDict\" object has no attribute \"{key}\"")

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "_data":
            super().__setattr__(key, value)
        else:
            if isinstance(value, dict):
                value = DotDict(value)
            self._data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if isinstance(value, dict):
            value = DotDict(value)
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __delattr__(self, key: str) -> None:
        try:
            del self._data[key]
        except KeyError:
            raise AttributeError(f"\"DotDict\" object has no attribute \"{key}\"")

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data})"
