from pathlib import Path
from uuid import uuid4

import aiofiles

from app.application.interfaces.storage import StorageService
from app.infrastructure.config.settings import get_settings


class LocalStorageService(StorageService):
    def __init__(self) -> None:
        settings = get_settings()
        self._root = Path(settings.upload_dir)
        self._base_url = settings.resolved_base_url
        self._root.mkdir(parents=True, exist_ok=True)

    async def save(self, *, folder: str, filename: str, content: bytes) -> tuple[str, str]:
        dest_dir = self._root / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        unique_name = f"{uuid4().hex}_{filename}"
        dest = dest_dir / unique_name
        async with aiofiles.open(dest, "wb") as fh:
            await fh.write(content)
        stored = str(dest)
        public_url = f"{self._base_url}/uploads/{folder}/{unique_name}"
        return stored, public_url

    async def delete(self, stored_path: str) -> None:
        path = Path(stored_path)
        if path.exists():
            path.unlink()
