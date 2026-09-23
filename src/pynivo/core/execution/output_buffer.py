"""Bounded semantic output storage for responsive consoles."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OutputChunk:
    text: str
    error: bool = False


class OutputBuffer:
    def __init__(self, maximum_characters: int = 250_000) -> None:
        if maximum_characters <= 0:
            raise ValueError("maximum_characters must be positive")
        self.maximum_characters = maximum_characters
        self._chunks: deque[OutputChunk] = deque()
        self._size = 0
        self.was_truncated = False

    def append(self, text: str, error: bool = False) -> bool:
        if not text:
            return False
        self._chunks.append(OutputChunk(text, error))
        self._size += len(text)
        truncated = False
        while self._size > self.maximum_characters and self._chunks:
            excess = self._size - self.maximum_characters
            first = self._chunks[0]
            if len(first.text) <= excess:
                self._size -= len(first.text)
                self._chunks.popleft()
            else:
                self._chunks[0] = OutputChunk(first.text[excess:], first.error)
                self._size -= excess
            truncated = True
        self.was_truncated = self.was_truncated or truncated
        return truncated

    def chunks(self) -> tuple[OutputChunk, ...]:
        return tuple(self._chunks)

    def clear(self) -> None:
        self._chunks.clear()
        self._size = 0
        self.was_truncated = False
