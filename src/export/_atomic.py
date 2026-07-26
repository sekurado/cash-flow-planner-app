from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from pathlib import Path

from src.domain.exceptions import ExportError


def atomic_write(path: Path, write: Callable[[Path], None]) -> None:
    """Write to a temp file in the same directory, then replace the target atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        fd, temp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        os.close(fd)
        temp_path = Path(temp_name)
        write(temp_path)
        temp_path.replace(path)
    except OSError as exc:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise ExportError(str(exc)) from exc
