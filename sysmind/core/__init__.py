# sysmind/os/__init__.py
from __future__ import annotations

from sysmind.core.windows import Windows
from sysmind.core.macos import MacOS
from sysmind.core.linux import Linux

__all__ = ['Windows', 'MacOS', 'Linux']

