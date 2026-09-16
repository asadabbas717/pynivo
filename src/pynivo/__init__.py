"""PyNivo application package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pynivo")
except PackageNotFoundError:
    __version__ = "0+unknown"
