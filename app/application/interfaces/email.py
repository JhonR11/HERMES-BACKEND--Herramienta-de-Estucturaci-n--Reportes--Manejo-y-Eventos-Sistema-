from abc import ABC, abstractmethod


class EmailService(ABC):
    @abstractmethod
    async def send_password_reset(self, recipient: str, reset_url: str) -> None: ...

    @abstractmethod
    async def send_password_reset_preview(self, recipient: str, preview_url: str) -> None: ...