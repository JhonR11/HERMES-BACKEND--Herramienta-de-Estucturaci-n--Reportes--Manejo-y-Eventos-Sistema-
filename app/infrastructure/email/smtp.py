from email.message import EmailMessage
from html import escape

import aiosmtplib

from app.application.interfaces.email import EmailService
from app.infrastructure.config.settings import get_settings


class SmtpEmailService(EmailService):
    async def send_password_reset(self, recipient: str, reset_url: str) -> None:
        await self._send_password_reset_email(recipient, reset_url)

    async def send_password_reset_preview(self, recipient: str, preview_url: str) -> None:
        await self._send_password_reset_email(recipient, preview_url)

    async def _send_password_reset_email(self, recipient: str, reset_url: str) -> None:
        settings = get_settings()
        if not settings.smtp_host:
            raise RuntimeError("SMTP no está configurado")

        message = EmailMessage()
        message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        message["To"] = recipient
        message["Subject"] = "Cambio de contraseña"
        message.set_content(
            "Solicitaste cambiar tu contraseña. Usa este enlace antes de que expire:\n\n"
            f"{reset_url}\n\n"
            "Si no solicitaste este cambio, ignora este correo."
        )
        safe_url = escape(reset_url, quote=True)
        message.add_alternative(
            f"""\
<!doctype html>
<html lang="es">
    <body style="margin:0;background:#f3f6f8;color:#24313a;font-family:Arial,sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:32px 12px;">
            <tr>
                <td align="center">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:#ffffff;border:1px solid #d9e1e5;">
                        <tr>
                            <td style="padding:26px 32px;background:#0d4f5c;color:#ffffff;">
                                <div style="font-size:13px;letter-spacing:1px;text-transform:uppercase;">Institución</div>
                                <h1 style="margin:10px 0 0;font-size:25px;font-weight:600;">Cambio de contraseña</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:32px;">
                                <p style="margin:0 0 16px;font-size:16px;line-height:1.6;">Hola,</p>
                                <p style="margin:0 0 24px;font-size:16px;line-height:1.6;">
                                    Recibimos una solicitud para cambiar la contraseña de tu cuenta institucional.
                                </p>
                                <table role="presentation" cellspacing="0" cellpadding="0" style="margin:0 auto 26px;">
                                    <tr>
                                        <td style="background:#d97706;border-radius:4px;">
                                            <a href="{safe_url}" style="display:inline-block;padding:14px 24px;color:#ffffff;font-size:15px;font-weight:bold;text-decoration:none;">
                                                Cambiar mi contraseña
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                <p style="margin:0 0 12px;font-size:13px;line-height:1.6;color:#52616b;">
                                    Este enlace es válido durante {get_settings().password_reset_token_expire_minutes} minutos y solo puede utilizarse una vez.
                                </p>
                                <p style="margin:0;font-size:13px;line-height:1.6;color:#52616b;">
                                    Si no solicitaste este cambio, puedes ignorar este correo.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:18px 32px;border-top:1px solid #e5eaed;color:#71808a;font-size:12px;">
                                Mensaje automático. Por favor, no respondas a este correo.
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
""",
            subtype="html",
        )
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            start_tls=settings.smtp_start_tls,
        )