from collections import deque
from .errors import FiberRuntimeError

class FiberStack:
    def __init__(self):
        self._data = []

    def push(self, value):
        self._data.append(value)

    def pop(self):
        if not self._data:
            raise FiberRuntimeError("Stack underflow")
        return self._data.pop()

    def peek(self):
        if not self._data:
            raise FiberRuntimeError("Stack is empty")
        return self._data[-1]

    def isEmpty(self):
        return len(self._data) == 0

    def size(self):
        return len(self._data)


class FiberQueue:
    def __init__(self):
        self._data = deque()

    def enqueue(self, value):
        self._data.append(value)

    def dequeue(self):
        if not self._data:
            raise FiberRuntimeError("Queue underflow")
        return self._data.popleft()

    def isEmpty(self):
        return len(self._data) == 0

    def size(self):
        return len(self._data)


class FiberSet:
    def __init__(self):
        self._data = set()

    def add(self, value):
        self._data.add(value)

    def remove(self, value):
        if value not in self._data:
            raise FiberRuntimeError("Value not in set")
        self._data.remove(value)

    def contains(self, value):
        return value in self._data

    def size(self):
        return len(self._data)
